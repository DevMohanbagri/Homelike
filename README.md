# Hostel Maintenance System

A full-stack web application for managing hostel maintenance complaints and resolutions. The system features role-based access (Admin/Warden and Student/Resident), **Firebase Console Authentication**, and complaint lifecycle management.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Firebase Setup](#firebase-setup)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [User Roles & Features](#user-roles--features)
- [API Endpoints](#api-endpoints)
- [System Architecture](#system-architecture)
- [Troubleshooting](#troubleshooting)

---

## Features

### Core Features
- **Firebase Console Authentication** - Secure login using Firebase with Email/Password and Google Sign-In
- **Role-Based Access Control**
  - Admin/Warden: Manage and resolve complaints
  - Student/Resident: File and track complaints
- **Complaint Management**
  - File complaints for Room, Washroom, or Water Filter
  - Track complaint status: Pending → Resolved → Confirmed
  - Filter complaints by status
- **Real-time Dashboard**
  - Statistics and complaint summaries
  - Status tracking and lifecycle management
  - Student confirmation of resolutions

### Database Features
- MySQL database with proper foreign key relationships
- Complaint linking to specific amenities (Room, Washroom, Filter)
- Hostel-based complaint filtering
- Warden-specific complaint assignment

### Authentication Features
- Multiple authentication methods (Email/Password, Google)
- Professional Firebase authentication UI
- Built-in email verification
- Password reset functionality
- Secure token verification on backend

---

## Technology Stack

### Backend
- **Flask** 2.3.3 - Web framework
- **Python 3.8+** - Programming language
- **MySQL** - Relational database
- **firebase-admin** 6.2.0 - Firebase backend SDK
- **mysql-connector-python** - Database driver

### Frontend
- **HTML5** - Markup
- **CSS3 & Tailwind CSS** - Styling
- **JavaScript (ES6+)** - Client-side logic
- **FirebaseUI** - Professional authentication UI
- **Fetch API** - HTTP requests

---

## Prerequisites

### System Requirements
- Python 3.8 or higher
- MySQL 5.7 or higher
- Git
- Firebase Console account (free)

### Software Installation

**Windows/Mac/Linux - Python:**
```bash
# Check Python version
python --version

# If not installed, download from https://www.python.org/downloads/
```

**Windows - MySQL:**
- Download from https://dev.mysql.com/downloads/mysql/
- Run the installer and follow the setup wizard
- Note: Remember the root password

**Mac - MySQL (using Homebrew):**
```bash
brew install mysql
brew services start mysql
```

**Linux - MySQL (Debian/Ubuntu):**
```bash
sudo apt-get update
sudo apt-get install mysql-server
sudo mysql_secure_installation
```

---

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/hostel-maintenance-system.git
cd hostel-maintenance-system
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements_firebase.txt
```

---


NOTE - To quick run the application, just double click index.html file.

I am still working on making it work with firebase
## Firebase Setup

### Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **"Add project"**
3. Enter project name: `Hostel Maintenance System`
4. Click **"Create project"**
5. Wait for project creation (1-2 minutes)

### Step 2: Enable Authentication Methods

1. In Firebase Console, go to **Authentication** (left sidebar)
2. Click **"Get started"**
3. Enable **Email/Password**:
   - Click "Email/Password" provider
   - Toggle **"Enable"** to ON
   - Click "Save"
4. Enable **Google**:
   - Click "Google" provider
   - Toggle **"Enable"** to ON
   - Enter your support email (auto-filled)
   - Click "Save"

### Step 3: Register Web App

1. Go to **Project settings** (gear icon at top)
2. Click **"Your apps"** or scroll to find web app section
3. Click **"Add app"** → Select **"Web"**
4. Enter app name: `Hostel Maintenance Web`
5. Click **"Register app"**
6. Copy the **firebaseConfig** object (you'll need this)

**Example firebaseConfig:**
```javascript
{
  apiKey: "AIzaSyC...",
  authDomain: "hostel-maintenance-xxxx.firebaseapp.com",
  projectId: "hostel-maintenance-xxxx",
  storageBucket: "hostel-maintenance-xxxx.appspot.com",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:abcdef123456"
}
```

### Step 4: Download Admin SDK Credentials

1. Go to **Project settings** → **"Service Accounts"** tab
2. Click **"Generate Private Key"**
3. A JSON file will be downloaded automatically
4. Save as `firebase-adminsdk.json` in your project root

⚠️ **IMPORTANT:** Keep this file private. Add it to `.gitignore`

---

## Environment Configuration

### 1. Create Environment File

```bash
cp .env.firebase.example .env
```

### 2. Fill in Firebase Values

Update `.env` with values from your Firebase project:

```env
# Firebase Web Configuration (from firebaseConfig)
FIREBASE_API_KEY=AIzaSyC...
FIREBASE_AUTH_DOMAIN=hostel-maintenance-xxxx.firebaseapp.com
FIREBASE_PROJECT_ID=hostel-maintenance-xxxx
FIREBASE_STORAGE_BUCKET=hostel-maintenance-xxxx.appspot.com
FIREBASE_MESSAGING_SENDER_ID=123456789012
FIREBASE_APP_ID=1:123456789012:web:abcdef123456

# Path to Firebase Admin SDK Credentials
FIREBASE_CREDS_PATH=firebase-adminsdk.json

# Database Configuration
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_NAME=homelike

# Flask Configuration
FLASK_SECRET_KEY=your_generated_secret_key
FLASK_ENV=development
```

### 3. Generate Flask Secret Key

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and paste into `.env` as `FLASK_SECRET_KEY`

---

## Database Setup

### 1. Create Database

Run the database setup script:
```bash
python create_homelike_db.py
```

This will:
- Create the `homelike` database
- Create all required tables with proper relationships
- Set up foreign key constraints

### 2. Add Sample Data (Optional)

Connect to MySQL:
```bash
mysql -u root -p homelike
```

**Sample SQL for testing:**
```sql
-- Add Hostel
INSERT INTO Hostel (HId, HName, WName) VALUES ('H1', 'Hostel A', 'Hostel A Main');

-- Add Rooms
INSERT INTO Rooms (RNo, Occupancy, Block, Floor) VALUES ('R101', 2, 'A', 1);
INSERT INTO Rooms (RNo, Occupancy, Block, Floor) VALUES ('R102', 2, 'A', 1);

-- Add Washrooms
INSERT INTO Washroom (WashroomID, Floor, Block) VALUES ('W1', 1, 'A');

-- Add Water Filters
INSERT INTO Filter (FId, Floor, Block) VALUES ('F1', 1, 'A');

-- Add Warden (use your Firebase email)
INSERT INTO Warden (WardenID, WName, Wmail, Wcontact, HId) 
VALUES ('WAR1', 'John Doe', 'warden@university.edu', '9876543210', 'H1');

-- Add Student (use your Firebase email)
INSERT INTO Student (SId, SName, Smail, Scontact, HId, RNo) 
VALUES ('STU1', 'Jane Smith', 'student@university.edu', '9123456789', 'H1', 'R101');
```

⚠️ **Important:** Use the same email addresses you'll use for Firebase authentication!

---

## Running the Application

### Start the Flask Server

```bash
python app_firebase.py
```

**Expected Output:**
```
✅ Firebase initialized successfully
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

### Access the Application

Open your browser and navigate to:
```
http://localhost:5000
```

You will be redirected to the Firebase login page.

---

## User Roles & Features

### Student/Resident Role

**Login:**
1. Go to http://localhost:5000
2. Click **"Sign up"** or **"Sign in"**
3. Choose authentication method:
   - **Email/Password**: Enter your email and create password
   - **Google**: Click Google button and sign in with Google account
4. You'll be redirected to the **Student Dashboard**

**Features:**
- **File New Complaint**
  - Select complaint type (Room, Washroom, or Water Filter)
  - Provide the amenity ID (e.g., R101 for room, W1 for washroom)
  - Add detailed description
  - Submit complaint

- **Track Complaints**
  - View all your filed complaints
  - See current status (Pending, Resolved, Confirmed)
  - View filing date and time
  - View complete complaint details

- **Confirm Resolution**
  - Once warden marks complaint as "Resolved"
  - Review the resolution
  - Confirm the resolution with one click
  - Complaint status changes to "Confirmed"

### Admin/Warden Role

**Login:**
1. Go to http://localhost:5000
2. Sign in with your warden account (same Firebase authentication)
3. You'll be redirected to the **Warden Dashboard**

**Features:**
- **Dashboard Overview**
  - Total complaints count
  - Pending complaints count
  - Resolved complaints count
  - Confirmed complaints count

- **View All Complaints**
  - List of all complaints assigned to your hostel
  - Filter by status (All, Pending, Resolved, Confirmed)
  - View student name and email
  - See complaint type and amenity ID
  - Read full complaint description

- **Manage Complaints**
  - Mark complaints as "Resolved"
  - Students will then confirm the resolution
  - Track complaint lifecycle in real-time

- **Refresh Data**
  - Real-time updates
  - Quick refresh button for latest data

---

## API Endpoints

### Authentication
- `POST /api/auth/firebase` - Firebase token verification and user session creation

### Student Endpoints
- `POST /api/student/file-complaint` - File a new complaint
- `GET /api/student/complaints` - Get all student's complaints
- `POST /api/student/confirm-resolution/<complaint_id>` - Confirm resolution

### Warden Endpoints
- `GET /api/warden/complaints` - Get all assigned complaints
- `PUT /api/warden/complaint/<complaint_id>/resolve` - Mark as resolved
- `GET /api/warden/stats` - Get dashboard statistics

### Request/Response Examples

**File Complaint:**
```json
POST /api/student/file-complaint
Content-Type: application/json

{
  "description": "Water leakage in the bathroom",
  "complaint_type": "Room",
  "amenity_id": "R101"
}

Response:
{
  "success": true,
  "complaint_id": "CH10001",
  "message": "Complaint filed successfully"
}
```

**Mark as Resolved:**
```
PUT /api/warden/complaint/CH10001/resolve

Response:
{
  "success": true,
  "message": "Complaint marked as resolved"
}
```

---

## System Architecture

### Authentication Flow

```
User visits http://localhost:5000
              ↓
Redirects to /login (Flask)
              ↓
FirebaseUI displays authentication options
              ↓
User signs in (Email/Password or Google)
              ↓
Firebase validates credentials
              ↓
Frontend receives Firebase ID token
              ↓
Sends token to backend: POST /api/auth/firebase
              ↓
Backend verifies token with Firebase Admin SDK
              ↓
Backend looks up user email in MySQL database
              ↓
Backend detects role (Student or Warden)
              ↓
Backend creates session with user data
              ↓
Backend returns dashboard redirect URL
              ↓
Frontend redirects to /dashboard
              ↓
Backend routes to correct dashboard template
              ↓
User sees their dashboard!
```

### Database Schema

**Hostel Table**
- HId (Primary Key)
- HName
- WName

**Rooms Table**
- RNo (Primary Key)
- Occupancy
- Block
- Floor

**Washroom Table**
- WashroomID (Primary Key)
- Floor
- Block

**Filter Table**
- FId (Primary Key)
- Floor
- Block

**Warden Table**
- WardenID (Primary Key)
- WName
- Wmail (Unique, matches Firebase email)
- Wcontact
- HId (Foreign Key → Hostel)

**Student Table**
- SId (Primary Key)
- SName
- Smail (Unique, matches Firebase email)
- Scontact
- HId (Foreign Key → Hostel, Nullable)
- RNo (Foreign Key → Rooms, Nullable)

**Complaint Table**
- CId (Primary Key)
- description
- Status (Default: 'Pending')
- date_time
- SId (Foreign Key → Student)
- WardenID (Foreign Key → Warden)
- HId (Foreign Key → Hostel)
- RNo (Foreign Key → Rooms, Nullable)
- WashroomID (Foreign Key → Washroom, Nullable)
- FId (Foreign Key → Filter, Nullable)
- Check Constraint: At least one of RNo, WashroomID, or FId must be NOT NULL

### Complaint Lifecycle
```
1. Student files complaint → Status: Pending
2. Warden reviews → Status: Resolved
3. Student confirms → Status: Confirmed
```

---

## Troubleshooting

### Issue: "Firebase credentials file not found"

**Solution:**
1. Ensure `firebase-adminsdk.json` is in project root
2. Verify `FIREBASE_CREDS_PATH` in .env points to correct file
3. Check file has read permissions

### Issue: "Database connection failed"

**Solution:**
1. Check MySQL is running:
   ```bash
   # Windows
   net start MySQL80
   
   # Mac
   brew services start mysql
   
   # Linux
   sudo systemctl start mysql
   ```
2. Verify credentials in .env file
3. Ensure database exists: `mysql -u root -p -e "SHOW DATABASES;"`

### Issue: "User not registered in the system"

**Solution:**
1. Verify the Firebase email is in the database:
   ```sql
   SELECT * FROM Warden WHERE Wmail = 'your@email.com';
   SELECT * FROM Student WHERE Smail = 'your@email.com';
   ```
2. Email must match EXACTLY (case-sensitive in database checks)
3. Add the user using the Sample SQL provided above

### Issue: "Firebase authentication failed"

**Solution:**
1. Verify all Firebase config values in .env
2. Check `firebase-adminsdk.json` is valid (download again if needed)
3. Check browser console (F12) for JavaScript errors
4. Ensure internet connection (Firebase SDK loaded from CDN)

### Issue: "Invalid token" or "Token expired"

**Solution:**
1. This is usually temporary - try logging out and back in
2. Restart the Flask server
3. Clear browser cookies (Ctrl+Shift+Delete)

### Issue: Port 5000 already in use

**Solution:**
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Mac/Linux
lsof -i :5000
kill -9 <PID>
```

### Issue: CSS/JavaScript not loading

**Solution:**
1. Clear browser cache (Ctrl+Shift+Delete)
2. Check browser console for errors (F12)
3. Ensure internet connection (Tailwind CSS loaded from CDN)
4. Try different browser

---

## File Structure

```
hostel-maintenance-system/
├── app_firebase.py                 # Flask backend with Firebase
├── requirements_firebase.txt       # Python dependencies
├── create_homelike_db.py          # Database setup script
├── .env.example                    # Environment variables template
├── .env.firebase.example           # Firebase config template
├── firebase-adminsdk.json         # Firebase admin credentials (download)
├── README.md                       # This file
└── templates/
    ├── login_firebase.html         # Firebase login page
    ├── student_dashboard.html      # Student dashboard
    └── warden_dashboard.html       # Warden dashboard
```

---

## Security Best Practices

### Authentication Security
- Firebase handles password hashing and storage securely
- All tokens verified on backend with Firebase Admin SDK
- Session management with secure cookies
- Email verification built-in

### Application Security
- Never commit `.env` file to version control
- Keep `firebase-adminsdk.json` private (add to `.gitignore`)
- Validate all user inputs on backend
- Use parameterized queries (SQL injection prevention)
- Enable HTTPS in production

### Development Best Practices
- Use virtual environment for dependency isolation
- Keep Flask debug mode OFF in production
- Use proper error handling and logging
- Test all endpoints before deployment
- Regular database backups

### Production Deployment
- Enable HTTPS/SSL certificate
- Use environment-specific configuration
- Enable production Firebase security rules
- Use production database server
- Set up monitoring and logging
- Regular security audits

---

## Troubleshooting Checklist

Before opening an issue, verify:
- [ ] Firebase project is created
- [ ] Authentication methods enabled (Email/Password, Google)
- [ ] Firebase credentials downloaded (`firebase-adminsdk.json`)
- [ ] `.env` file created with all values
- [ ] MySQL is running
- [ ] Database created (`python create_homelike_db.py`)
- [ ] Test user added to database with Firebase email
- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip install -r requirements_firebase.txt`)
- [ ] Flask server running (`python app_firebase.py`)
- [ ] Browser cache cleared
- [ ] Internet connection working

---

## Support & Contribution

For issues or feature requests:
1. Check this README documentation
2. Review troubleshooting section
3. Check browser console for errors (F12)
4. Check Flask server logs for errors
5. Verify Firebase project configuration
6. Verify database setup

---

## License

This project is provided as-is for educational purposes.

---

## Version History

- **v2.0.0** (Firebase Integration)
  - Migrated from Google OAuth to Firebase Console
  - Added Email/Password authentication
  - Improved authentication UI with FirebaseUI
  - Better security with Firebase Admin SDK
  - Enhanced user management

- **v1.0.0** (Initial Release)
  - Core complaint management system
  - Google OAuth integration
  - Role-based access control
  - Real-time dashboards
  - Status tracking (Pending → Resolved → Confirmed)

---

## Contact

For technical support or questions, contact the hostel administration office or the development team.

---

**Last Updated:** 2024
**Authentication:** Firebase Console
**Author:** Hostel Maintenance System Team