# RetailHub — Python + MySQL Backend Server

This backend implements the full REST API and relational database schema for the **RetailHub Inventory & Order Management System** (CS4431 Human-Computer Interaction Mini-Project).

## Tech Stack
- **Language**: Python 3.10+
- **Web Framework**: Flask 3.0 / Flask-CORS
- **Database Engine**: MySQL 8.0+ 
- **Database Driver**: `mysql-connector-python` with connection pooling

---

## 1. Database Setup (MySQL)

1. Start your local MySQL server (or XAMPP / Docker / Cloud MySQL).
2. Execute the schema migration and seed script:
```bash
mysql -u root -p < schema.sql
mysql -u root -p < seed.sql
```

This creates the database `retailhub_db` with normalized tables:
- `users` (RBAC: customer, admin)
- `categories` (Hierarchy)
- `products` (Catalogue & inventory counts)
- `product_variants` (Norman mapping: color hex, size, custom images)
- `product_images` (Multi-image galleries)
- `orders` (Master orders & financial totals)
- `order_items` (Order line items & stock deduction)
- `order_timeline_events` (Takealot 4-stage tracking status)
- `coupons` (Discount verification engine)

---

## 2. Python Backend Setup

1. Create and activate a Python virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables in `.env`:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=retailhub_db
PORT=5000
```

4. Run the Flask server:
```bash
python app.py
```

The REST API will be accessible on `http://localhost:5000/api`.

---

## 3. REST API Endpoints

### Products & Catalogue
- `GET /api/health` — Health check and DB connection pool status
- `GET /api/products?category=...&search=...&sortBy=...` — Filtered catalogue list
- `GET /api/products/<id>` — Product details with variants & images

### Admin Inventory Management (CRUD)
- `POST /api/admin/products` — Create new product record
- `PUT /api/admin/products/<id>` — Update product details and stock
- `PATCH /api/admin/products/<id>/restock` — Quick batch restock
- `DELETE /api/admin/products/<id>` — Delete product from inventory

### Orders & Tracking
- `POST /api/orders` — Place order, deduct stock, and initialize Takealot timeline
- `GET /api/orders/<id>` — Order status and tracking timeline
- `PATCH /api/admin/orders/<id>/status` — Update order status (Placed -> Processing -> Shipped -> Delivered)
- `POST /api/coupons/validate` — Validate promotional discount codes
