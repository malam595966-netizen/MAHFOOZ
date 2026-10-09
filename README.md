# 👑 MAHFOOZ - Luxury Restaurant Web Application
> **Location:** Fraser Road, Near Dak Bungalow, Patna, Bihar - 800001, India  
> **Brand Identity:** Premium Royal Awadhi, Mughlai & Multi-Cuisine Fine Dining

---

## 🌟 Project Overview

**MAHFOOZ** is a full-stack, enterprise-grade restaurant web platform designed with an elegant Obsidian Black, Warm Cream, and Royal Gold visual aesthetic. It functions as a complete digital presence for the real-world business, featuring customer-facing ordering, table bookings, customer inquiries, order tracking, and a secure operational Admin Dashboard.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | HTML5, CSS3 (Custom Responsive Luxury Design System), Vanilla JavaScript (ES6+) |
| **Backend** | Python 3 (Flask Framework, Werkzeug Security) |
| **Database** | MySQL (with PyMySQL & Flask-SQLAlchemy ORM + SQLite auto-fallback) |
| **Icons & Fonts** | FontAwesome 6, Google Fonts (*Cinzel*, *Playfair Display*, *Plus Jakarta Sans*) |
| **Deployment Ready** | Python-Dotenv, WSGI-compliant architecture |

---

## 📁 Project Structure

```
d:\PROJECT\
├── app.py                      # Core Flask application, route controllers & API endpoints
├── config.py                   # Configuration & automatic MySQL connection handler
├── database.sql                # Complete MySQL schema & initial seed data script
├── requirements.txt            # Python dependencies (Flask, SQLAlchemy, PyMySQL, etc.)
├── seed_data.py                # Standalone database seeder script
├── .env.example                # Environment variables template
├── .env                        # Local active environment configuration
├── README.md                   # Complete documentation & setup guide
│
├── models/
│   ├── __init__.py             # SQLAlchemy DB instance & models registry
│   ├── admin.py                # Admin staff authentication model (password hashing)
│   ├── category.py             # Food category model (Starters, Biryani, Curries, etc.)
│   ├── food_item.py            # Menu dishes (pricing, veg/non-veg, availability, prep time)
│   ├── order.py                # Customer orders & itemized line items models
│   ├── reservation.py          # Table booking reservation model with reference codes
│   └── contact.py              # Customer contact & banquet inquiry model
│
├── static/
│   ├── css/
│   │   ├── style.css           # Luxury obsidian & gold theme, responsive layout, animations
│   │   └── admin.css           # Dedicated operational styles for Admin Dashboard
│   ├── js/
│   │   ├── main.js             # Cart management (localStorage), drawer, toasts, mobile nav
│   │   ├── menu.js             # Live search, category tabs, veg/non-veg filters
│   │   ├── order.js            # Live cost calculations & AJAX checkout submission
│   │   └── admin.js            # Admin toggles (availability, mark read, async actions)
│   └── images/
│       └── logo.svg            # Bespoke royal golden crest emblem
│
└── templates/
    ├── base.html               # Master layout with navbar, cart slide-over, footer & WhatsApp CTA
    ├── index.html              # Home page: Hero, popular dishes, reviews, opening hours
    ├── menu.html               # Menu page: Search, categories, diet filters, food cards
    ├── checkout.html           # Food checkout: Address, customer info, COD/UPI options
    ├── order_confirmation.html # Order receipt with generated Order ID and tracking timeline
    ├── track_order.html        # Live order lookup by Order Number
    ├── book_table.html         # Table reservation page with guest & seating selections
    ├── reservation_confirmation.html # Booking receipt with reservation code
    ├── about.html              # Restaurant story, mission, and Executive Chef profile
    ├── gallery.html            # Categorized image showcase with interactive lightbox
    ├── contact.html            # Fraser Road Patna address, contact form, Google Maps, WhatsApp
    │
    └── admin/
        ├── layout.html         # Admin sidebar and topbar layout
        ├── login.html          # Secure admin login form
        ├── dashboard.html      # Overview metrics & recent orders table
        ├── items.html          # Food items CRUD & live availability switches
        ├── item_form.html      # Add & Edit dish form
        ├── categories.html     # Category management
        ├── orders.html         # Orders management & status transitions (Pending -> Delivered)
        ├── order_detail.html   # Printable order receipt / invoice view
        ├── reservations.html   # Table reservations manager (Confirm / Cancel)
        └── messages.html       # Customer messages & banquet inquiries inbox
```

---

## 🚀 Quick Setup & Installation Guide

### Prerequisites
- Python 3.9+ installed on your system.
- MySQL Server (e.g., via XAMPP, WampServer, Docker, or standalone MySQL Community Server).

---

### Step 1: Clone or Navigate to the Project Directory
```powershell
cd d:\PROJECT
```

---

### Step 2: (Recommended) Create & Activate a Virtual Environment
```powershell
# Create virtual environment
py -m venv venv

# Activate on Windows PowerShell:
.\venv\Scripts\Activate.ps1
```

---

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

---

### Step 4: Configure Database (`.env`)

Open `.env` (or copy `.env.example` to `.env`) and adjust your MySQL credentials:

```ini
# Flask Configuration
SECRET_KEY=mahfooz_super_secure_key_patna_2025
FLASK_APP=app.py
DEBUG=True

# MySQL Credentials (Default for local XAMPP / WampServer / MySQL):
DB_TYPE=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DB=mahfooz_restaurant

# Set to True to allow automatic fallback to SQLite if MySQL is offline during initial tests:
ALLOW_SQLITE_FALLBACK=True

# Payment Gateway Configuration (Razorpay - India)
RAZORPAY_KEY_ID=rzp_test_YourKeyHere
RAZORPAY_KEY_SECRET=YourSecretKeyHere
RAZORPAY_CURRENCY=INR

# Direct Restaurant UPI ID (For Direct Scan & Pay QR)
RESTAURANT_UPI_ID=mahfoozrestaurant@oksbi
RESTAURANT_UPI_NAME=MAHFOOZ RESTAURANT PATNA
```

---

## 💳 Payment Gateway Setup (Razorpay & Instant UPI)

The website is equipped with **3 complete, real-world payment modes**:

### 1. Razorpay Payment Gateway (UPI, Credit/Debit Cards, NetBanking)
- **Get Free Keys:** Sign up at [https://dashboard.razorpay.com](https://dashboard.razorpay.com) and go to **Settings ➔ API Keys**.
- Generate your **Key ID** (`rzp_test_...` or `rzp_live_...`) and **Key Secret**.
- Paste them into `d:\PROJECT\.env`.
- **Sandbox Testing:** If you run without keys, an interactive **Sandbox Simulator** automatically opens so you can test successful payments and webhook signature verification immediately!

### 2. Direct Scan & Pay UPI QR Code
- Enter your restaurant's official UPI ID in `.env` (e.g. `mahfoozrestaurant@oksbi` or your PhonePe/GPay merchant UPI ID).
- When customers choose this option, the checkout page automatically renders a **live dynamic QR code** with the exact bill amount. Customers scan, pay via any UPI app, and enter their 12-digit UTR reference.

### 3. Cash on Delivery (COD)
- The customer pays in cash or UPI upon food arrival at their doorstep in Patna.


---

### Step 5: Database Setup

You have **two options** to set up the MySQL database:

#### Option A: Automatic Seeding via Python (Fastest)
The application will automatically create all tables and populate realistic gourmet dishes upon first run. You can also run the standalone seeder:
```powershell
py seed_data.py
```

#### Option B: Manual Import via `database.sql`
1. Open **phpMyAdmin** or **MySQL Command Line Client**:
   ```sql
   mysql -u root -p < database.sql
   ```
2. Or in **phpMyAdmin**, click on the **Import** tab and select `d:\PROJECT\database.sql`.

---

### Step 6: Start the Flask Application
```powershell
py app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🔐 Admin Dashboard Access

- **Admin Login URL:** `http://127.0.0.1:5000/admin/login`
- **Default Username:** `admin`
- **Default Password:** `admin123`

*(Password is securely hashed in the database using Werkzeug's Scrypt/PBKDF2 algorithms).*

---

## 🍽️ Key Features Breakdown

### 1. Home Page
- Hero banner with headline *"Delicious Food, Unforgettable Moments"*.
- Quick action buttons: **Order Now** and **Book a Table**.
- Popular dishes cards with pricing, prep time, veg/non-veg tags, and one-click "Add to Cart".
- Authentic customer testimonials from Patna diners.
- Weekly opening hours and location badge.

### 2. Royal Menu
- 8 Categories: **Starters, Biryani, Indian Main Course, Chinese, Pizza, Burgers, Desserts, Beverages**.
- Instant live search by dish name or ingredient.
- Category pills navigation.
- Pure Veg / Non-Veg diet filters.

### 3. Food Ordering System
- Persistent shopping cart stored in client browser (`localStorage`).
- Slide-over Cart Drawer with subtotal, free delivery threshold indicator, and checkout CTA.
- Customer name, phone number, and delivery address verification.
- **Payment Methods:** Cash on Delivery (COD) and UPI on Delivery.
- Order Confirmation page with generated tracking ID (e.g. `MFZ-20251009-XXXX`).
- Live order tracking page (`/track-order`).

### 4. Table Booking System
- Guest name, contact phone, and optional email.
- Date picker with automated minimum date validation.
- Selectable time slots (Lunch, Evening, Prime Dinner).
- Seating areas: *Royal Family Lounge*, *Fine Dining Hall*, *Balcony / Window View*, *Private Booth*.
- Generates a unique Reservation Reference Code (e.g. `TBL-MFZ-XXXX`).

### 5. Admin Dashboard
- **Overview:** Live counter for Gross Revenue, Total Orders, Pending Orders, Table Bookings, Dishes on Menu, and Unread Messages.
- **Menu Items Manager:** Add new dishes, edit prices/descriptions, delete dishes, toggle instant availability (Available / Sold Out).
- **Categories Manager:** Add, view, or organize menu categories.
- **Orders Manager:** Filter orders by status (*Pending, Preparing, Ready, Delivered, Cancelled*), view line items, update delivery and payment statuses.
- **Printable Invoices:** Clean printable customer receipt view.
- **Reservations Manager:** Review customer dining bookings and confirm/cancel status.
- **Customer Messages:** Inbox for inquiries submitted through the Contact form.

---

## 🛡️ Security & Quality Standards

- **SQL Injection Prevention:** All database operations utilize SQLAlchemy ORM parameterized queries.
- **Password Security:** Admin passwords hashed with `werkzeug.security.generate_password_hash`.
- **Session Authentication:** All admin routes protected by the `@admin_required` decorator.
- **Price Verification:** Checkout total is calculated server-side from database prices to prevent client-side price tampering.
- **Environment Isolation:** Secrets and database credentials stored in `.env`.

---

## 📞 Support & Patna Location

**MAHFOOZ Restaurant**  
Heritage Boulevard, Fraser Road, Near Dak Bungalow Crossing, Patna, Bihar – 800001  
**Phone:** +91 98350 45678  
**Email:** contact@mahfoozrestaurant.com  
**WhatsApp:** [Chat with Mahfooz](https://wa.me/919835045678)
