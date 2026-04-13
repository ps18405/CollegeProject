# 💰 Advanced Expense Tracker

A modern, feature-rich expense tracking application built with Flask, SQLite, and Bootstrap 5. Manage your finances with advanced analytics, budgeting tools, and detailed reporting.

---

## ✨ Features

### 🔐 **Security & Authentication**
- User registration with email validation
- Password hashing using `werkzeug.security`
- Strong password enforcement (minimum 6 characters, requires digits)
- Session management with secure login/logout
- Input validation on all forms
- Protected routes (login required)

### 📊 **Dashboard & Analytics**
- **Interactive Dashboard** with real-time statistics
  - Total spending overview
  - Current month spending tracker
  - Total expenses count
  - Active categories count
- **Advanced Charts**
  - Pie/Doughnut charts for category breakdown
  - Bar charts for spending comparison
  - Line charts for spending trends
  - Monthly trend visualization
  - Payment method distribution

### 💸 **Expense Management**
- **Add Expenses** with rich details:
  - Amount tracking
  - Category selection (predefined list)
  - Description
  - Expense date
  - Payment method (Cash, Credit Card, Online Transfer, UPI)
  - Status (Paid/Pending)
  - Tags for organization
- **Edit & Delete** expenses with full validation
- **Search & Filter** by:
  - Description keywords
  - Category
  - Date range
  - Multiple criteria at once

### 💰 **Budget Management**
- Set budgets per category
- Multiple budget periods (Weekly, Monthly, Yearly)
- Real-time budget tracking
- Visual progress bars
- Budget alerts when spending exceeds limit
- Percentage tracking and overspend warnings

### 🔄 **Recurring Expenses**
- Automate recurring transactions
- Support for multiple frequencies:
  - Daily
  - Weekly
  - Monthly
  - Yearly
- Auto-generate expenses on scheduled dates
- Track recurring expenses separately

### 📈 **Advanced Reports**
- **12-Month Trend Analysis**
  - Monthly spending history
  - Average spending calculation
  - Spending pattern visualization
- **Category Breakdown**
  - Amount spent per category
  - Percentage distribution
  - Detailed analysis
- **Payment Method Analysis**
  - Distribution by payment type
  - Usage statistics
- **Smart Insights**
  - Spending trend indicators
  - Monthly comparisons
  - Intelligent recommendations

### 📥 **Data Export**
- **CSV Export** with filters
- Export by date range
- Category-specific exports
- Payment method filtering
- Compatible with Excel and spreadsheets

### 🎨 **User Interface**
- Modern, responsive design with Bootstrap 5
- **Light & Dark Mode** toggle
- Mobile-friendly interface
- Smooth animations and transitions
- Status badges and color coding
- Professional color scheme
- Font Awesome icons throughout
- Empty state messaging
- Success/Error notifications

---

## 🛠️ Installation

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Setup Steps

1. **Clone/Download the project:**
   ```bash
   cd expense-tracker
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install flask werkzeug
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Access the application:**
   - Open browser and go to: `http://localhost:5000`
   - You'll be redirected to login page

---

## 📋 Database Schema

### Users Table
```
- id: Primary Key
- username: Unique username
- email: Email address
- password: Hashed password
- created_at: Account creation timestamp
- theme_preference: Light/Dark mode
- currency: Preferred currency
```

### Expenses Table
```
- id: Primary Key
- user_id: Foreign Key (users)
- amount: Expense amount
- category: Category name
- description: Expense description
- expense_date: Date of expense
- payment_method: Payment type
- status: Paid/Pending
- tags: Custom tags
- created_at: Creation timestamp
- updated_at: Last update timestamp
- is_recurring: Boolean flag
- recurring_id: Link to recurring expense
```

### Budgets Table
```
- id: Primary Key
- user_id: Foreign Key (users)
- category: Budget category
- budget_amount: Budget limit
- period: Weekly/Monthly/Yearly
- start_date: Budget period start
- end_date: Budget period end
- created_at: Creation timestamp
```

### Recurring Expenses Table
```
- id: Primary Key
- user_id: Foreign Key (users)
- amount: Recurring amount
- category: Category name
- description: Description
- payment_method: Payment type
- frequency: Daily/Weekly/Monthly/Yearly
- next_date: Next scheduled date
- status: Active/Inactive
- created_at: Creation timestamp
```

---

## 🚀 Usage Guide

### **Getting Started**

1. **Register** a new account
   - Username (3+ characters)
   - Valid email address
   - Strong password (6+ chars, with numbers)
   - Confirm password

2. **Login** with your credentials

### **Main Dashboard**

The dashboard provides:
- Quick stats cards (Total, Monthly, Count, Categories)
- Budget alerts (if any budgets exceeded)
- Advanced filters
- Quick action buttons
- Recent expenses table
- Interactive charts

### **Adding Expenses**

1. Fill in the "Add New Expense" form:
   - Amount (required)
   - Category (dropdown)
   - Description (required)
   - Date (defaults to today)
   - Payment Method
2. Click "Add" button
3. Expense appears in table and updates charts

### **Managing Budgets**

1. Click **"Manage Budgets"** button
2. Fill "Create New Budget" form:
   - Select Category
   - Enter Budget Amount
   - Choose Period (Weekly/Monthly/Yearly)
3. View active budgets with progress bars
4. Receive alerts when budget exceeded
5. Delete budgets as needed

### **Recurring Expenses**

1. Click **"Recurring Expenses"** button
2. Add recurring expense:
   - Amount
   - Category
   - Description
   - Frequency (Daily/Weekly/Monthly/Yearly)
   - Start Date
3. System auto-generates on scheduled dates
4. View all active recurring expenses
5. Manage or delete as needed

### **Viewing Reports**

1. Click **"View Reports"** button
2. Explore:
   - 12-month spending trend
   - Monthly average spending
   - Category breakdown with percentages
   - Payment method distribution
   - AI-generated insights
3. Compare months and identify patterns

### **Searching & Filtering**

On dashboard:
1. Enter search keywords in description field
2. Select category from dropdown
3. Choose date range
4. Click "Search"
5. Results filter in real-time

### **Exporting Data**

1. Click **"Export CSV"** button
2. Optional: Apply filters
3. Download CSV file
4. Open in Excel or spreadsheet app

### **Dark Mode**

- Click moon icon in navbar
- Preference saves automatically
- Works across all pages

---

## 📁 Project Structure

```
expense-tracker/
│
├── app.py                          # Main Flask application
│
├── templates/
│   ├── dashboard.html              # Main dashboard (replaces index.html)
│   ├── login.html                  # Enhanced login page
│   ├── register.html               # Enhanced registration
│   ├── edit.html                   # Edit expense page
│   ├── budgets.html                # Budget management page
│   ├── recurring.html              # Recurring expenses page
│   └── reports.html                # Advanced reports page
│
├── database.db                     # SQLite database (auto-created)
├── venv/                           # Virtual environment
└── README.md                       # This file
```

---

## 🔑 Key Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Main dashboard |
| `/login` | GET, POST | Login page |
| `/register` | GET, POST | Registration page |
| `/add` | POST | Add new expense |
| `/edit/<id>` | GET | Edit expense form |
| `/update/<id>` | POST | Update expense |
| `/delete/<id>` | GET | Delete expense |
| `/budgets` | GET | View budgets |
| `/add_budget` | POST | Create new budget |
| `/delete_budget/<id>` | GET | Delete budget |
| `/recurring` | GET | View recurring expenses |
| `/add_recurring` | POST | Add recurring expense |
| `/delete_recurring/<id>` | GET | Delete recurring |
| `/reports` | GET | View reports |
| `/export_csv` | GET | Download CSV |
| `/api/chart_data` | GET | API for charts |
| `/logout` | GET | Logout |

---

## 🎯 Categories Available

- Food
- Transport
- Entertainment
- Shopping
- Bills
- Healthcare
- Education
- Other

---

## 💡 Advanced Features Explained

### **Smart Budget Alerts**
- System monitors spending in real-time
- Alerts appear on dashboard when budget exceeded
- Shows percentage over budget
- Color-coded warning system

### **Auto-Processing Recurring**
- Background process checks recurring expenses
- Automatically creates new entries when due
- Updates next scheduled date based on frequency
- Maintains recurring relationship tracking

### **Search & Filter**
- Real-time filtering by multiple criteria
- Case-insensitive search
- Date range support
- Quick filter reset option

### **Chart.js Integration**
- Interactive, responsive charts
- Hover tooltips
- Multiple chart types (pie, bar, line)
- Auto-updates based on filters

### **Session Management**
- Secure session handling
- Automatic user ID tracking
- Protected routes
- Clean logout clearing all sessions

---

## 🔒 Security Features

✅ **Password Security**
- Hashed using PBKDF2-SHA256
- Minimum 6 characters
- Must contain numbers
- Strength indicator during registration

✅ **Input Validation**
- All inputs validated server-side
- Email format verification
- Amount format checking
- Category whitelist validation
- SQL injection prevention (parameterized queries)

✅ **User Protection**
- Ownership verification on edit/delete
- Session-based authentication
- Protected routes with decorators
- Unique username/email constraints

---

## 🚨 Error Handling

- Form validation with user feedback
- Database error handling
- Invalid route handling
- Redirect to appropriate pages on errors
- User-friendly error messages
- Success notifications

---

## 🔄 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers

---

## 📝 Tips & Best Practices

1. **Set Realistic Budgets** - Use historical data to set achievable budget limits
2. **Categorize Properly** - Consistent categorization improves reports
3. **Regular Reviews** - Check reports monthly to identify spending patterns
4. **Use Recurring** - Set up recurring for fixed expenses (rent, subscriptions)
5. **Export Reports** - Keep monthly exports for accounting/record keeping
6. **Tag Expenses** - Use tags for special purposes (urgent, deductible, etc.)
7. **Monitor Alerts** - Respond to budget alerts promptly

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Port 5000 already in use** | Change port in `app.run(port=5001)` |
| **Database locked** | Close other instances, restart app |
| **Charts not showing** | Check Chart.js CDN connection |
| **Dark mode not working** | Clear browser cache, refresh |
| **Password validation fails** | Ensure 6+ chars with at least 1 number |

---

## 🚀 Future Enhancement Ideas

- [ ] Multi-currency support with conversion
- [ ] Bank statement imports
- [ ] Receipt image uploads with OCR
- [ ] Email notifications for budget alerts
- [ ] Mobile app version
- [ ] Data backup & restore
- [ ] Shared accounts/family budgeting
- [ ] Income tracking
- [ ] Investment tracking
- [ ] Bill reminders
- [ ] Spending goals with progress
- [ ] Data analytics & ML predictions
- [ ] API for third-party integrations
- [ ] Two-factor authentication
- [ ] Password reset via email

---

## 📄 License

This project is open source and available for personal and educational use.

---

## 👨‍💻 Development Notes

### Technologies Used
- **Backend**: Python Flask
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3, JavaScript
- **UI Framework**: Bootstrap 5
- **Charts**: Chart.js
- **Icons**: Font Awesome 6.4
- **Security**: Werkzeug Password Hashing

### Key Libraries
```
flask==2.3.0+
werkzeug==2.3.0+
```

### Testing
Run with debug mode enabled (default):
```python
app.run(debug=True)  # Auto-reloads on code changes
```

---

## 📞 Support & Feedback

For issues or feature requests, consider:
1. Checking the troubleshooting section
2. Reviewing browser console (F12) for JavaScript errors
3. Checking database file permissions
4. Ensuring Python and dependencies are properly installed

---

## 🎉 Acknowledgments

- Bootstrap 5 for responsive design framework
- Chart.js for interactive visualizations
- Font Awesome for beautiful icons
- Flask framework for web development
- Werkzeug for security utilities

---

**Last Updated**: March 2026  
**Version**: 2.0 (Advanced)  
**Status**: Production Ready ✅

Enjoy tracking your expenses! 💚
