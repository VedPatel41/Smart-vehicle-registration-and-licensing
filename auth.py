"""
Authentication Module
Handles user registration and login for all roles
"""

from db_config import connect_db
from utils import generate_random_id, validate_email, validate_password
import hashlib

# ============================================================================
# HELPER FUNCTIONS (Streamlit versions of auth functions)
# ============================================================================

def register_user_streamlit(name, email, password):
    """Streamlit version of register_user"""
    if not name:
        return None, "Name cannot be empty!"
    
    if not validate_email(email):
        return None, "Invalid email format!"
    
    if not validate_password(password):
        return None, "Password must be at least 6 characters!"
    
    connection = connect_db()
    if not connection:
        return None, "Database connection failed!"
    
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT email FROM users WHERE email = %s UNION SELECT email FROM officers WHERE email = %s""", (email, email))
        if cursor.fetchone():
            return None, "Email already registered!"
        
        user_id = generate_random_id('USR')
        hashed_password = hash_password(password)
        
        cursor.execute(
            "INSERT INTO users (user_id, name, email, password) VALUES (%s, %s, %s, %s)",
            (user_id, name, email, hashed_password)
        )
        connection.commit()
        return user_id, f"Registration successful! Your User ID: {user_id}"
        
    except Exception as e:
        return None, f"Error: {e}"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def login_user_streamlit(email, password):
    """Streamlit version of login_user"""
    connection = connect_db()
    if not connection:
        return None, "Database connection failed!"
    
    try:
        cursor = connection.cursor()
        hashed_password = hash_password(password)
        
        cursor.execute(
            "SELECT user_id, name FROM users WHERE email = %s AND password = %s",
            (email, hashed_password)
        )
        result = cursor.fetchone()
        
        if result:
            user_id, name = result
            return user_id, f"Welcome {name}!"
        else:
            return None, "Invalid email or password!"
            
    except Exception as e:
        return None, f"Error: {e}"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def login_officer_streamlit(email, password):
    """Streamlit version of login_officer"""
    connection = connect_db()
    if not connection:
        return None, "Database connection failed!"
    
    try:
        cursor = connection.cursor()
        hashed_password = hash_password(password)
        
        cursor.execute(
            "SELECT officer_id, name FROM officers WHERE email = %s AND password = %s",
            (email, hashed_password)
        )
        result = cursor.fetchone()
        
        if result:
            officer_id, name = result
            return officer_id, f"Welcome Officer {name}!"
        else:
            return None, "Invalid email or password!"
            
    except Exception as e:
        return None, f"Error: {e}"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def register_admin_streamlit(name, email, password,admin_key1):
    """Streamlit version of register_admin"""
    # 🔐 Special Admin Passkey Check
    if admin_key1 != "Admin@123":
        return False, "Invalid Admin Pass Key!"

    if not name:
        return False, "Name cannot be empty!"
    
    if not validate_email(email):
        return False, "Invalid email format!"
    
    if not validate_password(password):
        return False, "Password must be at least 6 characters!"
    
    connection = connect_db()
    if not connection:
        return False, "Database connection failed!"
    
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT email FROM users WHERE email = %s UNION SELECT email FROM officers WHERE email = %s""", (email, email))
        if cursor.fetchone():
            return False, "Email already registered!"
        
        admin_id = generate_random_id('ADM')
        hashed_password = hash_password(password)
        
        cursor.execute(
            "INSERT INTO officers (officer_id, name, email, password) VALUES (%s, %s, %s, %s)",
            (admin_id, name, email, hashed_password)
        )
        connection.commit()
        return True, f"Registration successful! Your Admin ID: {admin_id}"
        
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def login_admin_streamlit(email, password):
    """Streamlit version of login_admin"""
    connection = connect_db()
    if not connection:
        return False, "Database connection failed!"
    
    try:
        cursor = connection.cursor()
        hashed_password = hash_password(password)
        
        cursor.execute(
            "SELECT officer_id, name FROM officers WHERE email = %s AND password = %s",
            (email, hashed_password)
        )
        result = cursor.fetchone()
        
        if result:
            officer_id, name = result
            return True, f"Welcome Admin {name}!"
        else:
            return False, "Invalid email or password!"
            
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def hash_password(password):
    """
    Simple password hashing (for demonstration)
    In production, use bcrypt or similar
    Args:
        password: Plain text password
    Returns: Hashed password
    """
    return hashlib.md5(password.encode()).hexdigest()


