import streamlit as st
import pymysql
from pymysql import IntegrityError
import pandas as pd

# --- Database Configuration (Use Streamlit Secrets for production!) ---
# NOTE: Replace these with your actual credentials or use st.secrets
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "P@sahu15" # WARNING: Hardcoding passwords is not secure!
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
                phone VARCHAR(15)
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

# --- CRUD Functions for Streamlit ---

def add_vehicle(reg_no, owner_name, state, district, phone):
    """Adds a new vehicle record."""
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO VehicleDetails VALUES (%s, %s, %s, %s, %s)",
                       (reg_no.upper(), owner_name, state, district, phone))
        conn.commit()
        st.success(f"✅ Vehicle **{reg_no.upper()}** added successfully!")
        return True
    except IntegrityError:
        st.error(f"❌ Error: Registration number **{reg_no.upper()}** already exists.")
        return False
    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {e}")
        return False
    finally:
        cursor.close()

@st.cache_data(ttl=60) # Cache data for 60 seconds
def get_all_vehicles():
    """Fetches all vehicle records."""
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM VehicleDetails")
        records = cursor.fetchall()
        columns = ["Reg No", "Owner Name", "State", "District", "Phone"]
        if records:
            return pd.DataFrame(records, columns=columns)
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
        st.success(f"🎉 Details for **{reg_no.upper()}** updated successfully!")
        return True
    except Exception as e:
        st.error(f"❌ Failed to update details: {e}")
        return False
    finally:
        cursor.close()

def delete_vehicle(reg_no):
    """Deletes a vehicle record."""
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM VehicleDetails WHERE reg_no=%s", (reg_no.upper(),))
        conn.commit()
        st.success(f"🗑️ Record for **{reg_no.upper()}** deleted successfully.")
        return True
    except Exception as e:
        st.error(f"❌ Failed to delete record: {e}")
        return False
    finally:
        cursor.close()

# --- Streamlit UI Layout ---

st.set_page_config(
    page_title="Vehicle Database Management System",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("🚗 Vehicle Record Manager")
st.markdown("A Streamlit application for managing vehicle owner details using MySQL.")

# Create tabs for clean navigation
tab_add, tab_view, tab_search_update, tab_delete = st.tabs(
    ["➕ Add Vehicle", "📋 View All Records", "🔍 Search/Update", "❌ Delete Record"]
)

# --- 1. Add Vehicle Tab ---
with tab_add:
    st.header("Add New Vehicle Details")
    st.markdown("Enter all details for the new vehicle record below.")
    
    with st.form("add_vehicle_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            reg_no = st.text_input("Vehicle Registration Number", max_chars=20).strip().upper()
            owner_name = st.text_input("Owner Name", max_chars=100).strip()
        
        with col2:
            state = st.text_input("State", max_chars=50).strip()
            district = st.text_input("District", max_chars=50).strip()

        phone = st.text_input("Phone Number", max_chars=15, help="e.g., 9876543210").strip()
        
        st.markdown("---")
        submitted = st.form_submit_button("💾 Save Vehicle Details", use_container_width=True)
        
        if submitted:
            if all([reg_no, owner_name, state, district, phone]):
                success = add_vehicle(reg_no, owner_name, state, district, phone)
                if success:
                    get_all_vehicles.clear() # Clear cache after successful insertion
                    st.rerun() # Rerun to show updated data
            else:
                st.warning("Please fill in all the required fields.")

# --- 2. View All Records Tab ---
with tab_view:
    st.header("All Registered Vehicle Records")
    
    # Button to refresh data
    if st.button("🔄 Refresh Data", key="refresh_view"):
        get_all_vehicles.clear()
        st.rerun()
        
    df = get_all_vehicles()
    
    if not df.empty:
        st.metric(label="Total Records", value=len(df))
        # Display DataFrame as an interactive table
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("The database is currently empty. Add a vehicle in the 'Add Vehicle' tab.")

# --- 3. Search/Update Tab ---
with tab_search_update:
    st.header("Search and Update Vehicle Details")
    
    # 1. Search Section
    st.subheader("1. Find Record")
    search_reg_no = st.text_input(
        "Enter Registration Number to Search/Update", 
        key="update_search_reg", 
        max_chars=20
    ).strip().upper()
    
    if search_reg_no:
        record = get_vehicle_by_reg_no(search_reg_no)
        
        if record:
            st.success("Record found! You can now update the details below.")
            
            # Display current details
            st.info(f"Current Owner: **{record[1]}** | State: **{record[2]}** | Phone: **{record[4]}**")
            
            # 2. Update Form
            st.subheader("2. Update Details")
            with st.form("update_vehicle_form"):
                
                # Pre-populate fields with current data
                new_owner_name = st.text_input("Owner Name", value=record[1]).strip()
                col_up1, col_up2 = st.columns(2)
                with col_up1:
                    new_state = st.text_input("State", value=record[2]).strip()
                with col_up2:
                    new_district = st.text_input("District", value=record[3]).strip()
                new_phone = st.text_input("Phone Number", value=record[4]).strip()
                
                st.markdown("---")
                updated = st.form_submit_button("✅ Update Details", use_container_width=True)
                
                if updated:
                    success = update_vehicle(search_reg_no, new_owner_name, new_state, new_district, new_phone)
                    if success:
                        get_all_vehicles.clear() # Clear cache
                        st.rerun() # Rerun to show updated info
                    
        else:
            st.warning(f"No record found for registration number **{search_reg_no}**.")
    else:
        st.info("Enter a Registration Number to begin searching.")

# --- 4. Delete Record Tab ---
with tab_delete:
    st.header("Delete Vehicle Record")
    st.warning("⚠️ This action is irreversible. Proceed with caution.")
    
    delete_reg_no = st.text_input(
        "Enter Registration Number to Delete", 
        key="delete_reg", 
        max_chars=20
    ).strip().upper()
    
    if delete_reg_no:
        record_to_delete = get_vehicle_by_reg_no(delete_reg_no)
        
        if record_to_delete:
            st.error(f"Record found for owner: **{record_to_delete[1]}** in **{record_to_delete[3]}**.")
            
            if st.button(f"🔥 Permanently Delete Record: {delete_reg_no}", use_container_width=True):
                success = delete_vehicle(delete_reg_no)
                if success:
                    get_all_vehicles.clear() # Clear cache
                    st.rerun() # Rerun to clear input and message
        else:
            st.info(f"No record found for registration number **{delete_reg_no}**.")
    
# --- Footer/Cleanup ---
st.sidebar.markdown("---")
st.sidebar.caption("App created using Streamlit and pymysql.")