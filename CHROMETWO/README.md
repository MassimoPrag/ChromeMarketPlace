# Chrome Hearts Database

A full-stack web application that scrapes Chrome Hearts item data from multiple reseller websites and presents it in a sleek interface.

## Features

- Scrapes Chrome Hearts items from multiple websites
- Displays items in a responsive grid layout
- Search functionality to find specific items
- Option to refresh data with new scraping results
- Sleek black, white, and grey design inspired by Chrome Hearts branding

## Setup and Installation

1. Clone this repository
2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with your Google API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

## Running the Application

1. Start the Flask backend:
   ```
   python app.py
   ```
2. Open your browser and navigate to:
   ```
   http://localhost:5000/static/index.html
   ```

## Project Structure

- `app.py` - Flask backend API
- `chrome_hearts.db` - SQLite database for storing scraped items
- `static/` - Frontend files
  - `index.html` - Main HTML page
  - `styles.css` - CSS styles with Chrome Hearts-inspired design
  - `app.js` - JavaScript for frontend functionality

## API Endpoints

- GET `/api/items` - Get all items, optionally filtered by search query
- POST `/api/refresh` - Trigger a new scraping operation and refresh the database

## Troubleshooting

If you see "Cannot connect to server" errors or cannot refresh data:

1. Make sure the Flask server is running by running `python app.py`.
2. Verify that port 5000 is not blocked or used by other services.
3. Check firewall settings or network connectivity.
4. Confirm that your .env file is correctly set up with a valid Google API key.

### Localhost Connection Issues

If you're seeing "Access denied" or cannot connect to localhost:

1. **Run the connection checker**: 
   ```
   python check_connection.py
   ```
   This will diagnose common connection issues.

2. **Try using the IP address directly**:
   Instead of `localhost`, use `127.0.0.1`:
   ```
   http://127.0.0.1:5000/static/index.html
   ```

3. **Check for port conflicts**:
   - On Windows: Run `netstat -ano | findstr :5000` to see what's using port 5000
   - On Mac/Linux: Run `lsof -i :5000` to see what's using port 5000
   - If the port is in use, try running with a different port: `python app.py`

4. **Temporary disable firewall/antivirus**:
   Some security software can block localhost connections.

5. **Check your browser**:
   - Try a different browser
   - Clear browser cache and cookies
   - Disable browser extensions that might interfere
