from flask import Flask, render_template, request, redirect
import sqlite3
from urllib.parse import urlparse
app = Flask(__name__)

# Initialize the database
def init_db():
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            originalurl TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Function to get a database connection
def get_db_connection():
    conn = sqlite3.connect('my_database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database on application startup
init_db()
@app.route('/')
def root():
    return render_template('index.html')
# Route to create a short URL
@app.route('/create-url/', methods=['POST'])
def create():
    link = request.form['url']
    parsed_url = urlparse(link)
    if not parsed_url.scheme:
        link = "https://" + link
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the URL already exists in the database
    cursor.execute("SELECT id FROM urls WHERE originalurl = ?", (link,))
    existing_record = cursor.fetchone()

    if existing_record:
        # URL already exists, retrieve the existing ID
        url_id = existing_record['id']
    else:
        # URL doesn't exist, add it to the database
        cursor.execute("INSERT INTO urls(originalurl) VALUES(?)", (link,))
        conn.commit()
        
        # Retrieve the last inserted ID
        url_id = cursor.lastrowid

    conn.close()

    return render_template("result.html", shortURL=f"localhost:5000/url/{url_id}/")

# Route to redirect to the original URL
@app.route('/url/<int:id>/')
def index(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT originalurl FROM urls WHERE id=?", (id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return redirect(result['originalurl'])
    else:
        return render_template('wrongReq.html'), 404

# Error handler for 404 Not Found
@app.errorhandler(404)
def page_not_found(error):
    return render_template('wrongReq.html'), 404

if __name__ == "__main__":
    app.run(host="localhost", port=1080)
