"""
Reset password for testuser account
"""

import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect('database.db')
cur = conn.cursor()

# Check if user exists
cur.execute("SELECT id, username FROM users WHERE username='testuser'")
user = cur.fetchone()

if user:
    user_id, username = user
    print(f"✓ Found user: {username} (ID: {user_id})")
    
    # Hash new password
    new_password = 'password123'
    hashed = generate_password_hash(new_password)
    
    # Update password
    cur.execute("UPDATE users SET password=? WHERE id=?", (hashed, user_id))
    conn.commit()
    
    print(f"✓ Password reset successfully!")
    print(f"\nLogin credentials:")
    print(f"  Username: testuser")
    print(f"  Password: password123")
else:
    print("✗ User 'testuser' not found in database")
    print("\nCreating new testuser account...")
    
    hashed = generate_password_hash('password123')
    cur.execute("""
        INSERT INTO users (username, email, password)
        VALUES (?, ?, ?)
    """, ('testuser', 'test@example.com', hashed))
    conn.commit()
    
    print(f"✓ User 'testuser' created successfully!")
    print(f"\nLogin credentials:")
    print(f"  Username: testuser")
    print(f"  Password: password123")

conn.close()
