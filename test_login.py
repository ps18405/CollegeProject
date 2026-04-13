import sqlite3
from werkzeug.security import check_password_hash

# Use Row factory like app.py does
conn = sqlite3.connect('database.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Test the exact login logic 
username = 'testuser'
password = 'password123'

cur.execute("SELECT * FROM users WHERE username=?", (username,))
user = cur.fetchone()
conn.close()

if user:
    # Test the login condition from app.py line 398
    login_successful = user and check_password_hash(user['password'], password)
    
    print(f"User found: {user is not None}")
    print(f"Password in DB: {user['password'][:50]}...")
    print(f"Password verification: {check_password_hash(user['password'], password)}")
    print(f"Login result: {login_successful}")
else:
    print("User not found")
