# CUST Research Desk - User Authentication Module

## Features Implemented:
- User registration with role (Author, Reviewer, Chair)
- Secure password hashing with Werkzeug
- Role-based login and redirection
- Author dashboard with complete submission form
- Paper upload, edit, and view functionality

## How to Test:
1. Run `app.py` (Python 3.x with Flask and SQLAlchemy required).
2. Visit `http://127.0.0.1:5000/register` to register a new user.
3. Login at `/login` using the registered email and password.
4. Based on role, you'll be redirected to your dashboard.
   
## Setup Notes:
- Ensure `static/uploads/` folder exists or will be created automatically.
- The database is SQLite and saved as `cust_research_desk.db`.

requirements.txt