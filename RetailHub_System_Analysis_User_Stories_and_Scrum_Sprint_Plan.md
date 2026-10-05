# RetailHub: System Analysis, User Stories and Scrum Sprint Plan

Based on a code review of the uploaded RetailHub repository (Flask + MySQL backend, vanilla JS frontend). All work below is planned on the existing codebase; no rewrite or new framework is proposed.

## 1. Executive Summary

RetailHub today is a polished **catalogue browser with a partly working admin product form**. The database schema and several backend endpoints are well designed, but most of them are **not connected to the UI**. The backend defines 13 routes, and the frontend calls only two (GET /api/products and POST /api/admin/products). The customer journey (login, cart, checkout, logout) and admin order management cannot currently be completed end to end.

The plan below closes those gaps in **6 two-week sprints (34 user stories, about 150 points)**, with a working, demonstrable increment at the end of each sprint.

## 2. How an E-Commerce System Works, and Where RetailHub Stands

### 2.1 Customer journey

| Stage                           | What a production e-commerce system does                                              | RetailHub today (verified in code)                                                                                                                                                                 |
|---------------------------------|---------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1\. Login                       | Authenticate with hashed passwords, issue a session or token, apply role-based access | **Missing.** No login, register or logout routes. "Customer View / Admin Portal" is a client-side toggle anyone can click. Orders default to usr-cust-01. Seeded password hashes are placeholders. |
| 2\. Browse and search           | Server-side search, filter and sort                                                   | Backend supports it, but the UI filters an in-memory array. If the API is down, only 4 fallback products show (seed has 8).                                                                        |
| 3\. Product detail and variants | Gallery, variant picker, price modifier, per-variant stock                            | Tables and API data exist. The detail modal markup is in index.html but app.js never opens it. Variants are unused.                                                                                |
| 4\. Cart                        | Add, edit, remove, stock limits, persistence, recalculation                           | In-memory only (lost on refresh). Quantity is capped at stock. No variant support. Subtotal only.                                                                                                  |
| 5\. Checkout                    | Address, shipping and tax, coupon, payment choice, order creation                     | The "Proceed to Checkout" button has **no click handler**. POST /api/orders and POST /api/coupons/validate exist but are never called.                                                             |
| 6\. Order creation              | Atomic, priced on the server, stock-checked                                           | Transaction is good, but the server **trusts client prices and totals**. GREATEST(0, stock - qty) silently hides overselling. Variant stock is never decremented.                                  |
| 7\. Tracking                    | Customer sees a status timeline and order history                                     | GET /api/orders/\<id\> returns a timeline. There is no UI and no "my orders" list endpoint.                                                                                                        |
| 8\. Logout                      | End session, clear private state                                                      | Not present.                                                                                                                                                                                       |

### 2.2 Admin: inventory CRUD

| Operation   | Current state                                                                                                                                                                                                        |
|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Create**  | Works end to end, but category is always saved as id 1 (the dropdown is ignored). The image is stored in browser localStorage instead of using the existing /api/upload, which is also hard-coded to localhost:5050. |
| **Read**    | Admin table reuses the public list. Inactive products are hidden and there is no pagination.                                                                                                                         |
| **Update**  | PUT endpoint exists, but there is no Edit button. Omitted fields are overwritten with NULL or 0 instead of being left unchanged.                                                                                     |
| **Delete**  | The UI only removes the row from memory, so it **reappears on refresh**. The real DELETE hard-deletes and will fail with a foreign-key error for any product that was ever ordered.                                  |
| **Restock** | The "+10 Stock" button changes memory only. The PATCH endpoint is never called.                                                                                                                                      |

### 2.3 Admin: order management

- There is no list-orders endpoint and no admin orders screen.

- PATCH /api/admin/orders/\<id\>/status updates orders.status but **not** order_timeline_events, so customer tracking would go stale.

- Any transition is accepted (for example Delivered back to Placed). Cancelling does not return stock.

- The analytics feature (FR-10) claimed in the code header has no backend route.

### 2.4 Cross-cutting findings

- **Secrets:** backend/.env is committed, and check_images.py contains a hard-coded database password. Rotate these credentials.

- **Repository hygiene:** the venv/ folder is committed (it is most of the 13 MB archive), and there is no .gitignore.

- **Configuration drift:** .env says PORT=5000, while the code and README say 5050. The DB port is 3307 in .env.example but defaults to 3306 in db.py.

- **Security:** CORS is \*, Flask runs with debug=True, and product names are injected with innerHTML unescaped (stored XSS risk).

- **Quality:** no automated tests. The README lists FR-1 to FR-10 as supported, but FR-4, 5, 7, 8 and 10 are not wired end to end.

- **Strengths to keep:** a normalised schema with FKs and CHECK constraints, connection pooling, a transactional order insert, a coupon engine, a timeline model, and a responsive UI.

## 3. Scrum Framework

**Product Goal:** *A customer can log in, shop, check out and log out securely, and an admin can manage inventory and fulfil orders, all on the existing RetailHub stack.*

**Personas (taken from the seed data):** Lerato Moloi (customer) and Thabo Ndlovu (store manager and admin).

**Assumptions (adjust to your team):** 3 to 5 developers, 2-week sprints, estimated velocity of about 25 points (re-baseline after Sprint 1). Points are Fibonacci and should be re-estimated by the team in Planning Poker.

| Role          | Responsibility                                         |
|---------------|--------------------------------------------------------|
| Product Owner | Owns and orders the backlog, accepts stories at Review |
| Scrum Master  | Facilitates events, removes impediments                |
| Developers    | Estimate, build, test, and deliver a Done increment    |

**Events per sprint:** Planning (sprint goal and commitment), Daily Scrum (15 min), Backlog Refinement (mid-sprint, next sprint's stories to Ready), Review (demo on the running system), Retrospective.

**Definition of Ready:** story has acceptance criteria, an estimate of 8 points or fewer, no unresolved dependency, and a UI sketch when relevant.

**Definition of Done:** acceptance criteria pass; API endpoint tested with pytest; no hard-coded secrets; input validated server-side; output escaped in the UI; works in Chrome and Firefox and on mobile width; merged to main via reviewed pull request; README updated; demoed at Review.

## 4. Epics

| Epic | Theme                             |
|------|-----------------------------------|
| E0   | Foundation and technical debt     |
| E1   | Authentication and accounts       |
| E2   | Catalogue and cart                |
| E3   | Checkout and customer orders      |
| E4   | Inventory management (admin CRUD) |
| E5   | Order management (admin)          |
| E6   | Quality, security and release     |

## 5. Sprint Plan with User Stories

Priority uses MoSCoW (M = Must, S = Should, C = Could). AC = acceptance criteria.

### Sprint 1: Foundation and Authentication (23 pts)

**Goal:** Users can securely log in and out, and roles are enforced on the server.

**US-01 (E0, 3 pts, M).** As a developer, I want secrets and build artefacts out of the repository, so that credentials are not leaked and setup is repeatable. *AC:* venv/, .env, uploads/ in .gitignore; password removed from check_images.py; DB password rotated; one agreed PORT and DB_PORT across .env.example, db.py, README and app.js; API_BASE read from one config constant.

**US-02 (E1, 3 pts, M).** As a new customer, I want to register with name, email and password, so that I can place orders. *AC:* POST /api/auth/register; unique email enforced with a clear error; password hashed with Werkzeug; minimum password rules validated on client and server.

**US-03 (E1, 5 pts, M).** As a customer or admin, I want to log in with email and password, so that I access my own account. *AC:* POST /api/auth/login verifies the hash and returns a signed token (PyJWT) with id and role; wrong credentials show a generic error; login form replaces the role toggle; token survives page reload.

**US-04 (E1, 2 pts, M).** As a logged-in user, I want to log out, so that nobody else uses my session on a shared device. *AC:* logout clears token and in-memory state; the UI returns to the guest catalogue; protected calls then return 401.

**US-05 (E1, 5 pts, M).** As the store owner, I want admin endpoints to be admin-only, so that customers cannot change stock or orders. *AC:* @admin_required on every /api/admin/\* route; 401 without token and 403 for customers; Admin Portal tab visible only to admins; userId taken from the token, never the request body.

**US-06 (E1, 2 pts, M).** As a tester, I want seeded accounts with real hashed passwords, so that I can demo both roles. *AC:* seed.sql or a seed script creates Lerato (customer) and Thabo (admin) with hashes generated by Werkzeug; documented in README.

**US-07 (E0, 3 pts, S).** As a developer, I want one API client module, so that auth headers and errors are handled consistently. *AC:* api.js wraps fetch with token header, JSON parsing and 401 handling; app.js split into api.js, auth.js, cart.js, admin.js.

### Sprint 2: Admin Inventory CRUD on the Real Database (24 pts)

**Goal:** Every inventory action persists in MySQL and survives a refresh.

**US-08 (E4, 3 pts, M).** As Thabo, I want the inventory table to show live database stock, so that I can trust what I see. *AC:* new GET /api/admin/products includes inactive items; low-stock and out-of-stock badges use low_stock_threshold; search box filters the table.

**US-09 (E4, 5 pts, M).** As Thabo, I want to create a product with the correct category and image, so that it appears properly in the shop. *AC:* form sends the real categoryId (categories loaded from API); image uploaded through /api/upload and URL stored in product_images; duplicate SKU returns a readable error; negative price or stock rejected.

**US-10 (E4, 5 pts, M).** As Thabo, I want to edit a product, so that I can fix prices, descriptions and stock. *AC:* Edit button opens the form pre-filled; PUT updates only the supplied fields; 404 for unknown id; the table and the shop refresh after saving.

**US-11 (E4, 3 pts, M).** As Thabo, I want to restock with a quantity I choose, so that deliveries are recorded accurately. *AC:* quantity prompt replaces the fixed +10; calls PATCH .../restock; quantity must be a positive integer; the new stock is shown from the server response.

**US-12 (E4, 5 pts, M).** As Thabo, I want deleting a product to archive it safely, so that past orders stay intact. *AC:* confirmation dialog; DELETE sets is_active = FALSE (soft delete); archived items are hidden from customers and can be restored; hard delete allowed only when the product has no order_items.

**US-13 (E4, 3 pts, S).** As a developer, I want consistent validation and error responses, so that the UI can show clear messages. *AC:* shared validator for product payloads; errors return {success:false, error} with correct 400, 404 or 409 codes; no raw SQL errors reach the client.

### Sprint 3: Catalogue, Product Detail and Cart (26 pts)

**Goal:** Lerato can open a product, choose a variant and keep a reliable cart.

**US-14 (E4, 5 pts, S).** As Thabo, I want to manage product variants (colour, size, price modifier, stock), so that customers can choose options. *AC:* create, edit and delete variants from the product form; the sum of variant stock is shown against product stock; an image is required per variant.

**US-15 (E2, 5 pts, M).** As Lerato, I want a product detail view with images and description, so that I can decide before buying. *AC:* clicking a card opens the existing modal (loaded via GET /api/products/\<id\>); gallery, rating, stock status and brand are shown; the modal is keyboard-closable.

**US-16 (E2, 5 pts, M).** As Lerato, I want to pick a colour or size, so that I buy the exact item. *AC:* variant swatches update the image and price (base plus priceModifier); out-of-stock variants are disabled; the chosen variant is stored on the cart line.

**US-17 (E2, 3 pts, M).** As Lerato, I want to add to cart with stock limits, so that I cannot order more than exists. *AC:* quantity capped at variant stock; the same product with different variants makes separate lines; clear toast on limit.

**US-18 (E2, 5 pts, M).** As Lerato, I want my cart to survive refresh and login, so that I do not lose my selections. *AC:* cart saved to localStorage per user; guest cart merged on login; cleared on logout.

**US-19 (E2, 3 pts, M).** As Lerato, I want to edit quantities, remove items and see the subtotal, so that I control my basket. *AC:* +/- and remove update totals in the chosen currency; stock re-checked when the cart opens; sold-out items flagged.

### Sprint 4: Checkout and Order Placement (26 pts)

**Goal:** A logged-in customer can complete a checkout and receive an order number.

**US-20 (E3, 5 pts, M).** As Lerato, I want to enter delivery details at checkout, so that my order reaches me. *AC:* "Proceed to Checkout" requires login (redirects to login, then back); form pre-filled from profile; required fields, South African postal code and phone validated; multi-step with progress indicator.

**US-21 (E3, 3 pts, S).** As Lerato, I want to apply a coupon, so that I get promised discounts. *AC:* calls POST /api/coupons/validate; expiry (expires_at) is honoured, which the current endpoint ignores; WELCOME10, SAVE100 and FREESHIP behave as seeded; the message shows the minimum order when not met.

**US-22 (E3, 5 pts, M).** As the store owner, I want the server to calculate all prices, so that customers cannot tamper with totals. *AC:* POST /api/orders accepts only product ids, variants and quantities; subtotal, shipping fee, 15% VAT, discount and total are computed from database prices; client totals are ignored.

**US-23 (E3, 3 pts, M).** As Lerato, I want to choose a payment method, so that I can pay my preferred way. *AC:* credit card, instant EFT, cash on delivery and mobile money from the schema enum; payments are **simulated** with a status field; card details are never stored.

**US-24 (E3, 8 pts, M).** As Lerato, I want my order to be rejected if stock ran out, so that I am never charged for unavailable items. *AC:* stock checked with SELECT ... FOR UPDATE inside the transaction; 409 listing unavailable items; variant stock decremented as well as product stock; remove GREATEST(0, ...); two simultaneous orders for the last unit cannot both succeed (tested).

**US-25 (E3, 2 pts, S).** As Lerato, I want an order confirmation, so that I know it worked. *AC:* confirmation screen shows order number, items, total and estimated delivery; cart is cleared only after success.

### Sprint 5: Order Tracking and Admin Order Management (25 pts)

**Goal:** Customers can track orders; Thabo can fulfil and cancel them.

**US-26 (E3, 5 pts, M).** As Lerato, I want to see my order history and tracking timeline, so that I know where my parcel is. *AC:* GET /api/orders returns only the caller's orders; timeline UI shows Placed, Processing, Shipped, Delivered with the current step highlighted; another user's order returns 403.

**US-27 (E5, 5 pts, M).** As Thabo, I want a list of all orders with filters, so that I can see what needs action. *AC:* GET /api/admin/orders with status, date and order-number search plus pagination; table shows customer, total, payment method and status; new orders highlighted.

**US-28 (E5, 5 pts, M).** As Thabo, I want to move an order through the fulfilment stages, so that customers see accurate progress. *AC:* only valid transitions allowed (Placed to Processing to Shipped to Delivered); the PATCH also updates order_timeline_events (is_completed, is_current, timestamp) in one transaction; invalid transition returns 400.

**US-29 (E5, 5 pts, M).** As Thabo or Lerato, I want to cancel an order before it ships, so that mistakes can be corrected. *AC:* allowed only in Placed or Processing; stock restored in the same transaction; timeline shows Cancelled; the customer can cancel only their own orders.

**US-30 (E5, 5 pts, S).** As Thabo, I want a dashboard of sales and low stock, so that I can reorder in time. *AC:* GET /api/admin/analytics returns revenue, order count by status, inventory value at cost, and items at or below threshold; shown as cards plus a low-stock list.

### Sprint 6: Hardening, Testing and Release (21 pts)

**Goal:** A secure, tested, deployable release candidate accepted by the Product Owner.

**US-31 (E2, 3 pts, S).** As Lerato, I want fast server-side search, filter and sort, so that large catalogues stay usable. *AC:* UI calls GET /api/products with debounced input; the sortBy=newest option is exposed in the UI; empty-state message shown.

**US-32 (E6, 5 pts, M).** As the store owner, I want standard web security applied, so that customer data is protected. *AC:* all dynamic text escaped (no unescaped innerHTML); CORS limited to the frontend origin; debug=False; login rate-limited; upload checks size and type.

**US-33 (E6, 5 pts, M).** As the team, I want automated tests, so that regressions are caught. *AC:* pytest suite covers auth, RBAC, inventory CRUD, order creation (including the stock race) and status transitions; one end-to-end smoke script runs login, add to cart, checkout, logout.

**US-34 (E6, 3 pts, S).** As a user on any device, I want an accessible, responsive interface, so that I can shop easily. *AC:* labelled form fields, focus order, colour contrast checked; usable at 360 px width; consistent loading and error states.

**US-35 (E6, 5 pts, S).** As the store owner, I want the system deployable, so that it can go live. *AC:* run with gunicorn; environment-based configuration; DB migration steps documented; backup and restore tested; release notes written.

About 10% of each sprint should be left unplanned for bugs and review feedback. UAT happens at the Sprint 6 Review.

## 6. Sprint Summary and Roadmap

| Sprint | Weeks | Goal                          | Points | Demo-able increment                                |
|--------|-------|-------------------------------|--------|----------------------------------------------------|
| 1      | 1-2   | Foundation and auth           | 23     | Register, log in, log out, admin-only API          |
| 2      | 3-4   | Admin inventory CRUD          | 24     | Create, edit, restock, archive, all persisted      |
| 3      | 5-6   | Catalogue and cart            | 26     | Product detail, variants, persistent cart          |
| 4      | 7-8   | Checkout                      | 26     | Full checkout with coupon and stock-safe order     |
| 5      | 9-10  | Tracking and order management | 25     | Order history, admin fulfilment, cancel, dashboard |
| 6      | 11-12 | Hardening and release         | 21     | Tested, secured, deployable release                |

After Sprint 4 the full customer path (login, add to cart, checkout, logout) works end to end. After Sprint 5 both admin processes (inventory and orders) are complete.

**Dependencies:** Sprint 1 (auth) blocks all later sprints. US-14 (variants) blocks US-16. US-22 and US-24 block US-25, US-26 and US-29.

## 7. Risks and Recommendations

| Risk                                                             | Mitigation                                                                                                                        |
|------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------|
| Velocity unknown for a new team                                  | Re-plan after Sprint 1 and move Should/Could stories rather than cutting Musts                                                    |
| Checkout stock race conditions                                   | US-24 includes a concurrency test; use row locks                                                                                  |
| Real payments out of scope                                       | Keep payment simulated and document it as a future epic                                                                           |
| Single 570-line app.js slows parallel work                       | Split into modules in Sprint 1 (US-07)                                                                                            |
| Currency confusion (prices stored in ZAR, UI defaults to Maluti) | Store ZAR as the base; display conversion only; the Maluti is pegged 1:1 to the Rand, so confirm the intended default with the PO |

**Backlog items for future releases:** product reviews and ratings, wishlist, password reset by email, real payment gateway, stock-adjustment audit log, and returns or refunds.

**Immediate action before Sprint 1:** rotate the database password found in the repository and remove it from Git history.
