"""
RetailHub Main Application Server (app.py)
CS4431: Human-Computer Interaction & E-Commerce Systems
Tech Stack: Python 3, Flask, MySQL 8.0, RESTful Architecture
Supports:
  - FR-1: Real-time Search & Instant Query Processing
  - FR-2: Category Navigation & Dynamic Attribute Filtering
  - FR-3: Product Detail View & Variant Color Mapping
  - FR-4: Shopping Cart State Management & Price Recalculation
  - FR-5: Multi-Step Checkout with Address & Payment Validation
  - FR-6: Order Generation & Stock Deduction Transactions
  - FR-7: Takealot-style Real-time Order Tracking Timeline
  - FR-8: Admin Order Fulfillment Pipeline (Placed -> Processing -> Shipped -> Delivered)
  - FR-9: Admin Inventory Full CRUD Management
  - FR-10: Executive Sales & Inventory Valuation Analytics
"""

import os
import uuid
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS

try:
    from db import execute_query, execute_mutation, get_db_connection, db_pool
except ImportError:
    from .db import execute_query, execute_mutation, get_db_connection, db_pool

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Health & Diagnostic endpoint
@app.route("/api/health", methods=["GET"])
def health_check():
    """System health check and MySQL connection status."""
    db_status = "connected" if db_pool is not None else "disconnected (check .env)"
    return jsonify({
        "status": "online",
        "service": "RetailHub Python REST API",
        "version": "1.0.0",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })


# --------------------------------------------------------------------------
# 1. Product Catalogue Endpoints (FR-1, FR-2, FR-3)
# --------------------------------------------------------------------------
@app.route("/api/products", methods=["GET"])
def get_products():
    """
    Fetch products with search, category filtering, and sorting.
    Query Params:
      - category: Name or 'All'
      - search: Search keyword
      - sortBy: 'featured' | 'price-asc' | 'price-desc' | 'rating' | 'newest'
    """
    category = request.args.get("category", "All")
    search = request.args.get("search", "").strip()
    sort_by = request.args.get("sortBy", "featured")

    try:
        query = """
            SELECT 
                p.id, p.sku, p.name, p.brand, p.price, p.original_price as originalPrice,
                p.cost_price as costPrice, p.stock, p.low_stock_threshold as lowStockThreshold,
                p.description, p.rating, p.review_count as reviewCount, p.is_featured as isFeatured,
                c.name as category
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.is_active = TRUE
        """
        params = []

        if category != "All":
            query += " AND c.name = %s"
            params.append(category)

        if search:
            query += " AND (p.name LIKE %s OR p.sku LIKE %s OR p.brand LIKE %s OR p.description LIKE %s)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param, search_param])

        if sort_by == "price-asc":
            query += " ORDER BY p.price ASC"
        elif sort_by == "price-desc":
            query += " ORDER BY p.price DESC"
        elif sort_by == "rating":
            query += " ORDER BY p.rating DESC"
        elif sort_by == "newest":
            query += " ORDER BY p.created_at DESC"
        else:
            query += " ORDER BY p.is_featured DESC, p.created_at DESC"

        products = execute_query(query, tuple(params))

        # Fetch variants and images for each product
        for prod in products:
            variants = execute_query(
                "SELECT id, name, color_hex as colorHex, size, price_modifier as priceModifier, image_url as image, stock FROM product_variants WHERE product_id = %s",
                (prod["id"],)
            )
            images = execute_query(
                "SELECT image_url FROM product_images WHERE product_id = %s ORDER BY display_order ASC",
                (prod["id"],)
            )
            prod["variants"] = variants
            prod["images"] = [img["image_url"] for img in images] if images else [
                "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=80"
            ]

        return jsonify({
            "success": True,
            "count": len(products),
            "products": products
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/products/<string:product_id>", methods=["GET"])
def get_product_detail(product_id):
    """Retrieve detailed product record by ID."""
    try:
        query = """
            SELECT 
                p.id, p.sku, p.name, p.brand, p.price, p.original_price as originalPrice,
                p.cost_price as costPrice, p.stock, p.low_stock_threshold as lowStockThreshold,
                p.description, p.rating, p.review_count as reviewCount, p.is_featured as isFeatured,
                c.name as category
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.id = %s
        """
        prod = execute_query(query, (product_id,), fetch_one=True)
        if not prod:
            return jsonify({"success": False, "error": "Product not found"}), 404

        variants = execute_query(
            "SELECT id, name, color_hex as colorHex, size, price_modifier as priceModifier, image_url as image, stock FROM product_variants WHERE product_id = %s",
            (product_id,)
        )
        images = execute_query(
            "SELECT image_url FROM product_images WHERE product_id = %s ORDER BY display_order ASC",
            (product_id,)
        )
        prod["variants"] = variants
        prod["images"] = [img["image_url"] for img in images] if images else []

        return jsonify({"success": True, "product": prod}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# --------------------------------------------------------------------------
# 2. Admin Inventory CRUD Operations (FR-9)
# --------------------------------------------------------------------------
@app.route("/api/admin/products", methods=["POST"])
def admin_create_product():
    """Create a new product in the MySQL inventory."""
    data = request.json or {}
    sku = data.get("sku", "").strip().upper()
    name = data.get("name", "").strip()
    category_id = data.get("categoryId", 1)
    brand = data.get("brand", "").strip()
    price = float(data.get("price", 0))
    cost_price = float(data.get("costPrice", 0))
    stock = int(data.get("stock", 0))
    low_stock_threshold = int(data.get("lowStockThreshold", 5))
    description = data.get("description", "").strip()

    if not sku or not name or price < 0:
        return jsonify({"success": False, "error": "SKU, Name, and valid Price are required"}), 400

    prod_id = f"prod-{uuid.uuid4().hex[:8]}"

    try:
        query = """
            INSERT INTO products (id, sku, name, category_id, brand, price, cost_price, stock, low_stock_threshold, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        execute_mutation(query, (
            prod_id, sku, name, category_id, brand, price, cost_price, stock, low_stock_threshold, description
        ))

        # Add primary image if provided
        image_url = data.get("imageUrl")
        if image_url:
            execute_mutation(
                "INSERT INTO product_images (product_id, image_url, display_order) VALUES (%s, %s, 0)",
                (prod_id, image_url)
            )

        return jsonify({
            "success": True,
            "message": "Product created successfully in MySQL inventory",
            "productId": prod_id
        }), 201

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/admin/products/<string:product_id>", methods=["PUT"])
def admin_update_product(product_id):
    """Update existing product details and stock level."""
    data = request.json or {}
    try:
        query = """
            UPDATE products
            SET name = %s, sku = %s, brand = %s, price = %s, cost_price = %s, stock = %s,
                low_stock_threshold = %s, description = %s
            WHERE id = %s
        """
        execute_mutation(query, (
            data.get("name"),
            data.get("sku"),
            data.get("brand"),
            float(data.get("price", 0)),
            float(data.get("costPrice", 0)),
            int(data.get("stock", 0)),
            int(data.get("lowStockThreshold", 5)),
            data.get("description", ""),
            product_id
        ))

        return jsonify({"success": True, "message": "Product updated successfully"}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/admin/products/<string:product_id>/restock", methods=["PATCH"])
def admin_restock_product(product_id):
    """Quick restock increment endpoint."""
    data = request.json or {}
    increment = int(data.get("quantity", 10))
    try:
        query = "UPDATE products SET stock = stock + %s WHERE id = %s"
        execute_mutation(query, (increment, product_id))
        return jsonify({"success": True, "message": f"Stock increased by {increment}"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/admin/products/<string:product_id>", methods=["DELETE"])
def admin_delete_product(product_id):
    """Delete a product from the catalogue."""
    try:
        execute_mutation("DELETE FROM products WHERE id = %s", (product_id,))
        return jsonify({"success": True, "message": "Product removed from inventory"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# --------------------------------------------------------------------------
# 3. Order Processing & Takealot Tracking Endpoints (FR-5, FR-6, FR-7)
# --------------------------------------------------------------------------
@app.route("/api/orders", methods=["POST"])
def create_order():
    """
    Processes customer checkout:
      1. Inserts master order record.
      2. Inserts line items and deducts stock transactionally.
      3. Generates the Takealot 4-stage tracking timeline.
    """
    data = request.json or {}
    items = data.get("items", [])
    shipping = data.get("shippingAddress", {})
    
    if not items or not shipping.get("fullName") or not shipping.get("addressLine1"):
        return jsonify({"success": False, "error": "Invalid order items or shipping details"}), 400

    order_id = f"ord-{uuid.uuid4().hex[:8]}"
    order_number = f"RH-2026-{uuid.uuid4().hex[:4].upper()}"

    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            # 1. Insert Master Order
            cursor.execute("""
                INSERT INTO orders (
                    id, order_number, user_id, customer_name, customer_email, customer_phone,
                    shipping_address_line1, shipping_address_line2, shipping_city, shipping_province,
                    shipping_postal_code, shipping_country, payment_method, subtotal, shipping_fee,
                    discount_amount, tax_amount, total_amount, status, coupon_code, estimated_delivery
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                order_id,
                order_number,
                data.get("userId", "usr-cust-01"),
                shipping.get("fullName"),
                shipping.get("email"),
                shipping.get("phone"),
                shipping.get("addressLine1"),
                shipping.get("addressLine2", ""),
                shipping.get("city"),
                shipping.get("provinceState"),
                shipping.get("postalCode"),
                shipping.get("country", "South Africa"),
                data.get("paymentMethod", "credit_card"),
                float(data.get("subtotal", 0)),
                float(data.get("shippingFee", 0)),
                float(data.get("discountAmount", 0)),
                float(data.get("taxAmount", 0)),
                float(data.get("totalAmount", 0)),
                "Placed",
                data.get("couponCode", ""),
                (datetime.now() + timedelta(days=3)).strftime("%d %b %Y")
            ))

            # 2. Insert Order Items & Deduct Stock
            for it in items:
                cursor.execute("""
                    INSERT INTO order_items (order_id, product_id, product_name, variant_name, quantity, unit_price, total_price)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    order_id,
                    it.get("productId"),
                    it.get("productName"),
                    it.get("variantName", ""),
                    it.get("quantity", 1),
                    float(it.get("unitPrice", 0)),
                    float(it.get("totalPrice", 0))
                ))

                # Decrement inventory stock
                cursor.execute(
                    "UPDATE products SET stock = GREATEST(0, stock - %s) WHERE id = %s",
                    (it.get("quantity", 1), it.get("productId"))
                )

            # 3. Create Timeline Events
            timeline_events = [
                ("Placed", "Order Placed & Confirmed", "Payment verified and order transmitted to warehouse", True, True, "Just Now"),
                ("Processing", "Warehouse Processing & QC", "Items picked, scanned, and packed into branded parcel", False, False, "Pending"),
                ("Shipped", "Courier Transit (Takealot Model)", "Handed to courier with live waypoint scanning", False, False, "Pending"),
                ("Delivered", "Delivered & Signed", "Doorstep delivery completed with signature capture", False, False, "Est. 3 Days")
            ]

            for ev in timeline_events:
                cursor.execute("""
                    INSERT INTO order_timeline_events (order_id, status, title, description, is_completed, is_current, event_timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (order_id, ev[0], ev[1], ev[2], ev[3], ev[4], ev[5]))

            conn.commit()
            return jsonify({
                "success": True,
                "orderId": order_id,
                "orderNumber": order_number,
                "message": "Order successfully placed and inventory updated."
            }), 201

        except Exception as e:
            conn.rollback()
            return jsonify({"success": False, "error": str(e)}), 500
        finally:
            cursor.close()


@app.route("/api/orders/<string:order_id>", methods=["GET"])
def get_order_tracking(order_id):
    """Retrieve full order details and Takealot timeline status."""
    try:
        order = execute_query("SELECT * FROM orders WHERE id = %s OR order_number = %s", (order_id, order_id), fetch_one=True)
        if not order:
            return jsonify({"success": False, "error": "Order not found"}), 404

        items = execute_query("SELECT * FROM order_items WHERE order_id = %s", (order["id"],))
        timeline = execute_query("SELECT * FROM order_timeline_events WHERE order_id = %s ORDER BY id ASC", (order["id"],))

        order["items"] = items
        order["timeline"] = timeline
        return jsonify({"success": True, "order": order}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/admin/orders/<string:order_id>/status", methods=["PATCH"])
def admin_update_order_status(order_id):
    """Transition order status through fulfillment pipeline."""
    data = request.json or {}
    new_status = data.get("status")
    allowed_statuses = ["Placed", "Processing", "Shipped", "Delivered", "Cancelled"]

    if new_status not in allowed_statuses:
        return jsonify({"success": False, "error": "Invalid status transition"}), 400

    try:
        execute_mutation("UPDATE orders SET status = %s WHERE id = %s", (new_status, order_id))
        return jsonify({"success": True, "message": f"Order status updated to {new_status}"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# --------------------------------------------------------------------------
# 4. Promo Coupons Engine
# --------------------------------------------------------------------------
@app.route("/api/coupons/validate", methods=["POST"])
def validate_coupon():
    """Validates coupon code against order subtotal."""
    data = request.json or {}
    code = data.get("code", "").strip().upper()
    subtotal = float(data.get("subtotal", 0))

    try:
        coupon = execute_query("SELECT * FROM coupons WHERE code = %s AND is_active = TRUE", (code,), fetch_one=True)
        if not coupon:
            return jsonify({"valid": False, "message": "Invalid or expired coupon code"}), 404

        if subtotal < float(coupon["min_order_amount"]):
            return jsonify({
                "valid": False,
                "message": f"Minimum order of R{coupon['min_order_amount']:.2f} required for this coupon"
            }), 400

        discount = 0.0
        if coupon["discount_type"] == "percentage":
            discount = subtotal * (float(coupon["discount_value"]) / 100.0)
        elif coupon["discount_type"] == "fixed":
            discount = float(coupon["discount_value"])
        elif coupon["discount_type"] == "free_shipping":
            discount = float(coupon["discount_value"])

        return jsonify({
            "valid": True,
            "code": code,
            "discountType": coupon["discount_type"],
            "discountValue": float(coupon["discount_value"]),
            "discountAmount": round(discount, 2),
            "message": f"Coupon {code} applied successfully!"
        }), 200

    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 RetailHub Python Backend REST Server starting on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=True)
