"""
Database Configuration Module
Contains database connection settings and connection function
"""

import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host': 'localhost',
    'database': 'echallan_system',
    'user': 'root',
    'password': '',    
    'port': 3306       
}

def connect_db():
    """
    Establishes connection to MySQL database
    Returns: Database connection object or None if connection fails
    """
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            port=DB_CONFIG['port']
        )

        if connection.is_connected():
            return connection
        else:
            print("MySQL connection created but not connected")
            return None

    except Error as e:
        print("Error connecting to MySQL:", e)
        return None
