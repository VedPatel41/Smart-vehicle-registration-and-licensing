from db_config import connect_db
from utils import (
    generate_random_id,
    get_future_date,
    format_date,
    validate_password,
    validate_gujarat_plate,
    validate_email
)

from datetime import datetime
from auth import hash_password


# ==========================================
# BASE CLASS
# ==========================================
class Person:
    def __init__(self, person_id):
        self.person_id = person_id

    def get_connection(self):
        return connect_db()


# ==========================================
# USER CLASS
# ==========================================
class User(Person):

    def apply_license(self):
        """Streamlit version of apply_driving_license"""
        connection = self.get_connection()

        if not connection:
            return None, "Database connection failed!"
        
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT license_id, status FROM licenses WHERE user_id = %s AND status IN ('pending', 'approved')",
                (self.person_id,)
            )
            existing = cursor.fetchone()
            
            if existing:
                return None, f"You already have a license application (Status: {existing[1]})"
            
            license_id = generate_random_id('LIC')
            expiry_date = get_future_date(5)
            
            cursor.execute(
                "INSERT INTO licenses (license_id, user_id, status, expiry_date) VALUES (%s, %s, 'pending', %s)",
                (license_id, self.person_id, expiry_date)
            )
            connection.commit()
            return license_id, f"License application submitted! License ID: {license_id}"
            
        except Exception as e:
            return None, f"Error: {e}"
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def give_license_exam(self, score, total):
        connection = self.get_connection()
        if not connection:
            return None, "Database connection failed!"

        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT license_id FROM licenses WHERE user_id = %s AND status = 'pending'",
                (self.person_id,)
            )


            result = 'pass' if score >= 7 else 'fail'
            exam_id = generate_random_id('EXM')

            cursor.execute(
                "INSERT INTO exams (exam_id, user_id, score, total_questions, result) VALUES (%s, %s, %s, %s, %s)",
                (exam_id, self.person_id, score, total, result)
            )

            connection.commit()

            if result == 'pass':
                return True, f"Congratulations! You passed! Score: {score}/{total}"
            else:
                return False, f"You failed. Score: {score}/{total}. Need 7/10 to pass."

        except Exception as e:
            return None, f"Error: {e}"

        finally:
            cursor.close()
            connection.close()

    def view_my_challans(self):
        """Streamlit version of view_my_challans"""
        connection = self.get_connection()

        if not connection:
            return None, "Database connection failed!"
        
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT vehicle_id, number_plate FROM vehicles WHERE owner_id = %s", (self.person_id,))
            vehicles = cursor.fetchall()
            
            if not vehicles:
                return [], "No vehicles found. You have no challans."
            
            vehicle_ids = [v[0] for v in vehicles]
            placeholders = ','.join(['%s'] * len(vehicle_ids))
            query = f"""
                SELECT c.challan_id, v.number_plate, c.reason, c.amount, c.date, c.status
                FROM challans c
                JOIN vehicles v ON c.vehicle_id = v.vehicle_id
                WHERE c.vehicle_id IN ({placeholders})
                ORDER BY c.date DESC
            """
            cursor.execute(query, tuple(vehicle_ids))
            challans = cursor.fetchall()
            
            if not challans:
                return [], "No challans found. You have a clean record!"
            
            return challans, None
            
        except Exception as e:
            return None, f"Error: {e}"
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def renew_license(self):
        """Streamlit version of renew_license"""
        connection = self.get_connection()

        if not connection:
            return False, "Database connection failed!"
        
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT license_id, status, expiry_date FROM licenses WHERE user_id = %s ORDER BY applied_at DESC LIMIT 1",
                (self.person_id,)
            )
            license_data = cursor.fetchone()
            
            if not license_data:
                return False, "No license found. Please apply for a new license first."
            
            license_id, status, expiry_date = license_data
            
            if status == 'pending':
                return False, "Your license application is still pending approval."
            
            if status == 'approved':
                new_expiry = get_future_date(5)
                cursor.execute(
                    "UPDATE licenses SET expiry_date = %s, status = 'approved' WHERE license_id = %s",
                    (new_expiry, license_id)
                )
                connection.commit()
                return True, f"License renewed successfully! New expiry date: {format_date(new_expiry)}"
            else:
                return False, "Cannot renew license with current status."
                
        except Exception as e:
            return False, f"Error: {e}"
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()




    def renew_insurance(self, vehicle_id):
        """Streamlit version of renew_insurance"""
        connection = self.get_connection()

        if not connection:
            return False, "Database connection failed!"
        
        try:
            cursor = connection.cursor()
            new_expiry = get_future_date(1)
            insurance_id = generate_random_id('INS')
            
            cursor.execute(
                "INSERT INTO insurance (insurance_id, vehicle_id, expiry_date) VALUES (%s, %s, %s)",
                (insurance_id, vehicle_id, new_expiry)
            )
            connection.commit()
            return True, f"Insurance renewed successfully! Insurance ID: {insurance_id}, Expiry: {format_date(new_expiry)}"
            
        except Exception as e:
            return False, f"Error: {e}"
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()


    def search_my_vehicle(self):
        """Streamlit version of search_my_vehicle"""
        connection = self.get_connection()

        if not connection:
            return None, "Database connection failed!"
        
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT vehicle_id, number_plate, model, type, registered_at FROM vehicles WHERE owner_id = %s",
                (self.person_id,)
            )
            vehicles = cursor.fetchall()
            
            if not vehicles:
                return [], "No vehicles found."
            
            return vehicles, None
            
        except Exception as e:
            return None, f"Error: {e}"
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def pay_challan(self, challan_id):
        connection = self.get_connection()

        if not connection:
            return False, "Database connection failed!"

        try:
            cursor = connection.cursor()

            # Check if challan belongs to this user and is pending
            cursor.execute("""
                SELECT c.challan_id
                FROM challans c
                JOIN vehicles v ON c.vehicle_id = v.vehicle_id
                WHERE c.challan_id = %s
                AND v.owner_id = %s
                AND c.status = 'pending'
            """, (challan_id, self.person_id))

            challan = cursor.fetchone()

            if not challan:
                return False, "Invalid challan ID or already paid!"

            # Update status
            cursor.execute(
                "UPDATE challans SET status = 'paid' WHERE challan_id = %s",
                (challan_id,)
            )

            connection.commit()

            return True, f"Challan {challan_id} paid successfully!"

        except Exception as e:
            return False, f"Error: {e}"

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()



# ==========================================
# OFFICER CLASS
# ==========================================
class Officer(Person):

    def register_vehicle(self, owner_id, number_plate, model, vehicle_type):
        """Streamlit version of register_vehicle"""
        connection = self.get_connection()

        if not connection:
            return False, "Database connection failed!"
        cursor=None
        try:
            if not validate_gujarat_plate(number_plate):
                return False, "Invalid vehicle number plate. Only Gujarat (GJ) format is allowed."
            cursor = connection.cursor()
            cursor.execute("SELECT name FROM users WHERE user_id = %s", (owner_id,))
            owner = cursor.fetchone()
            if not owner:
                return False, "User not found!"
            
            cursor.execute("SELECT vehicle_id FROM vehicles WHERE number_plate = %s", (number_plate,))
            if cursor.fetchone():
                return False, "Vehicle with this number plate already exists!"
            
            vehicle_id = generate_random_id('VEH')
            cursor.execute(
                "INSERT INTO vehicles (vehicle_id, owner_id, number_plate, model, type) VALUES (%s, %s, %s, %s, %s)",
                (vehicle_id, owner_id, number_plate, model, vehicle_type)
            )
            connection.commit()
            return True, f"Vehicle registered! Vehicle ID: {vehicle_id}"
            
        except Exception as e:
            return False, f"Error: {e}"
        finally:
            if cursor is not None:
                cursor.close()
            if connection.is_connected():
                connection.close()

    def approve_license(self, license_id):
        """Streamlit version of approve_license"""
        connection = self.get_connection()

        if not connection:
            return False, "Database connection failed!"
        
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT license_id, user_id FROM licenses WHERE license_id = %s AND status = 'pending'", (license_id,))
            license_data = cursor.fetchone()
            
            if not license_data:
                return False, "Invalid license ID or already processed!"
            
            lic_id, user_id = license_data
            cursor.execute("SELECT result FROM exams WHERE user_id = %s ORDER BY exam_date DESC LIMIT 1", (user_id,))
            exam_result = cursor.fetchone()
            
            if not exam_result or exam_result[0] != 'pass':
                return False, "User must pass the driving exam first!"
            
            cursor.execute("UPDATE licenses SET status = 'approved' WHERE license_id = %s", (lic_id,))
            connection.commit()
            return True, f"License {lic_id} approved successfully!"
            
        except Exception as e:
            return False, f"Error: {e}"
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()


    def reject_license(self, license_id):
        """Streamlit version of reject_license"""
        connection = self.get_connection()

        if not connection:
            return False, "Database connection failed!"
        
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT license_id FROM licenses WHERE license_id = %s AND status = 'pending'", (license_id,))
            if not cursor.fetchone():
                return False, "Invalid license ID or already processed!"
            
            cursor.execute("UPDATE licenses SET status = 'rejected' WHERE license_id = %s", (license_id,))
            connection.commit()
            return True, f"License {license_id} rejected."
            
        except Exception as e:
            return False, f"Error: {e}"
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    def generate_challan(self, number_plate, reason, amount):
        """Streamlit version of generate_challan"""
        connection = self.get_connection()

        if not connection:
            return None, "Database connection failed!"
        
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT vehicle_id, owner_id FROM vehicles WHERE number_plate = %s", (number_plate,))
            vehicle_data = cursor.fetchone()
            
            if not vehicle_data:
                return None, "Vehicle not found!"
            
            vehicle_id, owner_id = vehicle_data
            challan_id = generate_random_id('CHL')
            challan_date = datetime.now().date()
            
            cursor.execute(
                "INSERT INTO challans (challan_id, vehicle_id, officer_id, reason, amount, date) VALUES (%s, %s, %s, %s, %s, %s)",
                (challan_id, vehicle_id, self.person_id, reason, amount, challan_date)
            )
            connection.commit()
            return challan_id, f"E-Challan generated! Challan ID: {challan_id}"
            
        except Exception as e:
            return None, f"Error: {e}"
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def view_all_challans(self):
        """Streamlit version of view_all_challans"""
        connection = self.get_connection()

        if not connection:
            return None, "Database connection failed!"
        
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT c.challan_id, v.number_plate, u.name, c.reason, c.amount, c.date, c.status
                FROM challans c
                JOIN vehicles v ON c.vehicle_id = v.vehicle_id
                JOIN users u ON v.owner_id = u.user_id
                ORDER BY c.date DESC
            """)
            challans = cursor.fetchall()
            return challans, None
            
        except Exception as e:
            return None, f"Error: {e}"
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()


    def search_vehicle(self, number_plate):
        """Streamlit version of search_vehicle"""
        connection = self.get_connection()

        if not connection:
            return None, "Database connection failed!"
        
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT v.vehicle_id, v.number_plate, v.model, v.type, u.name, u.email, v.registered_at
                FROM vehicles v
                JOIN users u ON v.owner_id = u.user_id
                WHERE v.number_plate = %s
            """, (number_plate,))
            
            vehicle_data = cursor.fetchone()
            if not vehicle_data:
                return None, "Vehicle not found!"
            
            return vehicle_data, None
            
        except Exception as e:
            return None, f"Error: {e}"
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    

# ==========================================
# ADMIN CLASS
# ==========================================
class Admin(Person):

    def add_officer(self, name, email, password):

        if not name:
            return False, "Name cannot be empty!"

        if not validate_email(email):
            return False, "Invalid email format!"

        if not validate_password(password):
            return False, "Password must be at least 6 characters!"

        connection = self.get_connection()

        if not connection:
            return False, "Database connection failed!"

        try:
            cursor = connection.cursor()

            cursor.execute("SELECT officer_id FROM officers WHERE email = %s", (email,))
            if cursor.fetchone():
                return False, "Email already registered!"

            officer_id = generate_random_id('OFF')
            hashed_password = hash_password(password)

            cursor.execute(
                "INSERT INTO officers (officer_id, name, email, password) VALUES (%s, %s, %s, %s)",
                (officer_id, name, email, hashed_password)
            )

            connection.commit()
            return True, f"Officer added! Officer ID: {officer_id}"

        except Exception as e:
            return False, f"Error: {e}"

        finally:
            cursor.close()
            connection.close()


    
    def update_officer(self,officer_id, name, email, password=None):
        """Streamlit version of update_officer"""
        connection = self.get_connection()

        if not connection:
            return False, "Database connection failed!"
        
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT name, email FROM officers WHERE officer_id = %s", (officer_id,))
            if not cursor.fetchone():
                return False, "Officer not found!"
            
            if password:
                if not validate_password(password):
                    return False, "Password must be at least 6 characters!"
                hashed_password = hash_password(password)
                cursor.execute(
                    "UPDATE officers SET name = %s, email = %s, password = %s WHERE officer_id = %s",
                    (name, email, hashed_password, officer_id)
                )
            else:
                cursor.execute(
                    "UPDATE officers SET name = %s, email = %s WHERE officer_id = %s",
                    (name, email, officer_id)
                )
            
            connection.commit()
            return True, "Officer updated successfully!"
            
        except Exception as e:
            return False, f"Error: {e}"
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()


    def delete_officer(self,officer_id):
        """Streamlit version of delete_officer"""
        connection = self.get_connection()

        if not connection:
            return False, "Database connection failed!"
        
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT name, email FROM officers WHERE officer_id = %s", (officer_id,))
            officer_data = cursor.fetchone()
            
            if not officer_data:
                return False, "Officer not found!"
            
            cursor.execute("DELETE FROM officers WHERE officer_id = %s", (officer_id,))
            connection.commit()
            return True, "Officer deleted successfully!"
            
        except Exception as e:
            return False, f"Error: {e}"
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()


    def view_reports(self):
        """Streamlit version of view_reports"""
        connection = self.get_connection()

        if not connection:
            return None, "Database connection failed!"
        
        try:
            cursor = connection.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM officers")
            total_officers = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM vehicles")
            total_vehicles = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM licenses")
            total_licenses = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM licenses WHERE status = 'approved'")
            approved_licenses = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM licenses WHERE status = 'pending'")
            pending_licenses = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM challans")
            total_challans = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM challans WHERE status = 'pending'")
            pending_challans = cursor.fetchone()[0]
            cursor.execute("SELECT SUM(amount) FROM challans")
            total_amount = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM exams")
            total_exams = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM exams WHERE result = 'pass'")
            passed_exams = cursor.fetchone()[0]
            
            stats = {
                'users': total_users,
                'officers': total_officers,
                'vehicles': total_vehicles,
                'licenses': {'total': total_licenses, 'approved': approved_licenses, 'pending': pending_licenses},
                'challans': {'total': total_challans, 'pending': pending_challans, 'amount': total_amount},
                'exams': {'total': total_exams, 'passed': passed_exams, 'failed': total_exams - passed_exams}
            }
            
            return stats, None
            
        except Exception as e:
            return None, f"Error: {e}"
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
