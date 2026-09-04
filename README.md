# Smart Vehicle Registration & Licensing System

> A Python-powered Streamlit web application for vehicle registration, driver licensing, traffic challan management, and driving examination — built as a Semester 3 Python project.

[![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-red?style=for-the-badge&logo=streamlit)](https://streamlit.io/)
[![MySQL](https://img.shields.io/badge/MySQL-Database-blue?style=for-the-badge&logo=mysql)](https://www.mysql.com/)

---

## Overview

The Smart Vehicle Registration and Licensing System is a multi-role web application that simulates a government-style digital portal for vehicle and licensing management. It supports three distinct user roles — Admin, Officer, and User — each with tailored dashboards and permissions.

The application is built with Python and Streamlit for the web interface, MySQL for persistent storage, and uses object-oriented design with a clear separation of concerns across dedicated modules.

This was the Python Project for Semester 3.

---

## Features

### User Role
- Register a new vehicle (Gujarat number plate format validation: `GJ01AB1234`)
- Apply for a driving license
- View registered vehicles and license status
- Pay and view traffic challans

### Officer Role
- Search any vehicle by number plate
- Issue traffic challans to registered vehicles
- View all challans with vehicle and owner details

### Admin Role
- Add, update, and delete officer accounts
- View system-wide reports and statistics:
  - Total users, officers, vehicles
  - License approvals and pending counts
  - Challan totals and pending amounts
  - Exam pass/fail rates

### Authentication & Security
- Role-based login (Admin / Officer / User)
- Password hashing for all stored credentials
- Email format validation using regex
- Password strength validation (minimum 6 characters)
- Random unique ID generation for users, officers, and vehicles (`USR`, `OFF`, `VEH` prefixes)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Web Framework | Streamlit |
| Language | Python 3.x |
| Database | MySQL |
| DB Connector | mysql-connector-python |
| OOP Architecture | Python classes (Person, Admin, Officer, User) |
| Utilities | Pandas, NumPy (data processing and display) |
| Validation | re (regex), datetime |

---

## Project Structure

```
Smart-vehicle-registration-and-licensing/
├── app.py          # Streamlit application entry point and UI routing
├── auth.py         # Authentication logic and login handling
├── models.py       # OOP classes: Person (base), Admin, Officer, User
│                   # All database operations are methods on these classes
├── db_config.py    # MySQL connection configuration and connect_db() function
├── utils.py        # Helper functions: ID generation, email/password/plate validation
└── data.db         # SQLite file (legacy; active app uses MySQL)
```

---

## Database Schema

The application connects to a MySQL database named `echallan_system`. Key tables:

| Table | Description |
|-------|-------------|
| `users` | Registered vehicle owners (user_id, name, email, hashed password) |
| `officers` | Traffic officers (officer_id, name, email, hashed password) |
| `vehicles` | Registered vehicles (vehicle_id, number_plate, model, type, owner_id) |
| `licenses` | License applications (license_id, user_id, status: pending/approved) |
| `challans` | Traffic fines (challan_id, vehicle_id, reason, amount, date, status) |
| `exams` | Driving test results (exam_id, user_id, result: pass/fail) |

---

## How to Run

### Prerequisites
- Python 3.x
- MySQL Server running locally
- Database `echallan_system` created

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/VedPatel41/Smart-vehicle-registration-and-licensing.git
cd Smart-vehicle-registration-and-licensing

# 2. Install required packages
pip install streamlit mysql-connector-python pandas numpy

# 3. Configure MySQL connection
# Edit db_config.py and set your MySQL credentials:
# DB_CONFIG = {
#     'host': 'localhost',
#     'database': 'echallan_system',
#     'user': 'root',
#     'password': 'your_password',
#     'port': 3306
# }

# 4. Create the database and tables in MySQL
# Run the SQL schema setup in your MySQL client

# 5. Launch the Streamlit application
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## Architecture Notes

- All database operations are implemented as methods on OOP classes in `models.py`
- `Person` is the abstract base class; `Admin`, `Officer`, and `User` extend it
- `db_config.py` provides the `connect_db()` function used by all model methods
- `utils.py` provides stateless helper functions (validation, ID generation, date utilities)
- `auth.py` handles the login/authentication flow for all three roles
- Gujarat number plate format is validated with regex: `^GJ\d{1,2}[A-Z]{1,2}\d{4}$`

---

## Author

**Ved Patel** — B.Tech Computer Engineering Student  
[GitHub](https://github.com/VedPatel41) · [LinkedIn](https://www.linkedin.com/in/ved-patel-0bb446376)
