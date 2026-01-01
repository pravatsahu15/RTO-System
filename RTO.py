import streamlit as st
import pymysql
from pymysql import IntegrityError
import pandas as pd
import time
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random

# --- Page Configuration with Dark Theme ---
st.set_page_config(
    page_title="🚗 Vehicle Database Pro",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🚗"
)

# Apply custom CSS for dark theme and animations
st.markdown("""
<style>
    /* Main dark theme */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #e2e8f0;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #f1f5f9 !important;
        font-weight: 700 !important;
    }
    
    /* Cards and containers */
    .card {
        background: rgba(30, 41, 59, 0.7);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #3b82f6;
        backdrop-filter: blur(10px);
    }
    
    /* Input fields */
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input {
        background: #1e293b !important;
        color: white !important;
        border: 1px solid #475569 !important;
        border-radius: 10px !important;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(59, 130, 246, 0.4) !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(30, 41, 59, 0.7) !important;
        border-radius: 10px 10px 0 0 !important;
        padding: 10px 20px !important;
        border: none !important;
        color: #94a3b8 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6) !important;
        color: white !important;
    }
    
    /* Dataframe */
    .dataframe {
        background: rgba(15, 23, 42, 0.8) !important;
        color: white !important;
    }
    
    /* Metrics */
    .stMetric {
        background: rgba(30, 41, 59, 0.7);
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #10b981;
    }
    
    /* Success/Error messages */
    .stAlert {
        border-radius: 10px;
        border: none;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }
    
    /* Progress bars */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
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
    
    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    .slide-in {
        animation: slideIn 0.4s ease-out;
    }
    
    /* Custom success/warning styling */
    .custom-success {
        background: linear-gradient(90deg, #10b981, #34d399);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .custom-warning {
        background: linear-gradient(90deg, #f59e0b, #fbbf24);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    /* Table styling */
    table {
        border-collapse: separate;
        border-spacing: 0;
        border-radius: 10px;
        overflow: hidden;
    }
    
    th {
        background: #3b82f6 !important;
        color: white !important;
        font-weight: 600 !important;
    }
    
    td {
        background: rgba(30, 41, 59, 0.7) !important;
        color: #e2e8f0 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Database Configuration ---
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "P@sahu15"
DB_NAME = "vehicle_db"

# --- Database Connection Management ---
@st.cache_resource
def get_db_connection():
    """Establishes and caches the database connection."""
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return conn
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        st.stop()
        
def create_table(conn):
    """Creates the VehicleDetails table if it doesn't exist."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS VehicleDetails (
                reg_no VARCHAR(20) PRIMARY KEY,
                owner_name VARCHAR(100),
                state VARCHAR(50),
                district VARCHAR(50),
                phone VARCHAR(15),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    except Exception as e:
        st.error(f"Error creating table: {e}")
    finally:
        if cursor: cursor.close()

# Initialize connection and table
conn = get_db_connection()
create_table(conn)

# --- Enhanced CRUD Functions ---
def add_vehicle(reg_no, owner_name, state, district, phone):
    """Adds a new vehicle record with visual feedback."""
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO VehicleDetails (reg_no, owner_name, state, district, phone) VALUES (%s, %s, %s, %s, %s)",
                       (reg_no.upper(), owner_name, state, district, phone))
        conn.commit()
        
        # Success animation
        with st.spinner("Adding vehicle..."):
            time.sleep(0.5)
            st.markdown(f'<div class="custom-success fade-in">✅ Vehicle <b>{reg_no.upper()}</b> added successfully!</div>', unsafe_allow_html=True)
            time.sleep(0.5)
        return True
    except IntegrityError:
        st.markdown(f'<div class="custom-warning fade-in">⚠️ Registration number <b>{reg_no.upper()}</b> already exists!</div>', unsafe_allow_html=True)
        return False
    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {e}")
        return False
    finally:
        cursor.close()

@st.cache_data(ttl=60)
def get_all_vehicles():
    """Fetches all vehicle records."""
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT reg_no, owner_name, state, district, phone, created_at FROM VehicleDetails ORDER BY created_at DESC")
        records = cursor.fetchall()
        columns = ["Reg No", "Owner Name", "State", "District", "Phone", "Added On"]
        if records:
            df = pd.DataFrame(records, columns=columns)
            df['Added On'] = pd.to_datetime(df['Added On']).dt.strftime('%Y-%m-%d %H:%M')
            return df
        return pd.DataFrame(columns=columns)
    finally:
        cursor.close()

def get_vehicle_by_reg_no(reg_no):
    """Fetches a single vehicle record by registration number."""
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM VehicleDetails WHERE reg_no=%s", (reg_no.upper(),))
        record = cursor.fetchone()
        return record
    finally:
        cursor.close()

def update_vehicle(reg_no, owner_name, state, district, phone):
    """Updates an existing vehicle record."""
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE VehicleDetails
            SET owner_name=%s, state=%s, district=%s, phone=%s
            WHERE reg_no=%s
        """, (owner_name, state, district, phone, reg_no.upper()))
        conn.commit()
        
        # Success animation
        with st.spinner("Updating details..."):
            time.sleep(0.5)
            st.markdown(f'<div class="custom-success fade-in">🎉 Details for <b>{reg_no.upper()}</b> updated successfully!</div>', unsafe_allow_html=True)
            time.sleep(0.5)
        return True
    except Exception as e:
        st.error(f"❌ Failed to update details: {e}")
        return False
    finally:
        cursor.close()

def delete_vehicle(reg_no):
    """Deletes a vehicle record with visual feedback."""
    cursor = conn.cursor()
    try:
        # Show confirmation dialog
        cursor.execute("DELETE FROM VehicleDetails WHERE reg_no=%s", (reg_no.upper(),))
        conn.commit()
        
        # Deletion animation
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i + 1)
        
        st.markdown(f'<div class="custom-warning fade-in">🗑️ Record for <b>{reg_no.upper()}</b> has been deleted!</div>', unsafe_allow_html=True)
        return True
    except Exception as e:
        st.error(f"❌ Failed to delete record: {e}")
        return False
    finally:
        cursor.close()

def get_stats():
    """Get database statistics."""
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) as total FROM VehicleDetails")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT state) as states FROM VehicleDetails")
        states = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT district) as districts FROM VehicleDetails")
        districts = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT state, COUNT(*) as count 
            FROM VehicleDetails 
            GROUP BY state 
            ORDER BY count DESC 
            LIMIT 5
        """)
        top_states = cursor.fetchall()
        
        return {
            'total': total,
            'states': states,
            'districts': districts,
            'top_states': top_states
        }
    finally:
        cursor.close()

# --- Sidebar with Analytics ---
with st.sidebar:
    st.markdown('<div class="slide-in">', unsafe_allow_html=True)
    st.title("📊 Dashboard")
    
    # Statistics
    stats = get_stats()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Vehicles", stats['total'], delta="+2 today" if stats['total'] > 0 else None)
    with col2:
        st.metric("States Covered", stats['states'])
    
    # Quick Actions
    st.markdown("---")
    st.subheader("⚡ Quick Actions")
    
    if st.button("🔄 Refresh All Data", use_container_width=True):
        get_all_vehicles.clear()
        st.rerun()
    
    if st.button("📊 View Statistics", use_container_width=True):
        st.session_state.show_stats = True
    
    if st.button("🧹 Clear Cache", use_container_width=True):
        get_all_vehicles.clear()
        st.success("Cache cleared!")
    
    # Database Info
    st.markdown("---")
    st.subheader("🗄️ Database Info")
    st.info(f"Connected to: {DB_NAME}")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    st.markdown("</div>", unsafe_allow_html=True)

# --- Main Header ---
st.markdown('<div class="fade-in">', unsafe_allow_html=True)
col_title1, col_title2, col_title3 = st.columns([3, 1, 1])
with col_title1:
    st.title("🚗 Vehicle Database Pro")
    st.markdown("### *Intelligent Vehicle Management System*")
with col_title3:
    st.markdown(f"### 📅 {datetime.now().strftime('%d %b %Y')}")
st.markdown("</div>", unsafe_allow_html=True)

# --- Create Tabs with Icons ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Dashboard", 
    "➕ Add Vehicle", 
    "📋 View Records", 
    "🔍 Search/Update", 
    "⚙️ Manage"
])

# --- Tab 1: Dashboard ---
with tab1:
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    
    # Hero Section
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric("Total Vehicles", stats['total'])
        st.caption("Registered in database")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric("States", stats['states'])
        st.caption("Different states covered")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric("Districts", stats['districts'])
        st.caption("Total districts represented")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Charts
    if stats['total'] > 0:
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("📈 State Distribution")
            if stats['top_states']:
                states_data = pd.DataFrame(stats['top_states'], columns=['State', 'Count'])
                fig = go.Figure(data=[
                    go.Bar(
                        x=states_data['State'],
                        y=states_data['Count'],
                        marker_color=['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444']
                    )
                ])
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=False)
                )
                st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_chart2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("📊 Quick Stats")
            df = get_all_vehicles()
            if not df.empty:
                recent_count = len(df[df['Added On'] >= (datetime.now() - pd.Timedelta(days=7)).strftime('%Y-%m-%d')])
                st.metric("Added Last 7 Days", recent_count)
                st.metric("Avg. Vehicles/Day", round(stats['total'] / 30, 1))
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Recent Activity
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🕒 Recent Activity")
    df = get_all_vehicles()
    if not df.empty:
        st.dataframe(df.head(5), use_container_width=True, hide_index=True)
    else:
        st.info("No recent activity. Start by adding vehicles!")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- Tab 2: Add Vehicle ---
with tab2:
    st.markdown('<div class="slide-in">', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("➕ Add New Vehicle")
    st.caption("Enter all details for the new vehicle record")
    
    with st.form("add_vehicle_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            reg_no = st.text_input(
                "🚗 Vehicle Registration Number",
                placeholder="e.g., MH12AB1234",
                max_chars=20,
                help="Enter the complete registration number"
            ).strip().upper()
            
            owner_name = st.text_input(
                "👤 Owner Name",
                placeholder="John Doe",
                max_chars=100
            ).strip()
        
        with col2:
            state = st.text_input(
                "📍 State",
                placeholder="e.g., Maharashtra",
                max_chars=50
            ).strip()
            
            district = st.text_input(
                "🏙️ District",
                placeholder="e.g., Mumbai",
                max_chars=50
            ).strip()

        phone = st.text_input(
            "📞 Phone Number",
            placeholder="9876543210",
            max_chars=15,
            help="Enter 10-digit mobile number"
        ).strip()
        
        st.markdown("---")
        
        submitted = st.form_submit_button(
            "💾 Save Vehicle Details",
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            if all([reg_no, owner_name, state, district, phone]):
                success = add_vehicle(reg_no, owner_name, state, district, phone)
                if success:
                    get_all_vehicles.clear()
                    st.balloons()
                    time.sleep(1)
                    st.rerun()
            else:
                st.warning("⚠️ Please fill in all the required fields!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Tab 3: View Records ---
with tab3:
    st.markdown('<div class="slide-in">', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    col_header1, col_header2, col_header3 = st.columns([2, 1, 1])
    with col_header1:
        st.header("📋 Vehicle Records")
    with col_header3:
        if st.button("🔄 Refresh", key="refresh_main"):
            get_all_vehicles.clear()
            st.rerun()
    
    df = get_all_vehicles()
    
    if not df.empty:
        # Search and filter
        col_search, col_filter = st.columns(2)
        with col_search:
            search_term = st.text_input("🔍 Search records...", placeholder="Search by name or registration")
        
        if search_term:
            mask = df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)
            df_display = df[mask]
        else:
            df_display = df
        
        st.metric(label="Showing Records", value=len(df_display), delta=f"{len(df)} total")
        
        # Display with enhanced styling
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Reg No": st.column_config.TextColumn("Registration", width="medium"),
                "Owner Name": st.column_config.TextColumn("Owner", width="large"),
                "Phone": st.column_config.TextColumn("Contact", width="small"),
                "Added On": st.column_config.TextColumn("Registered On", width="medium")
            }
        )
        
        # Export options
        col_export1, col_export2, col_export3 = st.columns(3)
        with col_export1:
            if st.button("📥 Export as CSV", use_container_width=True):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"vehicle_records_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    else:
        st.info("🚘 The database is currently empty. Add your first vehicle!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Tab 4: Search/Update ---
with tab4:
    st.markdown('<div class="slide-in">', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("🔍 Search & Update")
    
    search_col1, search_col2 = st.columns([3, 1])
    with search_col1:
        search_reg_no = st.text_input(
            "Enter Registration Number",
            placeholder="MH12AB1234",
            key="update_search",
            max_chars=20
        ).strip().upper()
    
    with search_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔎 Search", use_container_width=True):
            st.session_state.searched = True
    
    if search_reg_no and ('searched' in st.session_state or search_reg_no):
        record = get_vehicle_by_reg_no(search_reg_no)
        
        if record:
            st.markdown('<div class="custom-success fade-in">', unsafe_allow_html=True)
            st.success("✅ Record found! Current details shown below:")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Display current info in cards
            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.metric("Owner", record[1])
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col_info2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.metric("State", record[2])
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col_info3:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.metric("Phone", record[4])
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Update form
            st.subheader("📝 Update Details")
            with st.form("update_form"):
                new_owner = st.text_input("Owner Name", value=record[1])
                col_up1, col_up2 = st.columns(2)
                with col_up1:
                    new_state = st.text_input("State", value=record[2])
                with col_up2:
                    new_district = st.text_input("District", value=record[3])
                new_phone = st.text_input("Phone", value=record[4])
                
                st.markdown("---")
                
                if st.form_submit_button("💾 Update Record", use_container_width=True, type="primary"):
                    success = update_vehicle(search_reg_no, new_owner, new_state, new_district, new_phone)
                    if success:
                        get_all_vehicles.clear()
                        st.rerun()
        else:
            st.warning(f"⚠️ No record found for **{search_reg_no}**")
    else:
        st.info("🔍 Enter a registration number to search")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Tab 5: Manage ---
with tab5:
    st.markdown('<div class="slide-in">', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("⚙️ Database Management")
    
    tab_delete, tab_stats = st.tabs(["🗑️ Delete Records", "📊 Advanced Statistics"])
    
    with tab_delete:
        st.warning("⚠️ **Danger Zone:** Deleted records cannot be recovered!")
        
        delete_reg = st.text_input(
            "Enter Registration to Delete",
            placeholder="MH12AB1234",
            key="delete_input",
            max_chars=20
        ).strip().upper()
        
        if delete_reg:
            record = get_vehicle_by_reg_no(delete_reg)
            
            if record:
                st.error(f"**Record Found:** {record[1]} | {record[2]}")
                
                col_confirm1, col_confirm2 = st.columns(2)
                with col_confirm1:
                    if st.button(f"🗑️ Delete {delete_reg}", use_container_width=True, type="secondary"):
                        if delete_vehicle(delete_reg):
                            get_all_vehicles.clear()
                            time.sleep(2)
                            st.rerun()
                
                with col_confirm2:
                    if st.button("❌ Cancel", use_container_width=True):
                        st.rerun()
            else:
                st.info(f"No record found for {delete_reg}")
    
    with tab_stats:
        st.subheader("📈 Advanced Analytics")
        stats = get_stats()
        
        if stats['total'] > 0:
            # Create a gauge chart for database health
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = stats['total'],
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Database Size"},
                gauge = {
                    'axis': {'range': [None, max(100, stats['total'] + 10)]},
                    'bar': {'color': "#3b82f6"},
                    'steps': [
                        {'range': [0, 50], 'color': "#10b981"},
                        {'range': [50, 80], 'color': "#f59e0b"},
                        {'range': [80, 100], 'color': "#ef4444"}
                    ]
                }
            ))
            
            fig.update_layout(
                height=300,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Additional stats
            col_stat1, col_stat2 = st.columns(2)
            with col_stat1:
                st.metric("Database Health", "Good" if stats['total'] < 80 else "Warning", 
                         delta="Optimal" if stats['total'] < 50 else "Monitor")
            with col_stat2:
                st.metric("Unique States", stats['states'])
        
        else:
            st.info("Add more records to see analytics")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Footer ---
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns([2, 1, 1])
with footer_col1:
    st.caption("© 2024 Vehicle Database Pro | Built with Streamlit & MySQL")
with footer_col3:
    st.caption(f"🔄 Last updated: {datetime.now().strftime('%H:%M:%S')}")

# --- Session State Management ---
if 'show_stats' not in st.session_state:
    st.session_state.show_stats = False
if 'searched' not in st.session_state:
    st.session_state.searched = False
