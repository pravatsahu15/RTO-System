import streamlit as st
import pymysql
from pymysql import IntegrityError
import pandas as pd
import time
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import hashlib
import secrets
import re
from typing import Optional, Dict, List
import bcrypt

# --- Page Configuration with Enhanced UI ---
st.set_page_config(
    page_title="🚗 RTO Vehicle Registration System",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🏢"
)

# Enhanced custom CSS with animations and better styling
st.markdown("""
<style>
    /* Main dark theme */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #e2e8f0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Status badges */
    .status-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
        margin: 2px;
    }
    
    .status-approved {
        background: linear-gradient(90deg, #10b981, #34d399);
        color: white;
    }
    
    .status-pending {
        background: linear-gradient(90deg, #f59e0b, #fbbf24);
        color: white;
    }
    
    .status-rejected {
        background: linear-gradient(90deg, #ef4444, #f87171);
        color: white;
    }
    
    .status-verified {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        color: white;
    }
    
    /* Enhanced cards */
    .card {
        background: rgba(30, 41, 59, 0.8);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid;
        backdrop-filter: blur(10px);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
    }
    
    /* Toast notifications */
    .toast-success {
        background: linear-gradient(90deg, #10b981, #34d399) !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
    }
    
    .toast-warning {
        background: linear-gradient(90deg, #f59e0b, #fbbf24) !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
    }
    
    /* Role-specific styling */
    .role-badge {
        padding: 3px 10px;
        border-radius: 15px;
        font-size: 11px;
        font-weight: 600;
        display: inline-block;
        margin-left: 10px;
    }
    
    .role-admin {
        background: linear-gradient(90deg, #8b5cf6, #a78bfa);
        color: white;
    }
    
    .role-user {
        background: linear-gradient(90deg, #3b82f6, #60a5fa);
        color: white;
    }
    
    .role-inspector {
        background: linear-gradient(90deg, #10b981, #34d399);
        color: white;
    }
    
    /* Form styling */
    .required-field::after {
        content: " *";
        color: #ef4444;
    }
    
    /* Animation classes */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideIn {
        from { transform: translateX(-20px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    .slide-in {
        animation: slideIn 0.4s ease-out;
    }
    
    .pulse-animation {
        animation: pulse 2s infinite;
    }
</style>
""", unsafe_allow_html=True)

# --- Database Configuration & Security ---
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "P@sahu15"
DB_NAME = "rto_vehicle_system"

# --- Security Functions ---
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def sanitize_input(text: str) -> str:
    """Basic input sanitization"""
    return re.sub(r'[<>"\']', '', text).strip()

# --- Database Connection & Schema Setup ---
@st.cache_resource
def get_db_connection():
    """Establishes and caches the database connection."""
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        st.stop()

def setup_database_schema():
    """Create all necessary tables with proper schema design."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Users table for authentication and roles
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                email VARCHAR(100),
                phone VARCHAR(15),
                role ENUM('admin', 'user', 'inspector') DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        """)
        
        # Vehicles table with comprehensive details
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vehicles (
                vehicle_id INT AUTO_INCREMENT PRIMARY KEY,
                engine_no VARCHAR(50) UNIQUE NOT NULL,
                chassis_no VARCHAR(50) UNIQUE NOT NULL,
                manufacturer VARCHAR(100) NOT NULL,
                model VARCHAR(100) NOT NULL,
                vehicle_type ENUM('2-wheeler', '3-wheeler', '4-wheeler', 'commercial', 'other') NOT NULL,
                fuel_type ENUM('petrol', 'diesel', 'electric', 'cng', 'hybrid') NOT NULL,
                color VARCHAR(50),
                manufacturing_year YEAR,
                seating_capacity INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Registrations table with status tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS registrations (
                registration_id INT AUTO_INCREMENT PRIMARY KEY,
                reg_no VARCHAR(20) UNIQUE NOT NULL,
                vehicle_id INT,
                owner_id INT,
                state VARCHAR(50) NOT NULL,
                district VARCHAR(50) NOT NULL,
                application_date DATE NOT NULL,
                registration_date DATE,
                status ENUM('pending', 'approved', 'rejected', 'verified') DEFAULT 'pending',
                status_updated_by INT,
                status_updated_at TIMESTAMP,
                remarks TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id),
                FOREIGN KEY (owner_id) REFERENCES users(user_id),
                FOREIGN KEY (status_updated_by) REFERENCES users(user_id)
            )
        """)
        
        # Payment tracking (optional)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                payment_id INT AUTO_INCREMENT PRIMARY KEY,
                registration_id INT,
                amount DECIMAL(10, 2) NOT NULL,
                payment_mode ENUM('online', 'cash', 'cheque') NOT NULL,
                transaction_id VARCHAR(100),
                payment_status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
                payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (registration_id) REFERENCES registrations(registration_id)
            )
        """)
        
        # Audit logs for security
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                log_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                action VARCHAR(100) NOT NULL,
                table_name VARCHAR(50),
                record_id INT,
                old_values TEXT,
                new_values TEXT,
                ip_address VARCHAR(45),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        conn.commit()
        
        # Create default admin user if not exists
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            admin_hash = hash_password("admin@123")
            cursor.execute("""
                INSERT INTO users (username, password_hash, full_name, role) 
                VALUES ('admin', %s, 'System Administrator', 'admin')
            """, (admin_hash,))
            conn.commit()
            
    except Exception as e:
        st.error(f"Error setting up database schema: {e}")
    finally:
        cursor.close()

# Initialize database
conn = get_db_connection()
setup_database_schema()

# --- Session State Management ---
if 'user' not in st.session_state:
    st.session_state.user = None
if 'current_role' not in st.session_state:
    st.session_state.current_role = 'guest'
if 'show_toast' not in st.session_state:
    st.session_state.show_toast = None

def show_toast(message: str, type: str = "success"):
    """Display toast notification"""
    st.session_state.show_toast = (message, type)

# --- Authentication Module ---
def login(username: str, password: str) -> bool:
    """Authenticate user"""
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE username = %s AND is_active = TRUE", (username,))
        user = cursor.fetchone()
        
        if user and verify_password(password, user['password_hash']):
            st.session_state.user = user
            st.session_state.current_role = user['role']
            show_toast(f"Welcome back, {user['full_name']}!", "success")
            return True
        return False
    finally:
        cursor.close()

def logout():
    """Logout current user"""
    st.session_state.user = None
    st.session_state.current_role = 'guest'
    st.rerun()

# --- Helper Functions ---
def generate_registration_number(state: str) -> str:
    """Generate unique registration number"""
    cursor = conn.cursor()
    try:
        # Get state code (first two letters)
        state_code = state[:2].upper()
        
        # Get sequential number
        cursor.execute("""
            SELECT COUNT(*) as count FROM registrations 
            WHERE state LIKE %s AND YEAR(application_date) = YEAR(CURDATE())
        """, (f"{state_code}%",))
        count = cursor.fetchone()['count'] + 1
        
        # Format: StateCode-SeriesNumber-UniqueNumber
        series = datetime.now().strftime('%y')
        unique_num = str(count).zfill(4)
        return f"{state_code}{series}{unique_num}"
    finally:
        cursor.close()

def get_status_badge(status: str) -> str:
    """Return HTML for status badge"""
    badges = {
        'approved': 'status-approved',
        'pending': 'status-pending',
        'rejected': 'status-rejected',
        'verified': 'status-verified'
    }
    return f'<span class="status-badge {badges.get(status, "status-pending")}">{status.upper()}</span>'

def get_role_badge(role: str) -> str:
    """Return HTML for role badge"""
    badges = {
        'admin': 'role-admin',
        'user': 'role-user',
        'inspector': 'role-inspector'
    }
    return f'<span class="role-badge {badges.get(role, "role-user")}">{role.upper()}</span>'

# --- CRUD Operations ---
def add_vehicle_registration(vehicle_data: dict, owner_id: int) -> tuple:
    """Add new vehicle registration"""
    cursor = conn.cursor()
    try:
        # Check for duplicate engine/chassis numbers
        cursor.execute("SELECT * FROM vehicles WHERE engine_no = %s OR chassis_no = %s", 
                      (vehicle_data['engine_no'], vehicle_data['chassis_no']))
        if cursor.fetchone():
            show_toast("Error: Engine or Chassis number already exists!", "warning")
            return False, None
        
        # Insert vehicle details
        cursor.execute("""
            INSERT INTO vehicles (engine_no, chassis_no, manufacturer, model, 
            vehicle_type, fuel_type, color, manufacturing_year, seating_capacity)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            vehicle_data['engine_no'], vehicle_data['chassis_no'],
            vehicle_data['manufacturer'], vehicle_data['model'],
            vehicle_data['vehicle_type'], vehicle_data['fuel_type'],
            vehicle_data['color'], vehicle_data['manufacturing_year'],
            vehicle_data['seating_capacity']
        ))
        
        vehicle_id = cursor.lastrowid
        
        # Generate registration number
        reg_no = generate_registration_number(vehicle_data['state'])
        
        # Insert registration
        cursor.execute("""
            INSERT INTO registrations (reg_no, vehicle_id, owner_id, state, district,
            application_date, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            reg_no, vehicle_id, owner_id,
            vehicle_data['state'], vehicle_data['district'],
            datetime.now().date(), 'pending'
        ))
        
        conn.commit()
        show_toast(f"Registration submitted successfully! Reference: {reg_no}", "success")
        return True, reg_no
        
    except IntegrityError as e:
        conn.rollback()
        show_toast("Database error: Please try again.", "warning")
        return False, None
    finally:
        cursor.close()

# --- Analytics Functions ---
def get_registration_stats() -> dict:
    """Get comprehensive registration statistics"""
    cursor = conn.cursor()
    try:
        stats = {}
        
        # Basic counts
        cursor.execute("SELECT COUNT(*) as total FROM registrations")
        stats['total'] = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as pending FROM registrations WHERE status = 'pending'")
        stats['pending'] = cursor.fetchone()['pending']
        
        cursor.execute("SELECT COUNT(*) as approved FROM registrations WHERE status = 'approved'")
        stats['approved'] = cursor.fetchone()['approved']
        
        # Monthly registrations
        cursor.execute("""
            SELECT DATE_FORMAT(application_date, '%Y-%m') as month, 
                   COUNT(*) as count
            FROM registrations
            WHERE application_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            GROUP BY month
            ORDER BY month
        """)
        stats['monthly'] = cursor.fetchall()
        
        # Vehicle type distribution
        cursor.execute("""
            SELECT v.vehicle_type, COUNT(*) as count
            FROM vehicles v
            JOIN registrations r ON v.vehicle_id = r.vehicle_id
            GROUP BY v.vehicle_type
        """)
        stats['vehicle_types'] = cursor.fetchall()
        
        # Fuel type analysis
        cursor.execute("""
            SELECT v.fuel_type, COUNT(*) as count
            FROM vehicles v
            JOIN registrations r ON v.vehicle_id = r.vehicle_id
            GROUP BY v.fuel_type
        """)
        stats['fuel_types'] = cursor.fetchall()
        
        # Approval rate
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) / COUNT(*) * 100 as approval_rate
            FROM registrations
            WHERE status IN ('approved', 'rejected')
        """)
        stats['approval_rate'] = cursor.fetchone()['approval_rate'] or 0
        
        return stats
    finally:
        cursor.close()

# --- Login Page ---
def show_login_page():
    """Display login page"""
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🏢 RTO Vehicle Registration System")
        st.markdown("### *Digitizing Vehicle Registration Workflow*")
        
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            
            login_tab, register_tab = st.tabs(["🔐 Login", "📝 Register"])
            
            with login_tab:
                username = st.text_input("Username", key="login_username")
                password = st.text_input("Password", type="password", key="login_password")
                
                if st.button("Login", type="primary", use_container_width=True):
                    if login(username, password):
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
            
            with register_tab:
                st.info("Note: User registrations require admin approval")
                full_name = st.text_input("Full Name")
                email = st.text_input("Email")
                phone = st.text_input("Phone")
                new_username = st.text_input("Choose Username")
                new_password = st.text_input("Choose Password", type="password")
                
                if st.button("Register", use_container_width=True):
                    # Simplified registration - in production, would send for approval
                    st.info("Registration functionality would be implemented with admin approval workflow")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- Main Application ---
def main_app():
    """Main application after login"""
    
    # --- Sidebar ---
    with st.sidebar:
        st.markdown('<div class="slide-in">', unsafe_allow_html=True)
        
        # User profile
        user = st.session_state.user
        st.markdown(f"""
            <div class="card">
                <h4>👤 {user['full_name']}</h4>
                <div>{get_role_badge(user['role'])}</div>
                <small>{user['email'] or 'No email'}</small>
            </div>
        """, unsafe_allow_html=True)
        
        # Navigation based on role
        st.markdown("---")
        st.subheader("📱 Navigation")
        
        if st.session_state.current_role == 'admin':
            menu_options = ["Dashboard", "Approve Registrations", "Manage Users", "Analytics", "System Logs"]
        elif st.session_state.current_role == 'inspector':
            menu_options = ["Dashboard", "Verify Vehicles", "My Inspections", "Reports"]
        else:  # user
            menu_options = ["Dashboard", "New Registration", "My Applications", "Track Status"]
        
        selected_menu = st.radio("", menu_options, label_visibility="collapsed")
        
        # Statistics
        st.markdown("---")
        st.subheader("📊 Quick Stats")
        
        stats = get_registration_stats()
        st.metric("Total Registrations", stats['total'])
        st.metric("Pending Approvals", stats['pending'])
        st.metric("Approval Rate", f"{stats['approval_rate']:.1f}%")
        
        # Logout button
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # --- Main Content Area ---
    
    # Show toast if set
    if st.session_state.show_toast:
        message, toast_type = st.session_state.show_toast
        if toast_type == "success":
            st.success(message)
        else:
            st.warning(message)
        st.session_state.show_toast = None
    
    # --- Dashboard Tab ---
    if selected_menu == "Dashboard":
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        
        # Hero Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.metric("Total Vehicles", stats['total'], delta=f"{stats['pending']} pending")
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.metric("Approval Rate", f"{stats['approval_rate']:.1f}%", 
                     delta="High" if stats['approval_rate'] > 75 else "Needs attention")
            st.markdown('</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.metric("This Month", 
                     sum(m['count'] for m in stats['monthly'] if m['month'] == datetime.now().strftime('%Y-%m')),
                     delta="Current")
            st.markdown('</div>', unsafe_allow_html=True)
        with col4:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.metric("Vehicle Types", len(stats['vehicle_types']))
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Charts Section
        if stats['total'] > 0:
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("📈 Monthly Registrations")
                
                if stats['monthly']:
                    monthly_df = pd.DataFrame(stats['monthly'])
                    fig = px.line(monthly_df, x='month', y='count', 
                                 markers=True, line_shape='spline')
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        xaxis=dict(showgrid=False, title=""),
                        yaxis=dict(showgrid=False, title="Registrations")
                    )
                    st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col_chart2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("🚗 Vehicle Type Distribution")
                
                if stats['vehicle_types']:
                    types_df = pd.DataFrame(stats['vehicle_types'])
                    fig = px.pie(types_df, values='count', names='vehicle_type',
                                color_discrete_sequence=px.colors.qualitative.Set3)
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        showlegend=True
                    )
                    st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Additional charts
            col_chart3, col_chart4 = st.columns(2)
            
            with col_chart3:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("⛽ Fuel Type Analysis")
                
                if stats['fuel_types']:
                    fuel_df = pd.DataFrame(stats['fuel_types'])
                    fig = px.bar(fuel_df, x='fuel_type', y='count',
                                color='fuel_type')
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        xaxis=dict(showgrid=False, title=""),
                        yaxis=dict(showgrid=False, title="Count"),
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col_chart4:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("📊 Status Overview")
                
                status_counts = {
                    'Approved': stats['approved'],
                    'Pending': stats['pending'],
                    'Total': stats['total']
                }
                fig = go.Figure(data=[
                    go.Indicator(
                        mode="gauge+number",
                        value=stats['approval_rate'],
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "Approval Rate %"},
                        gauge={
                            'axis': {'range': [0, 100]},
                            'bar': {'color': "#10b981"},
                            'steps': [
                                {'range': [0, 50], 'color': "#ef4444"},
                                {'range': [50, 75], 'color': "#f59e0b"},
                                {'range': [75, 100], 'color': "#10b981"}
                            ]
                        }
                    )
                ])
                fig.update_layout(
                    height=300,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Recent Activity
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🕒 Recent Activity")
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.reg_no, r.status, r.application_date, u.full_name, v.model
            FROM registrations r
            JOIN users u ON r.owner_id = u.user_id
            JOIN vehicles v ON r.vehicle_id = v.vehicle_id
            ORDER BY r.created_at DESC
            LIMIT 10
        """)
        recent = cursor.fetchall()
        
        if recent:
            df = pd.DataFrame(recent)
            df['Status'] = df['status'].apply(lambda x: get_status_badge(x))
            st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.info("No recent activity. Start by adding a registration!")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # --- New Registration Tab (for users) ---
    elif selected_menu == "New Registration" and st.session_state.current_role == 'user':
        st.markdown('<div class="slide-in">', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        st.header("🚗 New Vehicle Registration")
        st.caption("Please fill all mandatory fields for vehicle registration")
        
        with st.form("registration_form", clear_on_submit=True):
            # Owner Details Section
            st.subheader("👤 Owner Details")
            col1, col2 = st.columns(2)
            with col1:
                owner_name = st.text_input("Full Name", value=st.session_state.user['full_name'])
                email = st.text_input("Email", value=st.session_state.user.get('email', ''))
            with col2:
                phone = st.text_input("Phone Number", value=st.session_state.user.get('phone', ''))
                aadhar = st.text_input("Aadhar Number (Optional)", max_chars=12)
            
            # Vehicle Details Section
            st.subheader("🚗 Vehicle Details")
            
            col3, col4 = st.columns(2)
            with col3:
                manufacturer = st.text_input("Manufacturer", placeholder="e.g., Maruti Suzuki")
                model = st.text_input("Model", placeholder="e.g., Swift Dzire")
                vehicle_type = st.selectbox(
                    "Vehicle Type",
                    ['2-wheeler', '3-wheeler', '4-wheeler', 'commercial', 'other']
                )
                fuel_type = st.selectbox(
                    "Fuel Type",
                    ['petrol', 'diesel', 'electric', 'cng', 'hybrid']
                )
            
            with col4:
                engine_no = st.text_input("Engine Number", placeholder="Unique engine number")
                chassis_no = st.text_input("Chassis Number", placeholder="Unique chassis number")
                color = st.text_input("Color")
                manufacturing_year = st.number_input(
                    "Manufacturing Year",
                    min_value=1990,
                    max_value=datetime.now().year,
                    value=datetime.now().year
                )
                seating_capacity = st.number_input("Seating Capacity", min_value=1, max_value=50, value=5)
            
            # Registration Details Section
            st.subheader("📍 Registration Details")
            col5, col6 = st.columns(2)
            with col5:
                state = st.text_input("State", placeholder="e.g., Maharashtra")
            with col6:
                district = st.text_input("District", placeholder="e.g., Mumbai")
            
            # Documents upload (simulated)
            st.subheader("📄 Required Documents")
            col7, col8, col9 = st.columns(3)
            with col7:
                st.checkbox("✅ Address Proof")
            with col8:
                st.checkbox("✅ Identity Proof")
            with col9:
                st.checkbox("✅ Vehicle Invoice")
            
            st.markdown("---")
            st.markdown('<p class="required-field">All fields are mandatory unless specified</p>', unsafe_allow_html=True)
            
            submitted = st.form_submit_button(
                "📋 Submit Registration",
                use_container_width=True,
                type="primary"
            )
            
            if submitted:
                # Validate required fields
                required_fields = [
                    owner_name, manufacturer, model, engine_no, chassis_no,
                    state, district
                ]
                
                if all(required_fields):
                    vehicle_data = {
                        'engine_no': sanitize_input(engine_no),
                        'chassis_no': sanitize_input(chassis_no),
                        'manufacturer': sanitize_input(manufacturer),
                        'model': sanitize_input(model),
                        'vehicle_type': vehicle_type,
                        'fuel_type': fuel_type,
                        'color': sanitize_input(color),
                        'manufacturing_year': manufacturing_year,
                        'seating_capacity': seating_capacity,
                        'state': sanitize_input(state),
                        'district': sanitize_input(district)
                    }
                    
                    success, reg_no = add_vehicle_registration(
                        vehicle_data, 
                        st.session_state.user['user_id']
                    )
                    
                    if success:
                        st.balloons()
                        time.sleep(2)
                        st.rerun()
                else:
                    show_toast("Please fill all required fields!", "warning")
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # --- Approve Registrations Tab (for admin) ---
    elif selected_menu == "Approve Registrations" and st.session_state.current_role == 'admin':
        st.markdown('<div class="slide-in">', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        st.header("✅ Approve/Reject Registrations")
        
        # Tabs for different statuses
        status_tabs = st.tabs(["⏳ Pending", "✅ Approved", "❌ Rejected"])
        
        with status_tabs[0]:  # Pending tab
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.registration_id, r.reg_no, r.application_date,
                       u.full_name, u.phone, v.*
                FROM registrations r
                JOIN users u ON r.owner_id = u.user_id
                JOIN vehicles v ON r.vehicle_id = v.vehicle_id
                WHERE r.status = 'pending'
                ORDER BY r.application_date
            """)
            pending_records = cursor.fetchall()
            
            if pending_records:
                for record in pending_records:
                    with st.expander(f"📄 Application: {record['reg_no']} - {record['full_name']}"):
                        col_info1, col_info2 = st.columns(2)
                        with col_info1:
                            st.markdown(f"**Owner:** {record['full_name']}")
                            st.markdown(f"**Phone:** {record['phone']}")
                            st.markdown(f"**Application Date:** {record['application_date']}")
                            st.markdown(f"**Vehicle:** {record['manufacturer']} {record['model']}")
                        with col_info2:
                            st.markdown(f"**Engine No:** {record['engine_no']}")
                            st.markdown(f"**Chassis No:** {record['chassis_no']}")
                            st.markdown(f"**Fuel Type:** {record['fuel_type']}")
                            st.markdown(f"**Color:** {record['color']}")
                        
                        st.markdown("---")
                        
                        # Approval buttons
                        col_btn1, col_btn2, col_btn3 = st.columns(3)
                        with col_btn1:
                            if st.button(f"✅ Approve {record['reg_no']}", key=f"approve_{record['registration_id']}"):
                                cursor.execute("""
                                    UPDATE registrations 
                                    SET status = 'approved', 
                                        status_updated_by = %s,
                                        status_updated_at = NOW(),
                                        registration_date = CURDATE()
                                    WHERE registration_id = %s
                                """, (st.session_state.user['user_id'], record['registration_id']))
                                conn.commit()
                                show_toast(f"Registration {record['reg_no']} approved!", "success")
                                st.rerun()
                        
                        with col_btn2:
                            if st.button(f"🔍 Verify {record['reg_no']}", key=f"verify_{record['registration_id']}"):
                                cursor.execute("""
                                    UPDATE registrations 
                                    SET status = 'verified',
                                        status_updated_by = %s,
                                        status_updated_at = NOW()
                                    WHERE registration_id = %s
                                """, (st.session_state.user['user_id'], record['registration_id']))
                                conn.commit()
                                show_toast(f"Registration {record['reg_no']} marked for verification!", "success")
                                st.rerun()
                        
                        with col_btn3:
                            remarks = st.text_input("Remarks (if rejecting)", key=f"remarks_{record['registration_id']}")
                            if st.button(f"❌ Reject {record['reg_no']}", key=f"reject_{record['registration_id']}"):
                                if remarks:
                                    cursor.execute("""
                                        UPDATE registrations 
                                        SET status = 'rejected',
                                            status_updated_by = %s,
                                            status_updated_at = NOW(),
                                            remarks = %s
                                        WHERE registration_id = %s
                                    """, (st.session_state.user['user_id'], remarks, record['registration_id']))
                                    conn.commit()
                                    show_toast(f"Registration {record['reg_no']} rejected.", "warning")
                                    st.rerun()
                                else:
                                    st.warning("Please provide remarks for rejection")
            else:
                st.info("No pending registrations!")
        
        # Show other statuses in their tabs
        for i, status in enumerate(['approved', 'rejected'], start=1):
            with status_tabs[i]:
                cursor.execute(f"""
                    SELECT r.reg_no, r.application_date, r.registration_date,
                           u.full_name, v.model, r.status, r.remarks
                    FROM registrations r
                    JOIN users u ON r.owner_id = u.user_id
                    JOIN vehicles v ON r.vehicle_id = v.vehicle_id
                    WHERE r.status = '{status}'
                    ORDER BY r.status_updated_at DESC
                    LIMIT 20
                """)
                status_records = cursor.fetchall()
                
                if status_records:
                    for record in status_records:
                        st.markdown(f"""
                            <div style="padding: 10px; margin: 5px 0; border-radius: 8px; background: rgba(30,41,59,0.5);">
                                <strong>{record['reg_no']}</strong> - {record['full_name']}<br>
                                <small>Vehicle: {record['model']} | 
                                Status: {get_status_badge(record['status'])}<br>
                                {f"Remarks: {record['remarks']}" if record['remarks'] else ""}
                                </small>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info(f"No {status} registrations!")
        
        cursor.close()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # --- Search & Filter Tab ---
    elif selected_menu == "My Applications" and st.session_state.current_role == 'user':
        st.markdown('<div class="slide-in">', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        st.header("🔍 Search & Track Applications")
        
        # Search and filter options
        col_search1, col_search2, col_search3 = st.columns(3)
        with col_search1:
            search_type = st.selectbox(
                "Search by",
                ["Registration Number", "Vehicle Model", "Status"]
            )
        
        with col_search2:
            if search_type == "Registration Number":
                search_term = st.text_input("Enter registration number")
            elif search_type == "Vehicle Model":
                search_term = st.text_input("Enter vehicle model")
            else:
                search_term = st.selectbox("Select status", ["pending", "approved", "rejected", "verified"])
        
        with col_search3:
            st.markdown("<br>", unsafe_allow_html=True)
            search_btn = st.button("🔍 Search", use_container_width=True)
        
        # Date filters
        col_date1, col_date2 = st.columns(2)
        with col_date1:
            date_from = st.date_input("From date", value=datetime.now() - timedelta(days=30))
        with col_date2:
            date_to = st.date_input("To date", value=datetime.now())
        
        # Get user's applications
        cursor = conn.cursor()
        query = """
            SELECT r.reg_no, r.application_date, r.status, r.registration_date,
                   v.model, v.vehicle_type, v.fuel_type, r.remarks
            FROM registrations r
            JOIN vehicles v ON r.vehicle_id = v.vehicle_id
            WHERE r.owner_id = %s
            AND r.application_date BETWEEN %s AND %s
        """
        params = [st.session_state.user['user_id'], date_from, date_to]
        
        if search_btn and search_term:
            if search_type == "Registration Number":
                query += " AND r.reg_no LIKE %s"
                params.append(f"%{search_term}%")
            elif search_type == "Vehicle Model":
                query += " AND v.model LIKE %s"
                params.append(f"%{search_term}%")
            elif search_type == "Status":
                query += " AND r.status = %s"
                params.append(search_term)
        
        cursor.execute(query, params)
        applications = cursor.fetchall()
        
        if applications:
            df = pd.DataFrame(applications)
            df['Status'] = df['status'].apply(lambda x: get_status_badge(x))
            
            # Convert to HTML for better styling
            st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)
            
            # Export options
            st.download_button(
                label="📥 Export as CSV",
                data=df.to_csv(index=False),
                file_name=f"my_applications_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No applications found matching your criteria!")
        
        cursor.close()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # --- Analytics Tab (for admin) ---
    elif selected_menu == "Analytics" and st.session_state.current_role == 'admin':
        st.markdown('<div class="slide-in">', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        st.header("📊 Advanced Analytics Dashboard")
        
        stats = get_registration_stats()
        
        # Time series analysis
        st.subheader("📅 Registration Trends")
        
        if stats['monthly']:
            trend_df = pd.DataFrame(stats['monthly'])
            fig = px.area(trend_df, x='month', y='count', 
                         title="Monthly Registration Trends",
                         line_shape='spline')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Comparison charts
        col_compare1, col_compare2 = st.columns(2)
        
        with col_compare1:
            st.subheader("🚗 Vehicle Type Analysis")
            if stats['vehicle_types']:
                types_df = pd.DataFrame(stats['vehicle_types'])
                fig = px.bar(types_df, x='vehicle_type', y='count',
                            color='vehicle_type',
                            text='count')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col_compare2:
            st.subheader("⛽ Fuel Type Comparison")
            if stats['fuel_types']:
                fuel_df = pd.DataFrame(stats['fuel_types'])
                fig = px.pie(fuel_df, values='count', names='fuel_type',
                            hole=0.4,
                            color_discrete_sequence=px.colors.qualitative.Pastel)
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Performance metrics
        st.subheader("📈 Performance Metrics")
        
        col_metric1, col_metric2, col_metric3 = st.columns(3)
        with col_metric1:
            avg_processing_time = 3.2  # This would be calculated from database
            st.metric("Avg Processing Time", f"{avg_processing_time} days", delta="-0.5 days")
        
        with col_metric2:
            rejection_rate = 100 - stats['approval_rate']
            st.metric("Rejection Rate", f"{rejection_rate:.1f}%", 
                     delta="+1.2%" if rejection_rate > 10 else "-0.8%")
        
        with col_metric3:
            current_month = sum(m['count'] for m in stats['monthly'] 
                              if m['month'] == datetime.now().strftime('%Y-%m'))
            prev_month = sum(m['count'] for m in stats['monthly'] 
                           if m['month'] == (datetime.now() - timedelta(days=30)).strftime('%Y-%m'))
            growth = ((current_month - prev_month) / prev_month * 100) if prev_month > 0 else 0
            st.metric("Monthly Growth", f"{growth:.1f}%", 
                     delta="positive" if growth > 0 else "negative")
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # --- Footer ---
    st.markdown("---")
    footer_col1, footer_col2, footer_col3 = st.columns([2, 1, 1])
    with footer_col1:
        st.caption("© 2024 RTO Vehicle Registration System | Built with Streamlit & MySQL")
        st.caption("**Problem Solved:** Manual vehicle registration is time-consuming, error-prone, and difficult to track. This system digitizes the RTO workflow with secure storage, validation, and analytics.")
    with footer_col3:
        st.caption(f"🔄 Last updated: {datetime.now().strftime('%H:%M:%S')}")

# --- Main Execution Flow ---
def main():
    """Main execution flow"""
    
    # Show login page if not authenticated
    if not st.session_state.user:
        show_login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()
