from flask import Flask, jsonify, send_from_directory
import sqlite3
from SCRAPERS.makeOneCsv import makeOneDF  # Import the function to update the database

app = Flask(__name__, static_folder="../frontend", static_url_path="/")

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/signup.html")
def signup():
    return send_from_directory(app.static_folder, "signup.html")

@app.route("/database.html")
def database():
    return send_from_directory(app.static_folder, "database.html")

@app.route("/api/items", methods=["GET"])
def get_items():
    conn = sqlite3.connect("chrome_hearts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    rows = cursor.fetchall()
    conn.close()

    # Convert rows to a list of dictionaries
    columns = [col[0] for col in cursor.description]
    items = [dict(zip(columns, row)) for row in rows]

    return jsonify(items)

@app.route("/api/update", methods=["POST"])
def update_database():
    try:
        # Trigger the scraping and database update process
        makeOneDF()
        return jsonify({"message": "Database updated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/websites", methods=["GET"])
def get_websites():
    try:
        with open("submitted_websites.txt", "r") as f:
            websites = f.readlines()
        websites = [line.strip() for line in websites if line.strip()]
        return jsonify({"websites": websites})
    except FileNotFoundError:
        return jsonify({"websites": []})

if __name__ == "__main__":
    app.run(debug=True)
