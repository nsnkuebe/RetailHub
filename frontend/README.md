# RetailHub — HTML, CSS, JavaScript Frontend

This directory contains the standalone, lightweight **HTML5, CSS3, and Vanilla JavaScript** client for RetailHub.

## Stack Overview
- **HTML5**: Semantic tags (`<header>`, `<main>`, `<section>`, `<dialog>`, `<table>`)
- **CSS3**: Modern responsive layout using CSS Grid, Flexbox, custom design tokens/variables, and backdrop blur.
- **JavaScript (ES6+)**: Pure client-side application logic, dynamic DOM rendering, cart calculations, instant filtering, and REST API communication with the Python backend (`/api/*`).

---

## How to Run

### Option A: Standalone Browser Mode (Zero Build Steps)
Simply open `index.html` directly in any web browser (Chrome, Firefox, Safari, Edge). It runs out of the box with sample seed data matching the MySQL database.

### Option B: Connected to Python Backend
1. Start the Python Flask backend:
```bash
cd backend
python app.py
```
2. Open `index.html` with a local web server (e.g., VS Code Live Server or `python -m http.server 8000`).
3. The JavaScript will communicate directly with the Python REST API endpoints at `http://localhost:5000/api`.
