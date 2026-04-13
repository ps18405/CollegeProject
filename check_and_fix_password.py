import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

conn = sqlite3.connect('database.db')
cur = conn.cursor()

# Get current user
cur.execute("SELECT id, username, password FROM users WHERE username='testuser'")
user = cur.fetchone()

if user:
    user_id, username, old_hash = user
    print(f"Found user: {username} (ID: {user_id})")
    print(f"Old hash: {old_hash[:50]}...")
    
    # Generate new hash
    new_password = 'password123'
    new_hash = generate_password_hash(new_password)
    print(f"New hash: {new_hash[:50]}...")
    
    # Update in database
    cur.execute("UPDATE users SET password=? WHERE id=?", (new_hash, user_id))
    conn.commit()
    
    # Verify by re-reading
    cur.execute("SELECT password FROM users WHERE id=?", (user_id,))
    stored_hash = cur.fetchone()[0]
    print(f"Stored hash: {stored_hash[:50]}...")
    
    # Test verification
    test_result = check_password_hash(stored_hash, new_password)
    print(f"Verification result: {test_result}")
    
    if test_result:
        print("✓ Password successfully updated and verified!")
    else:
        print("✗ Something went wrong with password verification")
else:
    print("User not found")

conn.close()
