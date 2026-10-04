-- ==========================================================
-- RetailHub Seed Data Script (MySQL)
-- Populates initial categories, users, products, variants, and coupons
-- ==========================================================

USE retailhub_db;

-- 1. Insert Categories
INSERT INTO categories (id, name, slug, description, icon) VALUES
(1, 'Electronics & Audio', 'electronics-audio', 'Headphones, smartwatches, speakers, and portable audio gear.', 'Headphones'),
(2, 'Apparel & Footwear', 'apparel-footwear', 'Athletic wear, jackets, sneakers, and daily essentials.', 'Shirt'),
(3, 'Home & Lifestyle', 'home-lifestyle', 'Smart living, kitchenware, desk accessories, and illumination.', 'Home'),
(4, 'Fitness & Outdoors', 'fitness-outdoors', 'Yoga mats, resistance gear, hydration, and outdoor exploration.', 'Activity'),
(5, 'Accessories & Bags', 'accessories-bags', 'Backpacks, leather wallets, tech organizers, and everyday carry.', 'ShoppingBag')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- 2. Insert Initial Users
INSERT INTO users (id, name, email, password_hash, role, phone) VALUES
('usr-cust-01', 'Lerato Moloi', 'lerato.m@example.com', 'pbkdf2:sha256:test_hash_lerato', 'customer', '+27 82 456 7890'),
('usr-admin-01', 'Thabo Ndlovu (Store Manager)', 'admin@retailhub.co.za', 'pbkdf2:sha256:test_hash_admin', 'admin', '+27 83 987 6543')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- 3. Insert Initial Products
INSERT INTO products (id, sku, name, category_id, brand, price, original_price, cost_price, stock, low_stock_threshold, description, rating, review_count, is_featured, is_active) VALUES
('prod-001', 'RH-ELEC-001', 'AcousticPro ANC Wireless Headphones', 1, 'SonicMaster', 2499.00, 3199.00, 1450.00, 18, 5, 'Hybrid active noise cancellation with 40mm custom graphene dynamic drivers, 45-hour battery life, multi-point Bluetooth 5.3, and ultra-soft memory foam earcups.', 4.9, 128, TRUE, TRUE),
('prod-002', 'RH-ELEC-002', 'PulseFit V4 Pro GPS Smartwatch', 1, 'AeroTech', 3299.00, 3899.00, 1980.00, 4, 6, 'Continuous biometric health tracking with AMOLED always-on display, dual-band GPS routing, 5ATM water resistance, and 14-day battery life.', 4.8, 94, TRUE, TRUE),
('prod-003', 'RH-APP-003', 'HydroShield All-Weather Shell Jacket', 2, 'NordicPeak', 1850.00, 2200.00, 920.00, 22, 5, '20,000mm waterproof breathable 3-layer ripstop membrane jacket with YKK AquaGuard zippers, fully taped seams, and underarm ventilation.', 4.7, 67, FALSE, TRUE),
('prod-004', 'RH-APP-004', 'CloudStride Ultra Foam Runners', 2, 'Veloce', 1699.00, 2099.00, 850.00, 3, 5, 'Engineered mesh running shoes featuring supercritical nitrogen-infused foam midsole for 78% energy return.', 4.9, 210, TRUE, TRUE),
('prod-005', 'RH-HOME-005', 'AuraBeam Smart Desk Lightbar', 3, 'LuminaLab', 899.00, 1150.00, 420.00, 35, 8, 'Asymmetric optical glare-free monitor light bar with wireless rotary dial controller and step-less auto-dimming.', 4.6, 52, FALSE, TRUE),
('prod-006', 'RH-HOME-006', 'Artisan Conical Burr Coffee Grinder', 3, 'BaristaCore', 1450.00, 1799.00, 780.00, 8, 5, '40mm stainless steel conical burr precision grinder with 31 stepped grind settings.', 4.9, 89, TRUE, TRUE),
('prod-007', 'RH-FIT-007', 'ThermaGrip Dual-Density Yoga Mat', 4, 'ZenFlow', 650.00, 799.00, 280.00, 2, 5, '6mm non-toxic natural tree rubber yoga mat with laser-etched alignment guides.', 4.8, 115, FALSE, TRUE),
('prod-008', 'RH-BAG-008', 'Nomad Tech Rolltop 26L Backpack', 5, 'UrbanNomad', 1599.00, 1950.00, 740.00, 14, 5, 'Weatherproof 840D Cordura ballistic nylon backpack with suspended 16" laptop sleeve and magnetic Fidlock buckles.', 4.9, 142, TRUE, TRUE)
ON DUPLICATE KEY UPDATE name=VALUES(name), price=VALUES(price), stock=VALUES(stock);

-- 4. Insert Product Variants (Norman's Mapping Principle)
INSERT INTO product_variants (id, product_id, name, color_hex, size, price_modifier, image_url, stock) VALUES
('var-001-blk', 'prod-001', 'Matte Black', '#18181b', 'Universal', 0.00, 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=80', 10),
('var-001-sil', 'prod-001', 'Silver White', '#e4e4e7', 'Universal', 0.00, 'https://images.unsplash.com/photo-1484704849700-f032a568e944?w=800&auto=format&fit=crop&q=80', 5),
('var-001-blu', 'prod-001', 'Midnight Navy', '#1e293b', 'Universal', 150.00, 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=800&auto=format&fit=crop&q=80', 3),

('var-002-blk', 'prod-002', 'Carbon Stealth', '#18181b', '44mm', 0.00, 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&auto=format&fit=crop&q=80', 2),
('var-002-gld', 'prod-002', 'Titanium Rose', '#fb7185', '40mm', 100.00, 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=800&auto=format&fit=crop&q=80', 2),

('var-003-olv', 'prod-003', 'Forest Olive', '#365314', 'M', 0.00, 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800&auto=format&fit=crop&q=80', 12),
('var-003-blk', 'prod-003', 'Stealth Charcoal', '#27272a', 'L', 0.00, 'https://images.unsplash.com/photo-1544441893-675973e31985?w=800&auto=format&fit=crop&q=80', 10),

('var-004-wht', 'prod-004', 'Cloud White', '#f8fafc', 'UK 9 / US 10', 0.00, 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&auto=format&fit=crop&q=80', 1),
('var-004-blk', 'prod-004', 'Shadow Core', '#18181b', 'UK 10 / US 11', 0.00, 'https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=800&auto=format&fit=crop&q=80', 2)
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- 5. Insert Coupons
INSERT INTO coupons (code, discount_type, discount_value, min_order_amount, is_active) VALUES
('WELCOME10', 'percentage', 10.00, 300.00, TRUE),
('SAVE100', 'fixed', 100.00, 500.00, TRUE),
('FREESHIP', 'free_shipping', 120.00, 450.00, TRUE)
ON DUPLICATE KEY UPDATE discount_value=VALUES(discount_value);
