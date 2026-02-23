"""
Smart Vehicle Registration And Licensing System
"""
import matplotlib.pyplot as plt
import streamlit as st
import sys
from db_config import connect_db
from utils import generate_random_id, get_future_date, format_date, validate_email, validate_password , validate_gujarat_plate
from auth import hash_password,register_user_streamlit,register_admin_streamlit,login_user_streamlit,login_officer_streamlit,login_admin_streamlit
from datetime import datetime
import pandas as pd
from models import User, Officer,Admin

st.set_page_config(
    page_title="E-Challan System",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'officer_id' not in st.session_state:
    st.session_state.officer_id = None
if 'admin_id' not in st.session_state:
    st.session_state.admin_id = None
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False
if 'role' not in st.session_state:
    st.session_state.role = None
if 'page' not in st.session_state:
    st.session_state.page = 'main'



def main_page():
    """Main page - Role selection"""
    st.title("Smart Vehicle Registration And Licensing")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("👤 User", use_container_width=True, type="primary"):
            st.session_state.page = 'user_role'
            st.rerun()
    
    with col2:
        if st.button("👮 Officer", use_container_width=True, type="primary"):
            st.session_state.page = 'officer_role'
            st.rerun()
    
    with col3:
        if st.button("👑 Admin", use_container_width=True, type="primary"):
            st.session_state.page = 'admin_role'
            st.rerun()


def user_role_page():
    """User role - Register/Login"""
    st.title("👤 User Portal")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["Register", "Login"])
    
    with tab1:
        st.subheader("User Registration")
        name = st.text_input("Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        
        if st.button("Register"):
            user_id, message = register_user_streamlit(name, email, password)
            if user_id:
                st.success(message)
                st.session_state.user_id = user_id
                st.session_state.role = 'user'
                st.session_state.page = 'user_menu'
                st.rerun()
            else:
                st.error(message)
    
    with tab2:
        st.subheader("User Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login"):
            user_id, message = login_user_streamlit(email, password)
            if user_id:
                st.success(message)
                st.session_state.user_id = user_id
                st.session_state.role = 'user'
                st.session_state.page = 'user_menu'
                st.rerun()
            else:
                st.error(message)
    
    if st.button("← Back to Main Menu"):
        st.session_state.page = 'main'
        st.rerun()


def user_menu_page():
    """User menu page"""
    st.title("👤 User Menu")
    st.markdown("---")
    
    menu_option = st.selectbox(
        "Select an option:",
        ["Apply for Driving License", "Give Driving License Exam", "View My Challans","Pay Challan",
         "Renew License", "Renew Insurance", "Search My Vehicle"]
    )
    
    if menu_option == "Apply for Driving License":
        if st.button("Apply"):
            user = User(st.session_state.user_id)
            license_id, message = user.apply_license()
            if license_id:
                st.success(message)
            else:
                st.error(message)
    
        elif menu_option == "Give Driving License Exam":

            questions = [
                {"q": "What is the minimum age for driving a car in India?", "options": ["A) 16 years", "B) 18 years", "C) 21 years", "D) 25 years"], "correct": "B"},
                {"q": "What does a red traffic light mean?", "options": ["A) Stop", "B) Go", "C) Slow down", "D) Proceed with caution"], "correct": "A"},
                {"q": "What is the speed limit in residential areas?", "options": ["A) 40 km/h", "B) 50 km/h", "C) 60 km/h", "D) 70 km/h"], "correct": "A"},
                {"q": "When should you use headlights?", "options": ["A) Only at night", "B) Only in fog", "C) At night and in poor visibility", "D) Never"], "correct": "C"},
                {"q": "What does a yellow traffic light mean?", "options": ["A) Stop", "B) Go", "C) Slow down and prepare to stop", "D) Speed up"], "correct": "C"},
                {"q": "What is the penalty for drunk driving?", "options": ["A) Fine only", "B) License suspension", "C) Both fine and license suspension", "D) No penalty"], "correct": "C"},
                {"q": "What should you do at a stop sign?", "options": ["A) Slow down", "B) Come to complete stop", "C) Honk and proceed", "D) Ignore it"], "correct": "B"},
                {"q": "What is the safe following distance?", "options": ["A) 1 second", "B) 2 seconds", "C) 3 seconds", "D) 5 seconds"], "correct": "C"},
                {"q": "When should you wear a seatbelt?", "options": ["A) Only on highways", "B) Only in cities", "C) Always", "D) Never"], "correct": "C"},
                {"q": "What does a green arrow signal mean?", "options": ["A) Stop", "B) Proceed in the direction of arrow", "C) Wait", "D) U-turn allowed"], "correct": "B"}
            ]

            if 'exam_current_q' not in st.session_state:
                st.session_state.exam_current_q = 0
                st.session_state.exam_score = 0

            if st.session_state.exam_current_q < len(questions):

                q = questions[st.session_state.exam_current_q]

                st.subheader(f"Question {st.session_state.exam_current_q + 1}/10")
                st.write(q["q"])

                answer = st.radio("Select your answer:", q["options"])

                if st.button("Next Question"):

                    selected = answer.split(')')[0]

                    if selected == q["correct"]:
                        st.session_state.exam_score += 1

                    st.session_state.exam_current_q += 1
                    st.rerun()

            else:
                # Exam Finished
                score = st.session_state.exam_score
                total = len(questions)

                user = User(st.session_state.user_id)
                result, message = user.give_license_exam(score, total)

                # Reset session
                del st.session_state.exam_current_q
                del st.session_state.exam_score

                if result:
                    st.success(message)
                else:
                    st.error(message)

    
    elif menu_option == "View My Challans":
        user = User(st.session_state.user_id)
        challans, error = user.view_my_challans()

        if error:
            st.info(error)
        elif challans:
            df = pd.DataFrame(challans, columns=['Challan ID', 'Vehicle', 'Reason', 'Amount', 'Date', 'Status'])
            st.dataframe(df, use_container_width=True)
            total = sum(c[3] for c in challans if c[5] == 'pending')
            st.info(f"Total Pending Amount: ₹{total:.2f}")
    
    elif menu_option == "Renew License":
        if st.button("Renew"):
            user = User(st.session_state.user_id)
            success, message = user.renew_license()
            if success:
                st.success(message)
            else:
                st.error(message)
    
    elif menu_option == "Renew Insurance":
        user = User(st.session_state.user_id)
        vehicles, error = user.search_my_vehicle()
        if error:
            st.error(error)
        elif vehicles:
            vehicle_options = {f"{v[1]} - {v[2]}": v[0] for v in vehicles}
            selected = st.selectbox("Select Vehicle:", list(vehicle_options.keys()))
            if st.button("Renew Insurance"):
                vehicle_id = vehicle_options[selected]
                user = User(st.session_state.user_id)
                success, message = user.renew_insurance(vehicle_id)
                if success:
                    st.success(message)
                else:
                    st.error(message)

    elif menu_option == "Pay Challan":

        user = User(st.session_state.user_id)
        challans, error = user.view_my_challans()

        if error:
            st.info(error)

        elif challans:
            pending = [c for c in challans if c[5] == 'pending']

            if not pending:
                st.success("No pending challans 🎉")
            else:
                challan_options = {
                    f"{c[0]} - ₹{c[3]} - {c[2]}": c[0] for c in pending
                }

                selected = st.selectbox("Select Challan to Pay:", list(challan_options.keys()))

                if st.button("Pay Now"):
                    challan_id = challan_options[selected]
                    success, message = user.pay_challan(challan_id)

                    if success:
                        st.success(message)
                    else:
                        st.error(message)

    
    elif menu_option == "Search My Vehicle":
        user = User(st.session_state.user_id)
        vehicles, error = user.search_my_vehicle()
        if error:
            st.info(error)
        elif vehicles:
            df = pd.DataFrame(vehicles, columns=['Vehicle ID', 'Number Plate', 'Model', 'Type', 'Registered Date'])
            st.dataframe(df, use_container_width=True)
    
    st.markdown("---")
    if st.button("Logout"):
        st.session_state.user_id = None
        st.session_state.role = None
        st.session_state.page = 'main'
        st.rerun()


def officer_role_page():
    """Officer role - Login only"""
    st.title("👮 Officer Portal")
    st.markdown("---")

    tab_login = st.tabs(["Login"])[0]

    with tab_login:
        st.subheader("Officer Login")
        email = st.text_input("Email", key="off_login_email")
        password = st.text_input("Password", type="password", key="off_login_pass")

        if st.button("Login"):
            officer_id, message = login_officer_streamlit(email, password)
            if officer_id:
                st.success(message)
                st.session_state.officer_id = officer_id
                st.session_state.role = 'officer'
                st.session_state.page = 'officer_menu'
                st.rerun()
            else:
                st.error(message)

    if st.button("← Back to Main Menu"):
        st.session_state.page = 'main'
        st.rerun()



def officer_menu_page():
    """Officer menu page"""
    st.title("👮 Officer Menu")
    st.markdown("---")
    
    menu_option = st.selectbox(
        "Select an option:",
        ["Register New Vehicle", "Approve Driving License", "Reject Driving License",
         "Generate E-Challan", "View All Challans", "Search Vehicle"]
    )
    
    if menu_option == "Register New Vehicle":
        owner_id = st.text_input("Owner User ID")
        number_plate = st.text_input("Vehicle Number Plate").strip().upper()
        model = st.text_input("Vehicle Model")
        vehicle_type = st.text_input("Vehicle Type (Car/Bike/Truck/etc)")
        
        if st.button("Register Vehicle"):
            officer = Officer(st.session_state.officer_id)
            success, message = officer.register_vehicle(
                owner_id, number_plate, model, vehicle_type
            )
            if success:
                st.success(message)
            else:
                st.error(message)
    
    elif menu_option == "Approve Driving License":
        connection = connect_db()
        if connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT l.license_id, u.name, l.applied_at
                FROM licenses l
                JOIN users u ON l.user_id = u.user_id
                WHERE l.status = 'pending'
                ORDER BY l.applied_at
            """)
            pending = cursor.fetchall()
            if pending:
                license_options = {f"{p[0]} - {p[1]}": p[0] for p in pending}
                selected = st.selectbox("Select License to Approve:", list(license_options.keys()))
                if st.button("Approve"):
                    license_id = license_options[selected]
                    officer = Officer(st.session_state.officer_id)
                    success, message = officer.approve_license(license_id)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.info("No pending license applications.")
            connection.close()
    
    elif menu_option == "Reject Driving License":
        connection = connect_db()
        if connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT l.license_id, u.name, l.applied_at
                FROM licenses l
                JOIN users u ON l.user_id = u.user_id
                WHERE l.status = 'pending'
                ORDER BY l.applied_at
            """)
            pending = cursor.fetchall()
            if pending:
                license_options = {f"{p[0]} - {p[1]}": p[0] for p in pending}
                selected = st.selectbox("Select License to Reject:", list(license_options.keys()))
                if st.button("Reject"):
                    license_id = license_options[selected]
                    officer = Officer(st.session_state.officer_id)
                    success, message = officer.reject_license(license_id)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.info("No pending license applications.")
            connection.close()
    
    elif menu_option == "Generate E-Challan":
        number_plate = st.text_input("Vehicle Number Plate").upper()
        reason = st.text_input("Violation Reason")
        amount = st.number_input("Challan Amount (₹)", min_value=0.0, step=100.0)
        
        if st.button("Generate Challan"):
            officer = Officer(st.session_state.officer_id)
            challan_id, message = officer.generate_challan(number_plate, reason, amount)

            if challan_id:
                st.success(message)
            else:
                st.error(message)
    
    elif menu_option == "View All Challans":
        officer = Officer(st.session_state.officer_id)
        challans, error = officer.view_all_challans()
        if error:
            st.info(error)
        elif challans:
            df = pd.DataFrame(challans, columns=['Challan ID', 'Vehicle', 'Owner', 'Reason', 'Amount', 'Date', 'Status'])
            st.dataframe(df, use_container_width=True)
            total = sum(c[4] for c in challans)
            st.info(f"Total Amount: ₹{total:.2f}")
    
    elif menu_option == "Search Vehicle":
        number_plate = st.text_input("Vehicle Number Plate").upper()
        if st.button("Search"):
            officer = Officer(st.session_state.officer_id)
            vehicle_data, error = officer.search_vehicle(number_plate)
            if error:
                st.error(error)
            elif vehicle_data:
                st.subheader("Vehicle Details")
                st.write(f"**Vehicle ID:** {vehicle_data[0]}")
                st.write(f"**Number Plate:** {vehicle_data[1]}")
                st.write(f"**Model:** {vehicle_data[2]}")
                st.write(f"**Type:** {vehicle_data[3]}")
                st.write(f"**Owner Name:** {vehicle_data[4]}")
                st.write(f"**Owner Email:** {vehicle_data[5]}")
                st.write(f"**Registered Date:** {format_date(str(vehicle_data[6]))}")
    
    st.markdown("---")
    if st.button("Logout"):
        st.session_state.officer_id = None
        st.session_state.role = None
        st.session_state.page = 'main'
        st.rerun()


def admin_role_page():
    """Admin role - Register/Login"""
    st.title("👑 Admin Portal")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["Register", "Login"])
    
    with tab1:
        st.subheader("Admin Registration")
        name = st.text_input("Name", key="adm_reg_name")
        email = st.text_input("Email", key="adm_reg_email")
        password = st.text_input("Password", type="password", key="adm_reg_pass")
        admin_key1 = st.text_input("Admin Pass Key", type="password", key="adm_key")

        if st.button("Register"):
            success, message = register_admin_streamlit(name, email, password,admin_key1)

            if success:
                st.success(message)
                st.session_state.admin_logged_in = True
                st.session_state.role = 'admin'
                st.session_state.page = 'admin_menu'
                st.session_state.admin_id = "ADMIN"

                st.rerun()
            else:
                st.error(message)
    
    with tab2:
        st.subheader("Admin Login")
        email = st.text_input("Email", key="adm_login_email")
        password = st.text_input("Password", type="password", key="adm_login_pass")
        
        if st.button("Login"):
            success, message = login_admin_streamlit(email, password)

            if success:
                st.success(message)
                st.session_state.admin_logged_in = True
                st.session_state.role = 'admin'
                st.session_state.page = 'admin_menu'
                st.session_state.admin_id = "ADMIN"  # any placeholder

                st.rerun()
            else:
                st.error(message)
    
    if st.button("← Back to Main Menu"):
        st.session_state.page = 'main'
        st.rerun()


def admin_menu_page():
    """Admin menu page"""
    st.title("👑 Admin Menu")
    st.markdown("---")
    
    menu_option = st.selectbox(
        "Select an option:",
        ["Add Officer", "Update Officer", "Delete Officer", "View Reports"]
    )
    
    if menu_option == "Add Officer":
        name = st.text_input("Officer Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        admin_key = st.text_input("Admin Pass Key", type="password")

        if st.button("Add Officer"):

            # 🔒 Check admin logged in
            if st.session_state.role != 'admin':
                st.error("Unauthorized: Only admin can add officers.")
            elif admin_key != "Admin@123":
                st.error("Invalid Admin Pass Key.")
            else:
                admin = Admin(st.session_state.admin_id)
                success, message = admin.add_officer(name, email, password)

                if success:
                    st.success(message)
                else:
                    st.error(message)

    
    elif menu_option == "Update Officer":
        officer_id = st.text_input("Officer ID to Update")
        name = st.text_input("New Name")
        email = st.text_input("New Email")
        password = st.text_input("New Password (leave empty to keep current)", type="password")
        
        if st.button("Update Officer"):
            admin = Admin(st.session_state.admin_id)
            success, message = admin.update_officer(
                officer_id, name, email, password if password else None
            )
            if success:
                st.success(message)
            else:
                st.error(message)
    
    elif menu_option == "Delete Officer":
        officer_id = st.text_input("Officer ID to Delete")
        if st.button("Delete Officer", type="primary"):
            admin = Admin(st.session_state.admin_id)
            success, message = admin.delete_officer(officer_id)
            if success:
                st.success(message)
            else:
                st.error(message)
    
    elif menu_option == "View Reports":
        admin = Admin(st.session_state.admin_id)
        stats, error = admin.view_reports()
        if error:
            st.error(error)
        elif stats:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Users", stats['users'])
                st.metric("Total Officers", stats['officers'])
            with col2:
                st.metric("Total Vehicles", stats['vehicles'])
                st.metric("Total Licenses", stats['licenses']['total'])
            with col3:
                st.metric("Total Challans", stats['challans']['total'])
                st.metric("Total Amount", f"₹{stats['challans']['amount']:.2f}")
            
            st.subheader("License Statistics")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Approved", stats['licenses']['approved'])
            with col2:
                st.metric("Pending", stats['licenses']['pending'])
            
            st.subheader("Exam Statistics")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Exams", stats['exams']['total'])
            with col2:
                st.metric("Passed", stats['exams']['passed'])
            with col3:
                st.metric("Failed", stats['exams']['failed'])
            st.subheader("License Distribution")

            #license piechart
            license_labels = ["Approved", "Pending"]
            license_values = [stats['licenses']['approved'],stats['licenses']['pending']]
            fig1, ax1 = plt.subplots()
            ax1.pie(license_values, labels=license_labels, autopct='%1.1f%%')
            ax1.set_title("License Status Distribution")
            st.pyplot(fig1)

            #chalaan barplot
            st.subheader("Challan Overview")
            challan_labels = ["Total Challans", "Pending Challans"]
            challan_values = [stats['challans']['total'],stats['challans']['pending']]
            fig2, ax2 = plt.subplots()
            ax2.bar(challan_labels, challan_values)
            ax2.set_title("Challan Statistics")
            ax2.set_ylabel("Count")
            st.pyplot(fig2)


    st.markdown("---")
    if st.button("Logout"):
        st.session_state.admin_logged_in = False
        st.session_state.role = None
        st.session_state.page = 'main'
        st.rerun()


# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Main Streamlit app"""
    if st.session_state.page == 'main':
        main_page()
    elif st.session_state.page == 'user_role':
        user_role_page()
    elif st.session_state.page == 'user_menu':
        user_menu_page()
    elif st.session_state.page == 'officer_role':
        officer_role_page()
    elif st.session_state.page == 'officer_menu':
        officer_menu_page()
    elif st.session_state.page == 'admin_role':
        admin_role_page()
    elif st.session_state.page == 'admin_menu':
        admin_menu_page()


if __name__ == "__main__":
    main()
