# 🚗 RTO Vehicle Registration System

A secure, role-based vehicle registration and analytics platform built using **Streamlit, MySQL, and Plotly**.  
This system digitizes the Regional Transport Office (RTO) workflow with authentication, approval management, and real-time analytics.

---

## 📌 Features

### 🔐 Authentication & Security
- Role-based login (Admin / User / Inspector)
- Bcrypt password hashing
- Session-based authentication
- Input sanitization and validation

### 🚘 Vehicle Registration
- Unique engine & chassis number validation
- Auto-generated registration numbers
- Multi-section vehicle registration form
- Status lifecycle: Pending → Verified → Approved / Rejected

### 🧑‍💼 Admin Controls
- Approve, reject, or verify registrations
- View recent activities
- Monitor approval and rejection metrics

### 📊 Analytics Dashboard
- Monthly registration trends
- Vehicle type distribution
- Fuel type analysis
- Approval rate gauge
- Exportable reports

### 🎨 UI & UX
- Dark theme with custom CSS
- Smooth animations
- Responsive layout
- Interactive Plotly charts

---

## 🛠️ Tech Stack

| Layer | Technology |
|------|-----------|
| Frontend | Streamlit |
| Backend | Python |
| Database | MySQL |
| Authentication | Bcrypt |
| Visualization | Plotly |
| Styling | Custom CSS |

---

## 🧑‍💻 User Roles

### 👤 User
- Submit vehicle registrations
- Track application status
- Search and export applications

### 🛡️ Admin
- Approve / reject registrations
- Verify applications
- Access analytics dashboard

### 🔍 Inspector
- Vehicle verification workflow (extensible)

---

## 🗄️ Database Schema

**Core Tables**
- users
- vehicles
- registrations
- payments
- audit_logs

All tables are automatically created at runtime if they do not exist.

---

## 📂 Project Structure

RTO-Vehicle-Registration-System/
│
├── app.py
├── README.md


---

## ⚙️ Installation & Setup

### 1️⃣ Clone Repository
git clone https://github.com/your-username/rto-vehicle-registration-system.git


### 2️⃣ Install Dependencies
pip install streamlit pymysql pandas plotly bcrypt


### 3️⃣ Create Database

Update database credentials in `app.py`:
```python
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "your_password"
DB_NAME = "rto_vehicle_system"

### 4️⃣ Run Application
streamlit run app.py


---

If you want next:
✅ `requirements.txt` file  
✅ Resume bullets (ATS-friendly)  
✅ Project abstract (college submission)  
✅ GitHub badges & screenshots section  

Just tell me 🔥
