from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, Controller
from pydantic import BaseModel, SecretStr
from typing import List
import datetime
import sqlite3
import json
import asyncio
import os
from dotenv import load_dotenv
import traceback
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

load_dotenv()

app = Flask(__name__, static_folder='static')
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Enable CORS for API routes

# Database setup
def init_db():
    conn = sqlite3.connect('chrome_hearts.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT NOT NULL,
        price REAL,
        size TEXT,
        availability BOOLEAN,
        image_url TEXT,
        item_url TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Pydantic model for items
class Item(BaseModel):
    item_name: str
    price: float
    size: str
    availability: bool
    image_url: str
    item_url: str
    
class Items(BaseModel):
    items: List[Item]

# Scraping function
async def scrape_data():
    api_key = os.getenv('GOOGLE_API_KEY', "AIzaSyDMPcsvZmoMo88v8i9oG2S6iNkJPXYGAEs")
    if not api_key:
        app.logger.error("Missing GOOGLE_API_KEY in environment variables")
        raise ValueError("Missing Google API key. Please check your .env file.")
        
    llm = ChatGoogleGenerativeAI(model='gemini-1.5-flash', api_key=SecretStr(api_key))
    
    # Log that we're starting the scraping process
    app.logger.info("Starting scraping process with Gemini model")
    
    links = [ 
        "https://ypcollective.com/collections/chrome-hearts",
        "https://topdrwr.io/brand/chrome-hearts", 
        "https://www.grailed.com/designers/chrome-hearts"
    ]
    
    task_description = f"""
    Visit all links provided in {links} to give me Chrome Hearts item listing data from each link. There are {len(links)} links to visit. Make sure to visit all the links. Return a single json.

    Guidelines:
    1. Still collect items that are sold out or unavailable, and if not specified if available or not, then assume it is available.
    2. Do not visit any other websites.
    3. If any specific info is not available then return 'N/A'.
    4. For the url and image url can you make sure the full url is recorded.
    5. For item url, if you cannot find the url for the specific item, then return the URL for the website.
    """
    
    controller = Controller(output_model=Items)
    
    agent = Agent(
        task=task_description,
        llm=llm,
        controller=controller
    )
    
    history = await agent.run()
    result = history.final_result()
    
    # Improved result handling - log what we received to help debugging
    app.logger.info(f"Received result of type: {type(result)}")
    
    # Handle nested structures better
    if isinstance(result, dict):
        # First check if it's a dictionary with "items" key directly
        if "items" in result and isinstance(result["items"], list):
            app.logger.info(f"Found 'items' key with {len(result['items'])} items")
            return result["items"]
            
        # Otherwise, look for any list values in the dictionary
        for key, value in result.items():
            if isinstance(value, list) and len(value) > 0:
                app.logger.info(f"Found list in key '{key}' with {len(value)} items")
                return value
                
        app.logger.warning("No usable lists found in result dictionary")
        return []
        
    return result

# Update process_scrape_result to better handle different data structures
def process_scrape_result(result, cursor):
    """Process scraping results and add to database, returns count of items added"""
    items_added = 0
    
    # Clear existing data
    cursor.execute("DELETE FROM items")
    
    if not result:
        app.logger.warning("Empty result received from scraping")
        return 0
        
    # Handle dictionary with "items" key
    if isinstance(result, dict):
        if "items" in result and isinstance(result["items"], list):
            items = result["items"]
        else:
            # Find the first list value in the dictionary
            items = None
            for key, value in result.items():
                if isinstance(value, list) and all(isinstance(item, dict) for item in value):
                    items = value
                    break
                    
        if not items:
            app.logger.warning("No valid item list found in dictionary result")
            return 0
            
        for item in items:
            try:
                # Use more robust value extraction with error checking
                item_name = str(item.get('item_name', 'Unknown'))
                
                # Handle price conversion more carefully
                price_value = item.get('price', 0)
                try:
                    price = float(price_value) if price_value not in ('N/A', None) else 0.0
                except (ValueError, TypeError):
                    app.logger.warning(f"Invalid price value '{price_value}' for item '{item_name}', using 0")
                    price = 0.0
                
                cursor.execute(
                    "INSERT INTO items (item_name, price, size, availability, image_url, item_url) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        item_name,
                        price,
                        str(item.get('size', 'N/A')),
                        bool(item.get('availability', True)),
                        str(item.get('image_url', 'N/A')),
                        str(item.get('item_url', 'N/A'))
                    )
                )
                items_added += 1
            except Exception as e:
                app.logger.error(f"Error processing item: {str(e)}")
                app.logger.error(f"Problematic item: {item}")
                
    # Handle list of items directly
    elif isinstance(result, list):
        for item in result:
            if not isinstance(item, dict):
                app.logger.warning(f"Skipping non-dictionary item: {item}")
                continue
                
            try:
                item_name = str(item.get('item_name', 'Unknown'))
                
                # Handle price conversion more carefully
                price_value = item.get('price', 0)
                try:
                    price = float(price_value) if price_value not in ('N/A', None) else 0.0
                except (ValueError, TypeError):
                    app.logger.warning(f"Invalid price value '{price_value}' for item '{item_name}', using 0")
                    price = 0.0
                    
                cursor.execute(
                    "INSERT INTO items (item_name, price, size, availability, image_url, item_url) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        item_name,
                        price,
                        str(item.get('size', 'N/A')),
                        bool(item.get('availability', True)),
                        str(item.get('image_url', 'N/A')),
                        str(item.get('item_url', 'N/A'))
                    )
                )
                items_added += 1
            except Exception as e:
                app.logger.error(f"Error processing item: {str(e)}")
                app.logger.error(f"Problematic item: {item}")
                
    return items_added

# API routes
@app.route('/api/items', methods=['GET'])
def get_items():
    search_query = request.args.get('q', '')
    
    try:
        conn = sqlite3.connect('chrome_hearts.db')
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        
        if search_query:
            # Add search functionality
            cursor.execute(
                "SELECT * FROM items WHERE item_name LIKE ? ORDER BY timestamp DESC", 
                (f'%{search_query}%',)
            )
        else:
            cursor.execute("SELECT * FROM items ORDER BY timestamp DESC")
        
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify(items)
    except Exception as e:
        app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    try:
        app.logger.info("Starting data refresh operation")
        
        # Check API key before attempting scrape
        if not os.getenv('GOOGLE_API_KEY'):
            app.logger.error("Missing GOOGLE_API_KEY in environment variables")
            return jsonify({"status": "error", "message": "Missing Google API key. Please check your .env file."}), 400
        
        # Use a timeout for the scraping operation
        try:
            result = asyncio.run(asyncio.wait_for(scrape_data(), timeout=180))  # 3 minute timeout
        except asyncio.TimeoutError:
            app.logger.error("Scraping operation timed out after 3 minutes")
            return jsonify({"status": "error", "message": "Scraping operation timed out. Try again or use a smaller sample."}), 504
        
        app.logger.info(f"Scraping completed, processing results")
        
        # Log the result structure for debugging
        if isinstance(result, dict):
            app.logger.info(f"Result is a dictionary with keys: {list(result.keys())}")
        elif isinstance(result, list):
            app.logger.info(f"Result is a list with {len(result)} items")
        else:
            app.logger.info(f"Result is of type: {type(result)}")
        
        # Process the result and store in database
        conn = sqlite3.connect('chrome_hearts.db')
        cursor = conn.cursor()
        
        # Use the new processing function
        items_added = process_scrape_result(result, cursor)
        
        conn.commit()
        conn.close()
        
        app.logger.info("Data refresh completed successfully")
        return jsonify({"status": "success", "message": f"Data refreshed successfully. Added {items_added} items."})
    except Exception as e:
        error_details = traceback.format_exc()
        app.logger.error(f"Refresh error: {str(e)}\n{error_details}")
        return jsonify({
            "status": "error", 
            "message": str(e),
            "details": error_details if app.debug else "Enable debug mode for more details."
        }), 500

# Add an error route to help with debugging
@app.route('/api/debug', methods=['GET'])
def debug_info():
    try:
        # Check if the database exists
        db_exists = os.path.exists('chrome_hearts.db')
        
        # Count items if database exists
        item_count = 0
        if db_exists:
            conn = sqlite3.connect('chrome_hearts.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM items")
            item_count = cursor.fetchone()[0]
            conn.close()
        
        return jsonify({
            "status": "ok",
            "database_exists": db_exists,
            "item_count": item_count,
            "api_version": "1.0",
            "server_time": str(datetime.datetime.now())
        })
    except Exception as e:
        app.logger.error(f"Debug error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Add seed data if needed
@app.route('/api/seed', methods=['POST'])
def seed_data():
    try:
        conn = sqlite3.connect('chrome_hearts.db')
        cursor = conn.cursor()
        
        # Add some sample data
        sample_items = [
            {
                "item_name": "Chrome Hearts Rolling Stones Leather Bracelet",
                "price": 999.00,
                "size": "os",
                "availability": True,
                "image_url": "N/A",
                "item_url": "https://ypcollective.com/collections/chrome-hearts"
            },
            {
                "item_name": "Chrome Hearts Space Matty Boy Hat",
                "price": 1200.00,
                "size": "os",
                "availability": True,
                "image_url": "N/A",
                "item_url": "https://ypcollective.com/collections/chrome-hearts"
            }
        ]
        
        for item in sample_items:
            cursor.execute(
                "INSERT INTO items (item_name, price, size, availability, image_url, item_url) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    item["item_name"],
                    item["price"],
                    item["size"],
                    item["availability"],
                    item["image_url"],
                    item["item_url"]
                )
            )
        
        conn.commit()
        conn.close()
        
        return jsonify({"status": "success", "message": f"Seeded database with {len(sample_items)} items"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Add a test route to verify scraping functionality
@app.route('/api/test_scrape', methods=['GET'])
def test_scrape():
    try:
        app.logger.info("Testing scraping functionality without database updates")
        
        try:
            # Run a shorter timeout for testing
            result = asyncio.run(asyncio.wait_for(scrape_data(), timeout=60))
            
            # Return basic info about result without modifying database
            if isinstance(result, dict):
                keys = list(result.keys())
                sample = "Sample found" if keys else "No data in result dictionary"
                return jsonify({
                    "status": "success", 
                    "result_type": "dictionary",
                    "keys": keys,
                    "sample": sample
                })
            elif isinstance(result, list):
                sample = result[0] if result else "Empty list"
                return jsonify({
                    "status": "success", 
                    "result_type": "list",
                    "length": len(result),
                    "sample": sample
                })
            else:
                return jsonify({
                    "status": "warning",
                    "result_type": str(type(result)),
                    "message": "Unexpected result type"
                })
        except asyncio.TimeoutError:
            return jsonify({"status": "error", "message": "Scraping operation timed out"}), 504
        except Exception as e:
            return jsonify({"status": "error", "message": str(e), "traceback": traceback.format_exc()}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Serve static files
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

# Add a fallback route to handle 404s
@app.errorhandler(404)
def not_found(e):
    return jsonify({"status": "error", "message": "Route not found"}), 404

# Add a fallback route to handle 500s
@app.errorhandler(500)
def server_error(e):
    return jsonify({"status": "error", "message": "Internal server error"}), 500

# Check if a port is in use
def is_port_in_use(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

if __name__ == '__main__':
    # Make sure the database is initialized
    init_db()
    
    port = 5000  # We'll insist on port 5000
    
    # Check if the default port is already in use
    if is_port_in_use(port):
        print(f"WARNING: Port {port} is already in use.")
        print("This application needs to run on port 5000.")
        print("\nTry these steps to free up port 5000:")
        print("1. Check for other Python/Flask applications that might be running")
        print("2. On macOS/Linux, use: lsof -i :5000 to see what's using the port")
        print("3. On Windows, use: netstat -ano | findstr :5000")
        print("4. Kill the process using the port or wait for it to finish")
        print("\nWould you like to:")
        print("1. Try to start anyway (might fail)")
        print("2. Exit the program")
        
        try:
            choice = input("Enter 1 or 2: ")
            if choice.strip() != "1":
                print("Exiting program. Please free up port 5000 and try again.")
                sys.exit(1)
        except:
            # If running non-interactively, exit
            print("Exiting program. Please free up port 5000 and try again.")
            sys.exit(1)
    
    app.logger.info(f"Starting Flask application on port {port}")
    print(f"Starting server on http://localhost:{port}")
    print(f"To view the application, open http://localhost:{port}/static/index.html in your browser")
    
    try:
        # Try to run on specifically port 5000 with host='0.0.0.0' to allow external connections
        app.run(debug=True, port=port, host='0.0.0.0')
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"ERROR: Port {port} is already in use by another application.")
            print("This application must use port 5000.")
            print("Please close the other application using this port and try again.")
        else:
            print(f"ERROR: {str(e)}")
        sys.exit(1)
