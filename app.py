from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import csv
import io
import re
from functools import wraps

app = Flask(__name__)
app.secret_key = "secret123_change_in_production"

# 🟢 Predefined Categories
CATEGORIES = ['Food', 'Transport', 'Entertainment', 'Shopping', 'Bills', 'Healthcare', 'Education', 'Other']
BUDGET_PERIODS = ['Monthly', 'Weekly', 'Yearly']
PAYMENT_METHODS = ['Cash', 'Credit Card', 'Debit Card', 'Online Transfer', 'UPI']

# 🟢 Initialize DB with Enhanced Schema
def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # Users table with enhanced fields
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            theme_preference TEXT DEFAULT 'light',
            currency TEXT DEFAULT 'INR'
        )
    ''')
    
    # Migration: Add missing columns to existing users table
    try:
        cur.execute("ALTER TABLE users ADD COLUMN email TEXT UNIQUE")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cur.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    except sqlite3.OperationalError:
        pass
    
    try:
        cur.execute("ALTER TABLE users ADD COLUMN theme_preference TEXT DEFAULT 'light'")
    except sqlite3.OperationalError:
        pass
    
    try:
        cur.execute("ALTER TABLE users ADD COLUMN currency TEXT DEFAULT 'INR'")
    except sqlite3.OperationalError:
        pass
    
    # Migration: Update password storage if needed (convert plain text to hash)
    try:
        cur.execute("SELECT password FROM users LIMIT 1")
        result = cur.fetchone()
        if result and result[0] and not (result[0].startswith('pbkdf2:sha256:') or result[0].startswith('scrypt:')):
            # Password is plain text, hash existing passwords
            cur.execute("SELECT id, password FROM users")
            users = cur.fetchall()
            for user_id, plain_password in users:
                hashed = generate_password_hash(plain_password)
                cur.execute("UPDATE users SET password = ? WHERE id = ?", (hashed, user_id))
    except:
        pass  # Skip if no data or already migrated

    # Expenses table with comprehensive fields
    cur.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            expense_date DATE NOT NULL,
            payment_method TEXT DEFAULT 'Cash',
            status TEXT DEFAULT 'paid',
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_recurring INTEGER DEFAULT 0,
            recurring_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    # Migration: Add missing columns to existing expenses table
    try:
        cur.execute("ALTER TABLE expenses ADD COLUMN expense_date DATE NOT NULL DEFAULT CURRENT_DATE")
    except sqlite3.OperationalError:
        pass
    
    try:
        cur.execute("ALTER TABLE expenses ADD COLUMN payment_method TEXT DEFAULT 'Cash'")
    except sqlite3.OperationalError:
        pass
    
    try:
        cur.execute("ALTER TABLE expenses ADD COLUMN status TEXT DEFAULT 'paid'")
    except sqlite3.OperationalError:
        pass
    
    try:
        cur.execute("ALTER TABLE expenses ADD COLUMN tags TEXT")
    except sqlite3.OperationalError:
        pass
    
    try:
        cur.execute("ALTER TABLE expenses ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    except sqlite3.OperationalError:
        pass
    
    try:
        cur.execute("ALTER TABLE expenses ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    except sqlite3.OperationalError:
        pass
    
    try:
        cur.execute("ALTER TABLE expenses ADD COLUMN is_recurring INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    
    try:
        cur.execute("ALTER TABLE expenses ADD COLUMN recurring_id INTEGER")
    except sqlite3.OperationalError:
        pass

    # Budget table for budget management
    cur.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            budget_amount REAL NOT NULL,
            period TEXT NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # Recurring Expenses table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS recurring_expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            payment_method TEXT DEFAULT 'Cash',
            frequency TEXT NOT NULL,
            next_date DATE NOT NULL,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# 🟢 Utility Functions
def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one digit"
    return True, "Valid"

def login_required(f):
    """Decorator to check if user is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def process_recurring_expenses():
    """Process recurring expenses - create new entries if needed"""
    conn = get_db_connection()
    cur = conn.cursor()
    today = datetime.now().date()
    
    cur.execute("SELECT * FROM recurring_expenses WHERE status='active'")
    recurring = cur.fetchall()
    
    for rec in recurring:
        next_date = datetime.strptime(rec['next_date'], '%Y-%m-%d').date()
        if next_date <= today:
            # Create new expense
            cur.execute("""
                INSERT INTO expenses (user_id, amount, category, description, 
                expense_date, payment_method, is_recurring, recurring_id)
                VALUES (?, ?, ?, ?, ?, ?, 1, ?)
            """, (rec['user_id'], rec['amount'], rec['category'], rec['description'],
                  today, rec['payment_method'], rec['id']))
            
            # Update next date based on frequency
            if rec['frequency'] == 'Daily':
                next_date = today + timedelta(days=1)
            elif rec['frequency'] == 'Weekly':
                next_date = today + timedelta(weeks=1)
            elif rec['frequency'] == 'Monthly':
                next_date = today + timedelta(days=30)
            elif rec['frequency'] == 'Yearly':
                next_date = today + timedelta(days=365)
            
            cur.execute("UPDATE recurring_expenses SET next_date=? WHERE id=?", 
                       (next_date, rec['id']))
    
    conn.commit()
    conn.close()

# 🟢 Home/Dashboard
@app.route('/')
@login_required
def home():
    process_recurring_expenses()
    
    conn = get_db_connection()
    cur = conn.cursor()
    user_id = session['user_id']
    
    # Get filter parameters
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    # Build query
    query = "SELECT * FROM expenses WHERE user_id=?"
    params = [user_id]
    
    if search:
        query += " AND (description LIKE ? OR category LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    
    if category and category != 'all':
        query += " AND category=?"
        params.append(category)
    
    if date_from:
        query += " AND expense_date >= ?"
        params.append(date_from)
    
    if date_to:
        query += " AND expense_date <= ?"
        params.append(date_to)
    
    query += " ORDER BY expense_date DESC"
    
    cur.execute(query, params)
    expenses = [dict(row) for row in cur.fetchall()]
    
    # Get totals
    cur.execute("SELECT SUM(amount) FROM expenses WHERE user_id=? AND status='paid'", (user_id,))
    total = cur.fetchone()[0] or 0
    
    # Get this month total
    today = datetime.now().date()
    month_start = today.replace(day=1)
    cur.execute("""SELECT SUM(amount) FROM expenses 
                   WHERE user_id=? AND expense_date >= ? AND status='paid'""", 
                (user_id, month_start))
    month_total = cur.fetchone()[0] or 0
    
    # Get category data
    cur.execute("""SELECT category, SUM(amount) FROM expenses 
                   WHERE user_id=? AND status='paid' GROUP BY category""", (user_id,))
    category_data = [list(row) for row in cur.fetchall()]
    
    # Get budget info
    cur.execute("""SELECT b.category, b.budget_amount, SUM(e.amount) as spent
                   FROM budgets b
                   LEFT JOIN expenses e ON b.category=e.category AND e.user_id=b.user_id
                   WHERE b.user_id=? AND b.start_date <= ? AND b.end_date >= ?
                   GROUP BY b.category""", (user_id, today, today))
    budget_data = [list(row) for row in cur.fetchall()]
    
    # Check budget alerts
    budget_alerts = []
    for budget in budget_data:
        spent = budget[2] or 0
        if spent > budget[1]:
            budget_alerts.append({
                'category': budget[0],
                'budget': budget[1],
                'spent': spent,
                'percent': int((spent / budget[1]) * 100)
            })
    
    conn.close()
    
    return render_template('dashboard.html', 
                         expenses=expenses, 
                         total=total,
                         month_total=month_total,
                         category_data=category_data,
                         budget_data=budget_data,
                         budget_alerts=budget_alerts,
                         categories=CATEGORIES,
                         search=search,
                         category=category,
                         date_from=date_from,
                         date_to=date_to)

# 🟢 Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        errors = []
        
        if not username or len(username) < 3:
            errors.append("Username must be at least 3 characters")
        
        if not email or not validate_email(email):
            errors.append("Please enter a valid email")
        
        if password != confirm_password:
            errors.append("Passwords do not match")
        
        valid, msg = validate_password(password)
        if not valid:
            errors.append(msg)
        
        if errors:
            return render_template('register.html', errors=errors)
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if username already exists
        cur.execute("SELECT id FROM users WHERE username=?", (username,))
        if cur.fetchone():
            return render_template('register.html', errors=['Username already exists'])
        
        # Check if email already exists
        cur.execute("SELECT id FROM users WHERE email=?", (email,))
        if cur.fetchone():
            return render_template('register.html', errors=['Email already exists'])
        
        # Hash password and insert
        hashed_password = generate_password_hash(password)
        try:
            cur.execute("""INSERT INTO users (username, email, password) 
                          VALUES (?, ?, ?)""", 
                       (username, email, hashed_password))
            conn.commit()
            conn.close()
            return redirect('/login?success=1')
        except Exception as e:
            conn.close()
            return render_template('register.html', errors=['Registration failed'])
    
    return render_template('register.html')

# 🟢 Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            return render_template('login.html', error='Please enter username and password')
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cur.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect('/')
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

# 🟢 Logout
@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect('/login')

# 🟢 Add Expense
@app.route('/add', methods=['POST'])
@login_required
def add_expense():
    try:
        amount = request.form.get('amount', '')
        category = request.form.get('category', '')
        description = request.form.get('description', '')
        expense_date = request.form.get('expense_date', str(datetime.now().date()))
        payment_method = request.form.get('payment_method', 'Cash')
        status = request.form.get('status', 'paid')
        tags = request.form.get('tags', '')
        
        # Validate amount
        try:
            amount = float(amount)
            if amount <= 0:
                return redirect('/?error=Amount must be positive')
        except ValueError:
            return redirect('/?error=Invalid amount format')
        
        if not category or category not in CATEGORIES:
            return redirect('/?error=Invalid category')
        
        if not description or len(description) < 3:
            return redirect('/?error=Description required (min 3 chars)')
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO expenses (user_id, amount, category, description, 
                                expense_date, payment_method, status, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (session['user_id'], amount, category, description, 
              expense_date, payment_method, status, tags))
        
        conn.commit()
        conn.close()
        
        return redirect('/?success=1')
    except Exception as e:
        return redirect('/?error=Failed to add expense')

# 🟢 Delete Expense
@app.route('/delete/<int:id>')
@login_required
def delete_expense(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check ownership
        cur.execute("SELECT user_id FROM expenses WHERE id=?", (id,))
        expense = cur.fetchone()
        
        if expense and expense['user_id'] == session['user_id']:
            cur.execute("DELETE FROM expenses WHERE id=?", (id,))
            conn.commit()
        
        conn.close()
        return redirect('/?success=1')
    except:
        return redirect('/?error=Failed to delete')

# 🟢 Edit Expense Page
@app.route('/edit/<int:id>')
@login_required
def edit_expense(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM expenses WHERE id=? AND user_id=?", 
                   (id, session['user_id']))
        expense = cur.fetchone()
        conn.close()
        
        if not expense:
            return redirect('/?error=Expense not found')
        
        expense = dict(expense) if expense else None
        
        return render_template('edit.html', expense=expense, 
                             categories=CATEGORIES, 
                             payment_methods=PAYMENT_METHODS)
    except:
        return redirect('/?error=Failed to load expense')

# 🟢 Update Expense
@app.route('/update/<int:id>', methods=['POST'])
@login_required
def update_expense(id):
    try:
        amount = request.form.get('amount', '')
        category = request.form.get('category', '')
        description = request.form.get('description', '')
        expense_date = request.form.get('expense_date', str(datetime.now().date()))
        payment_method = request.form.get('payment_method', 'Cash')
        status = request.form.get('status', 'paid')
        tags = request.form.get('tags', '')
        
        # Validate
        try:
            amount = float(amount)
            if amount <= 0:
                return redirect('/edit/{}?error=Amount must be positive'.format(id))
        except ValueError:
            return redirect('/edit/{}?error=Invalid amount'.format(id))
        
        if not category or category not in CATEGORIES:
            return redirect('/edit/{}?error=Invalid category'.format(id))
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Verify ownership
        cur.execute("SELECT user_id FROM expenses WHERE id=?", (id,))
        expense = cur.fetchone()
        
        if expense and expense['user_id'] == session['user_id']:
            cur.execute("""
                UPDATE expenses 
                SET amount=?, category=?, description=?, 
                    expense_date=?, payment_method=?, status=?, tags=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            """, (amount, category, description, expense_date, 
                  payment_method, status, tags, id))
            conn.commit()
        
        conn.close()
        return redirect('/?success=1')
    except Exception as e:
        return redirect('/?error=Failed to update')

# 🟢 Budget Management - View Budgets
@app.route('/budgets')
@login_required
def view_budgets():
    conn = get_db_connection()
    cur = conn.cursor()
    
    today = datetime.now().date()
    cur.execute("""
        SELECT b.*, SUM(e.amount) as spent
        FROM budgets b
        LEFT JOIN expenses e ON b.category=e.category AND e.user_id=b.user_id
        WHERE b.user_id=?
        GROUP BY b.id
        ORDER BY b.category
    """, (session['user_id'],))
    
    budgets = [dict(row) for row in cur.fetchall()]
    conn.close()
    
    return render_template('budgets.html', budgets=budgets, categories=CATEGORIES, periods=BUDGET_PERIODS)

# 🟢 Add Budget
@app.route('/add_budget', methods=['POST'])
@login_required
def add_budget():
    try:
        category = request.form.get('category', '')
        budget_amount = request.form.get('budget_amount', '')
        period = request.form.get('period', 'Monthly')
        
        try:
            budget_amount = float(budget_amount)
            if budget_amount <= 0:
                return redirect('/budgets?error=Amount must be positive')
        except ValueError:
            return redirect('/budgets?error=Invalid amount')
        
        if not category or category not in CATEGORIES:
            return redirect('/budgets?error=Invalid category')
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Calculate start and end dates based on period
        today = datetime.now().date()
        if period == 'Monthly':
            start_date = today.replace(day=1)
            if today.month == 12:
                end_date = today.replace(year=today.year+1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = today.replace(month=today.month+1, day=1) - timedelta(days=1)
        elif period == 'Weekly':
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
        elif period == 'Yearly':
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
        
        cur.execute("""
            INSERT INTO budgets (user_id, category, budget_amount, period, start_date, end_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (session['user_id'], category, budget_amount, period, start_date, end_date))
        
        conn.commit()
        conn.close()
        
        return redirect('/budgets?success=1')
    except Exception as e:
        return redirect('/budgets?error=Failed to add budget')

# 🟢 Delete Budget
@app.route('/delete_budget/<int:id>')
@login_required
def delete_budget(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT user_id FROM budgets WHERE id=?", (id,))
        budget = cur.fetchone()
        
        if budget and budget['user_id'] == session['user_id']:
            cur.execute("DELETE FROM budgets WHERE id=?", (id,))
            conn.commit()
        
        conn.close()
        return redirect('/budgets?success=1')
    except:
        return redirect('/budgets?error=Failed to delete')

# 🟢 Recurring Expenses
@app.route('/recurring')
@login_required
def view_recurring():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM recurring_expenses 
        WHERE user_id=? ORDER BY next_date
    """, (session['user_id'],))
    
    recurring = [dict(row) for row in cur.fetchall()]
    conn.close()
    
    return render_template('recurring.html', recurring=recurring, 
                         categories=CATEGORIES, payment_methods=PAYMENT_METHODS)

# 🟢 Add Recurring Expense
@app.route('/add_recurring', methods=['POST'])
@login_required
def add_recurring():
    try:
        amount = request.form.get('amount', '')
        category = request.form.get('category', '')
        description = request.form.get('description', '')
        frequency = request.form.get('frequency', 'Monthly')
        payment_method = request.form.get('payment_method', 'Cash')
        next_date = request.form.get('next_date', str(datetime.now().date()))
        
        try:
            amount = float(amount)
            if amount <= 0:
                return redirect('/recurring?error=Amount must be positive')
        except ValueError:
            return redirect('/recurring?error=Invalid amount')
        
        if not category or category not in CATEGORIES:
            return redirect('/recurring?error=Invalid category')
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO recurring_expenses 
            (user_id, amount, category, description, frequency, next_date, payment_method)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (session['user_id'], amount, category, description, frequency, next_date, payment_method))
        
        conn.commit()
        conn.close()
        
        return redirect('/recurring?success=1')
    except Exception as e:
        return redirect('/recurring?error=Failed to add')

# 🟢 Delete Recurring
@app.route('/delete_recurring/<int:id>')
@login_required
def delete_recurring(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT user_id FROM recurring_expenses WHERE id=?", (id,))
        recurring = cur.fetchone()
        
        if recurring and recurring['user_id'] == session['user_id']:
            cur.execute("DELETE FROM recurring_expenses WHERE id=?", (id,))
            conn.commit()
        
        conn.close()
        return redirect('/recurring?success=1')
    except:
        return redirect('/recurring?error=Failed to delete')

# 🟢 Reports - Monthly Report
@app.route('/reports')
@login_required
def view_reports():
    conn = get_db_connection()
    cur = conn.cursor()
    user_id = session['user_id']
    
    # Get monthly data for last 12 months
    today = datetime.now().date()
    months = []
    for i in range(11, -1, -1):
        if today.month - i > 0:
            month_date = today.replace(month=today.month-i, day=1)
        else:
            month_date = today.replace(year=today.year-1, month=12+today.month-i, day=1)
        months.append(month_date)
    
    monthly_totals = []
    for month in months:
        if month.month == 12:
            next_month = month.replace(year=month.year+1, month=1)
        else:
            next_month = month.replace(month=month.month+1)
        
        cur.execute("""
            SELECT SUM(amount) FROM expenses 
            WHERE user_id=? AND expense_date >= ? AND expense_date < ? AND status='paid'
        """, (user_id, month, next_month))
        
        total = cur.fetchone()[0] or 0
        monthly_totals.append({
            'month': month.strftime('%B %Y'),
            'total': total
        })
    
    # Get category breakdown for current month
    month_start = today.replace(day=1)
    cur.execute("""
        SELECT category, SUM(amount) as total FROM expenses
        WHERE user_id=? AND expense_date >= ? AND status='paid'
        GROUP BY category ORDER BY total DESC
    """, (user_id, month_start))
    
    category_breakdown = [dict(row) for row in cur.fetchall()]
    
    # Get payment method breakdown
    cur.execute("""
        SELECT payment_method, SUM(amount) as total FROM expenses
        WHERE user_id=? AND expense_date >= ? AND status='paid'
        GROUP BY payment_method
    """, (user_id, month_start))
    
    payment_breakdown = [dict(row) for row in cur.fetchall()]
    
    conn.close()
    
    return render_template('reports.html', 
                         monthly_totals=monthly_totals,
                         category_breakdown=category_breakdown,
                         payment_breakdown=payment_breakdown)

# 🟢 CSV Export
@app.route('/export_csv')
@login_required
def export_csv():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        category = request.args.get('category', '')
        
        query = "SELECT * FROM expenses WHERE user_id=?"
        params = [session['user_id']]
        
        if date_from:
            query += " AND expense_date >= ?"
            params.append(date_from)
        if date_to:
            query += " AND expense_date <= ?"
            params.append(date_to)
        if category and category != 'all':
            query += " AND category=?"
            params.append(category)
        
        query += " ORDER BY expense_date DESC"
        
        cur.execute(query, params)
        expenses = cur.fetchall()
        conn.close()
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Amount', 'Category', 'Description', 'Date', 'Payment Method', 'Status', 'Tags'])
        
        for expense in expenses:
            writer.writerow([
                expense['id'],
                expense['amount'],
                expense['category'],
                expense['description'],
                expense['expense_date'],
                expense['payment_method'],
                expense['status'],
                expense['tags']
            ])
        
        output.seek(0)
        response = app.response_class(
            response=output.getvalue(),
            status=200,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment;filename=expenses.csv'}
        )
        return response
    except Exception as e:
        return redirect('/?error=Export failed')

# 🟢 JSON API for charts
@app.route('/api/chart_data')
@login_required
def api_chart_data():
    conn = get_db_connection()
    cur = conn.cursor()
    
    today = datetime.now().date()
    period = request.args.get('period', 'month')  # day, week, month, year
    
    if period == 'month':
        cur.execute("""
            SELECT category, SUM(amount) as total FROM expenses
            WHERE user_id=? AND expense_date >= date('now', 'start of month')
            AND status='paid' GROUP BY category
        """, (session['user_id'],))
    elif period == 'year':
        cur.execute("""
            SELECT strftime('%Y-%m', expense_date) as month, SUM(amount) as total 
            FROM expenses
            WHERE user_id=? AND expense_date >= date('now', 'start of year')
            AND status='paid' GROUP BY month
        """, (session['user_id'],))
    else:  # week
        cur.execute("""
            SELECT strftime('%Y-%m-%d', expense_date) as day, SUM(amount) as total 
            FROM expenses WHERE user_id=? AND expense_date >= 
            date('now', '-6 days') AND status='paid' GROUP BY day
        """, (session['user_id'],))
    
    data = cur.fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in data])

if __name__ == '__main__':
    app.run(debug=True)