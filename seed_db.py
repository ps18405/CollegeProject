"""
Database Seeder - Fills database with realistic dummy data for testing
"""

import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# Connect to database
conn = sqlite3.connect('database.db')
cur = conn.cursor()

# 1. Create test user
try:
    hashed_password = generate_password_hash('password123')
    cur.execute("""
        INSERT INTO users (username, email, password)
        VALUES (?, ?, ?)
    """, ('testuser', 'test@example.com', hashed_password))
    user_id = cur.lastrowid
    print(f"✓ Created user: testuser (ID: {user_id})")
except:
    # Get existing user
    cur.execute("SELECT id FROM users WHERE username='testuser'")
    user_id = cur.fetchone()[0]
    print(f"✓ Using existing user: testuser (ID: {user_id})")

# 2. Insert diverse expenses across different categories and months
expenses_data = [
    # March 2026 (Recent)
    (user_id, 450, 'Food', 'Lunch at restaurant', '2026-03-26', 'Credit Card', 'paid', 'lunch'),
    (user_id, 1200, 'Bills', 'Monthly electricity bill', '2026-03-25', 'Online Transfer', 'paid', 'utilities'),
    (user_id, 850, 'Shopping', 'New clothes and accessories', '2026-03-24', 'Credit Card', 'paid', ''),
    (user_id, 280, 'Food', 'Grocery shopping', '2026-03-23', 'Cash', 'paid', 'groceries'),
    (user_id, 150, 'Transport', 'Fuel for car', '2026-03-22', 'Cash', 'paid', 'fuel'),
    (user_id, 320, 'Food', 'Coffee and snacks', '2026-03-21', 'Cash', 'paid', 'snacks'),
    (user_id, 500, 'Entertainment', 'Movie tickets and popcorn', '2026-03-20', 'Credit Card', 'paid', 'movies'),
    (user_id, 1500, 'Healthcare', 'Doctor consultation and medicines', '2026-03-19', 'Online Transfer', 'paid', 'medical'),
    
    # February 2026
    (user_id, 2500, 'Bills', 'Internet and phone bill', '2026-02-28', 'Online Transfer', 'paid', 'utilities'),
    (user_id, 420, 'Food', 'Dinner with friends', '2026-02-25', 'Credit Card', 'paid', 'dinner'),
    (user_id, 350, 'Transport', 'Auto rickshaw rides', '2026-02-24', 'Cash', 'paid', 'transport'),
    (user_id, 600, 'Entertainment', 'Concert tickets', '2026-02-20', 'Credit Card', 'paid', 'events'),
    (user_id, 200, 'Food', 'Bakery purchases', '2026-02-18', 'Cash', 'paid', 'food'),
    (user_id, 1000, 'Shopping', 'Electronics and gadgets', '2026-02-15', 'Credit Card', 'paid', 'tech'),
    (user_id, 450, 'Education', 'Online course subscription', '2026-02-10', 'Online Transfer', 'paid', 'learning'),
    (user_id, 800, 'Bills', 'Water bill and rent deposit', '2026-02-05', 'Online Transfer', 'paid', 'rent'),
    
    # January 2026
    (user_id, 1200, 'Shopping', 'Winter clothes and jackets', '2026-01-28', 'Credit Card', 'paid', 'clothing'),
    (user_id, 550, 'Food', 'New Year party catering', '2026-01-01', 'Credit Card', 'paid', 'party'),
    (user_id, 300, 'Entertainment', 'Gaming subscription', '2026-01-25', 'Online Transfer', 'paid', 'subscription'),
    (user_id, 650, 'Transport', 'Maintenance and car service', '2026-01-20', 'Cash', 'paid', 'car_service'),
    (user_id, 180, 'Food', 'Meal delivery service', '2026-01-15', 'Credit Card', 'paid', 'delivery'),
    (user_id, 900, 'Healthcare', 'Gym membership', '2026-01-10', 'Online Transfer', 'paid', 'fitness'),
    
    # December 2025
    (user_id, 3000, 'Shopping', 'Christmas gifts', '2025-12-20', 'Credit Card', 'paid', 'gifts'),
    (user_id, 800, 'Entertainment', 'Holiday party', '2025-12-25', 'Cash', 'paid', 'celebration'),
    (user_id, 2500, 'Bills', 'Year-end home repairs', '2025-12-15', 'Online Transfer', 'paid', 'maintenance'),
    (user_id, 450, 'Food', 'Special dinner', '2025-12-24', 'Credit Card', 'paid', 'holiday_food'),
    
    # November 2025
    (user_id, 1500, 'Shopping', 'Black Friday shopping', '2025-11-25', 'Credit Card', 'paid', 'sale'),
    (user_id, 300, 'Education', 'Books and study materials', '2025-11-15', 'Online Transfer', 'paid', 'books'),
    (user_id, 700, 'Transport', 'Long distance travel', '2025-11-10', 'Credit Card', 'paid', 'travel'),
]

for expense in expenses_data:
    try:
        cur.execute("""
            INSERT INTO expenses 
            (user_id, amount, category, description, expense_date, payment_method, status, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, expense)
    except Exception as e:
        print(f"Note: {e}")

print(f"✓ Added {len(expenses_data)} realistic expenses")

# 3. Add budgets for different categories
budgets = [
    (user_id, 'Food', 3000, 'Monthly', '2026-03-01', '2026-03-31'),
    (user_id, 'Transport', 1500, 'Monthly', '2026-03-01', '2026-03-31'),
    (user_id, 'Entertainment', 2000, 'Monthly', '2026-03-01', '2026-03-31'),
    (user_id, 'Shopping', 4000, 'Monthly', '2026-03-01', '2026-03-31'),
    (user_id, 'Healthcare', 2500, 'Monthly', '2026-03-01', '2026-03-31'),
]

for budget in budgets:
    try:
        cur.execute("""
            INSERT INTO budgets 
            (user_id, category, budget_amount, period, start_date, end_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, budget)
    except:
        pass

print(f"✓ Added {len(budgets)} budgets")

# 4. Add recurring expenses
recurring = [
    (user_id, 1200, 'Bills', 'Monthly rent payment', 'Cash', 'Monthly', '2026-04-01', 'active'),
    (user_id, 800, 'Bills', 'Internet and utilities', 'Online Transfer', 'Monthly', '2026-04-05', 'active'),
    (user_id, 500, 'Entertainment', 'Streaming subscription', 'Credit Card', 'Monthly', '2026-03-30', 'active'),
    (user_id, 300, 'Healthcare', 'Gym membership', 'Online Transfer', 'Monthly', '2026-04-10', 'active'),
]

for rec in recurring:
    try:
        cur.execute("""
            INSERT INTO recurring_expenses 
            (user_id, amount, category, description, payment_method, frequency, next_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, rec)
    except:
        pass

print(f"✓ Added {len(recurring)} recurring expenses")

# Commit all changes
conn.commit()
conn.close()

print("\n✅ Database successfully populated with realistic dummy data!")
print("📊 You can now:")
print("   - Login to see thousands in expenses")
print("   - Check reports for 4-month spending history")
print("   - View budget tracking in action")
print("   - See recurring expenses scheduled")
