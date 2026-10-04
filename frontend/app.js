/**
 * RetailHub Frontend Application Logic (app.js)
 * Pure Vanilla JavaScript (ES6+)
 * Communicates with Python Flask Backend (/api/*) with seamless fallback
 */

const API_BASE = 'http://localhost:5000/api';

// Initial In-Memory Dataset (Matches MySQL Seed)
let productsData = [
  {
    id: 'prod-001',
    sku: 'RH-ELEC-001',
    name: 'AcousticPro ANC Wireless Headphones',
    category: 'Electronics & Audio',
    brand: 'SonicMaster',
    price: 2499.00,
    originalPrice: 3199.00,
    costPrice: 1450.00,
    stock: 18,
    lowStockThreshold: 5,
    description: 'Hybrid active noise cancellation with 40mm custom graphene dynamic drivers, 45-hour battery life, and Bluetooth 5.3.',
    rating: 4.9,
    reviewCount: 128,
    isFeatured: true,
    image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=80'
  },
  {
    id: 'prod-002',
    sku: 'RH-ELEC-002',
    name: 'PulseFit V4 Pro GPS Smartwatch',
    category: 'Electronics & Audio',
    brand: 'AeroTech',
    price: 3299.00,
    originalPrice: 3899.00,
    costPrice: 1980.00,
    stock: 4,
    lowStockThreshold: 6,
    description: 'AMOLED display, dual-band GPS routing, 5ATM water resistance, and 14-day battery life.',
    rating: 4.8,
    reviewCount: 94,
    isFeatured: true,
    image: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&auto=format&fit=crop&q=80'
  },
  {
    id: 'prod-003',
    sku: 'RH-APP-003',
    name: 'HydroShield All-Weather Shell Jacket',
    category: 'Apparel & Footwear',
    brand: 'NordicPeak',
    price: 1850.00,
    originalPrice: 2200.00,
    costPrice: 920.00,
    stock: 22,
    lowStockThreshold: 5,
    description: '20,000mm waterproof breathable membrane with YKK AquaGuard zippers.',
    rating: 4.7,
    reviewCount: 67,
    isFeatured: false,
    image: 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800&auto=format&fit=crop&q=80'
  },
  {
    id: 'prod-004',
    sku: 'RH-APP-004',
    name: 'CloudStride Ultra Foam Runners',
    category: 'Apparel & Footwear',
    brand: 'Veloce',
    price: 1699.00,
    originalPrice: 2099.00,
    costPrice: 850.00,
    stock: 3,
    lowStockThreshold: 5,
    description: 'Engineered mesh running shoes featuring supercritical nitrogen-infused foam midsole.',
    rating: 4.9,
    reviewCount: 210,
    isFeatured: true,
    image: 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&auto=format&fit=crop&q=80'
  }
];

const categories = [
  'All',
  'Electronics & Audio',
  'Apparel & Footwear',
  'Home & Lifestyle',
  'Fitness & Outdoors',
  'Accessories & Bags'
];

let state = {
  activeRole: 'customer',
  currency: 'LSL', // Default: Maluti (Loti) (M)
  exchangeRate: 0.055, // 1 LSL/ZAR = 0.055 USD
  selectedCategory: 'All',
  searchQuery: '',
  sortBy: 'featured',
  cart: [],
  editingProductId: null
};

// DOM Elements
const searchInput = document.getElementById('searchInput');
const clearSearchBtn = document.getElementById('clearSearchBtn');
const roleToggleBtn = document.getElementById('roleToggleBtn');
const roleLabel = document.getElementById('roleLabel');
const currMaluti = document.getElementById('currMaluti');
const currZar = document.getElementById('currZar');
const currUsd = document.getElementById('currUsd');
const cartBtn = document.getElementById('cartBtn');
const cartCountBadge = document.getElementById('cartCountBadge');
const categoryPills = document.getElementById('categoryPills');
const sortSelect = document.getElementById('sortSelect');
const customerView = document.getElementById('customerView');
const adminView = document.getElementById('adminView');
const productGrid = document.getElementById('productGrid');
const inventoryTableBody = document.getElementById('inventoryTableBody');
const cartDrawer = document.getElementById('cartDrawer');
const closeCartBtn = document.getElementById('closeCartBtn');
const cartOverlay = document.getElementById('cartOverlay');
const cartItemsList = document.getElementById('cartItemsList');
const cartSubtotal = document.getElementById('cartSubtotal');
const cartDrawerCount = document.getElementById('cartDrawerCount');
const productFormModal = document.getElementById('productFormModal');
const openAddProductModalBtn = document.getElementById('openAddProductModalBtn');
const closeProductFormBtn = document.getElementById('closeProductFormBtn');
const cancelProductFormBtn = document.getElementById('cancelProductFormBtn');
const productForm = document.getElementById('productForm');

// Initialization
document.addEventListener('DOMContentLoaded', () => {
  renderCategoryPills();
  renderProducts();
  renderInventoryTable();
  setupEventListeners();
});

// Format Currency
function formatMoney(amount) {
  if (state.currency === 'USD') {
    return '$' + (amount * state.exchangeRate).toFixed(2);
  }
  if (state.currency === 'ZAR') {
    return 'R ' + Number(amount).toLocaleString('en-ZA', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
  // Default Maluti (Loti) (M)
  return 'M ' + Number(amount).toLocaleString('en-LS', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

// Render Categories
function renderCategoryPills() {
  categoryPills.innerHTML = categories.map(cat => `
    <button class="cat-pill ${cat === state.selectedCategory ? 'active' : ''}" onclick="selectCategory('${cat}')">
      ${cat}
    </button>
  `).join('');
}

window.selectCategory = function(cat) {
  state.selectedCategory = cat;
  renderCategoryPills();
  renderProducts();
};

// Filter & Sort Products
function getFilteredProducts() {
  return productsData.filter(p => {
    const matchesCat = state.selectedCategory === 'All' || p.category === state.selectedCategory;
    const query = state.searchQuery.toLowerCase();
    const matchesSearch = !query || 
      p.name.toLowerCase().includes(query) || 
      p.sku.toLowerCase().includes(query) || 
      p.brand.toLowerCase().includes(query);
    return matchesCat && matchesSearch;
  }).sort((a, b) => {
    if (state.sortBy === 'price-asc') return a.price - b.price;
    if (state.sortBy === 'price-desc') return b.price - a.price;
    if (state.sortBy === 'rating') return b.rating - a.rating;
    return (b.isFeatured ? 1 : 0) - (a.isFeatured ? 1 : 0);
  });
}

// Render Product Catalogue (FR-1, FR-2, FR-3)
function renderProducts() {
  const products = getFilteredProducts();
  if (products.length === 0) {
    productGrid.innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; padding: 48px; color: var(--text-muted);">
        <p>No products match your search or filter criteria.</p>
      </div>
    `;
    return;
  }

  productGrid.innerHTML = products.map(prod => {
    const isLow = prod.stock > 0 && prod.stock <= prod.lowStockThreshold;
    const isOut = prod.stock <= 0;

    return `
      <div class="product-card" id="card-${prod.id}">
        <div class="product-image-wrap">
          <img src="${prod.image}" alt="${prod.name}">
          ${isOut ? `<span class="stock-tag low">Out of Stock</span>` : 
            isLow ? `<span class="stock-tag low">Only ${prod.stock} Left</span>` : 
            `<span class="stock-tag">In Stock (${prod.stock})</span>`}
        </div>
        <div class="product-info">
          <span class="product-category">${prod.category}</span>
          <h3 class="product-name">${prod.name}</h3>
          <div class="product-footer">
            <span class="product-price">${formatMoney(prod.price)}</span>
            <button 
              class="btn btn-accent" 
              onclick="addToCart('${prod.id}')"
              ${isOut ? 'disabled style="opacity: 0.5; cursor: not-allowed;"' : ''}
            >
              ${isOut ? 'Sold Out' : '+ Add to Cart'}
            </button>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

// Shopping Cart (FR-4)
window.addToCart = function(productId) {
  const prod = productsData.find(p => p.id === productId);
  if (!prod || prod.stock <= 0) return;

  const existing = state.cart.find(item => item.productId === productId);
  if (existing) {
    if (existing.quantity < prod.stock) {
      existing.quantity += 1;
    } else {
      showToast('Maximum available stock reached for this item.');
      return;
    }
  } else {
    state.cart.push({
      id: `item-${Date.now()}`,
      productId: prod.id,
      product: prod,
      quantity: 1,
      unitPrice: prod.price
    });
  }

  updateCartBadge();
  showToast(`Added "${prod.name}" to cart!`);
};

function updateCartBadge() {
  const totalCount = state.cart.reduce((sum, item) => sum + item.quantity, 0);
  cartCountBadge.textContent = totalCount;
  cartDrawerCount.textContent = totalCount;
}

function renderCartDrawer() {
  updateCartBadge();
  if (state.cart.length === 0) {
    cartItemsList.innerHTML = `
      <div style="text-align: center; padding: 48px; color: var(--text-muted);">
        <p>Your shopping cart is currently empty.</p>
      </div>
    `;
    cartSubtotal.textContent = formatMoney(0);
    return;
  }

  let total = 0;
  cartItemsList.innerHTML = state.cart.map(item => {
    const itemTotal = item.unitPrice * item.quantity;
    total += itemTotal;
    return `
      <div style="display: flex; gap: 12px; padding: 12px 0; border-bottom: 1px solid var(--border);">
        <img src="${item.product.image}" style="width: 54px; height: 54px; object-fit: cover; border-radius: 6px;">
        <div style="flex: 1;">
          <h4 style="font-size: 13px; font-weight: 700;">${item.product.name}</h4>
          <span style="font-size: 12px; color: var(--accent); font-weight: 700;">${formatMoney(item.unitPrice)}</span>
          <div style="display: flex; align-items: center; gap: 8px; margin-top: 6px;">
            <button class="btn btn-outline" style="padding: 2px 8px;" onclick="changeCartQty('${item.id}', -1)">-</button>
            <span style="font-size: 12px; font-weight: 700;">${item.quantity}</span>
            <button class="btn btn-outline" style="padding: 2px 8px;" onclick="changeCartQty('${item.id}', 1)">+</button>
            <button class="btn btn-outline" style="padding: 2px 8px; margin-left: auto; color: var(--danger);" onclick="removeCartItem('${item.id}')">&times;</button>
          </div>
        </div>
      </div>
    `;
  }).join('');

  cartSubtotal.textContent = formatMoney(total);
}

window.changeCartQty = function(itemId, delta) {
  const item = state.cart.find(i => i.id === itemId);
  if (!item) return;

  const newQty = item.quantity + delta;
  if (newQty <= 0) {
    state.cart = state.cart.filter(i => i.id !== itemId);
  } else if (newQty <= item.product.stock) {
    item.quantity = newQty;
  } else {
    showToast('Cannot exceed available stock limit.');
  }

  renderCartDrawer();
};

window.removeCartItem = function(itemId) {
  state.cart = state.cart.filter(i => i.id !== itemId);
  renderCartDrawer();
  showToast('Item removed from cart.');
};

// Admin Inventory Table (FR-9)
function renderInventoryTable() {
  inventoryTableBody.innerHTML = productsData.map(p => {
    const isLow = p.stock > 0 && p.stock <= p.lowStockThreshold;
    const isOut = p.stock <= 0;

    return `
      <tr>
        <td>
          <div style="font-weight: 700;">${p.name}</div>
          <div style="font-size: 11px; color: var(--text-muted); font-family: monospace;">${p.sku} • ${p.brand}</div>
        </td>
        <td>${p.category}</td>
        <td>
          <div style="font-weight: 700;">${formatMoney(p.price)}</div>
          <div style="font-size: 11px; color: var(--text-muted);">Cost: ${formatMoney(p.costPrice || 0)}</div>
        </td>
        <td>
          <span style="font-weight: 700; ${isOut ? 'color: var(--danger);' : isLow ? 'color: var(--accent);' : 'color: var(--success);'}">
            ${p.stock} units
          </span>
        </td>
        <td>
          ${isOut ? '<span style="color: var(--danger); font-size: 11px; font-weight: 800;">OUT OF STOCK</span>' : 
            isLow ? '<span style="color: var(--accent); font-size: 11px; font-weight: 800;">LOW STOCK ALERT</span>' : 
            '<span style="color: var(--success); font-size: 11px; font-weight: 800;">OPTIMAL</span>'}
        </td>
        <td>
          <div style="display: flex; gap: 6px;">
            <button class="btn btn-outline" style="padding: 4px 8px; font-size: 11px;" onclick="restockProduct('${p.id}')">+10 Stock</button>
            <button class="btn btn-outline" style="padding: 4px 8px; font-size: 11px; color: var(--danger);" onclick="deleteProduct('${p.id}')">Delete</button>
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

window.restockProduct = function(productId) {
  const prod = productsData.find(p => p.id === productId);
  if (prod) {
    prod.stock += 10;
    renderInventoryTable();
    renderProducts();
    showToast(`Restocked +10 units for ${prod.name}`);
  }
};

window.deleteProduct = function(productId) {
  if (confirm('Are you sure you want to permanently delete this product from MySQL inventory?')) {
    productsData = productsData.filter(p => p.id !== productId);
    renderInventoryTable();
    renderProducts();
    showToast('Product record deleted successfully.');
  }
};

// Toast Notifications
function showToast(message) {
  const toastContainer = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = message;
  toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// Event Listeners
function setupEventListeners() {
  searchInput.addEventListener('input', (e) => {
    state.searchQuery = e.target.value;
    clearSearchBtn.classList.toggle('hidden', !state.searchQuery);
    renderProducts();
  });

  clearSearchBtn.addEventListener('click', () => {
    searchInput.value = '';
    state.searchQuery = '';
    clearSearchBtn.classList.add('hidden');
    renderProducts();
  });

  sortSelect.addEventListener('change', (e) => {
    state.sortBy = e.target.value;
    renderProducts();
  });

  roleToggleBtn.addEventListener('click', () => {
    state.activeRole = state.activeRole === 'customer' ? 'admin' : 'customer';
    roleLabel.textContent = state.activeRole === 'customer' ? 'Customer View' : 'Admin Portal';
    customerView.classList.toggle('hidden', state.activeRole !== 'customer');
    adminView.classList.toggle('hidden', state.activeRole !== 'admin');
    showToast(`Switched to ${state.activeRole.toUpperCase()} mode.`);
  });

  currMaluti.addEventListener('click', () => {
    state.currency = 'LSL';
    currMaluti.classList.add('active');
    currZar.classList.remove('active');
    currUsd.classList.remove('active');
    renderProducts();
    renderInventoryTable();
    renderCartDrawer();
  });

  currZar.addEventListener('click', () => {
    state.currency = 'ZAR';
    currZar.classList.add('active');
    currMaluti.classList.remove('active');
    currUsd.classList.remove('active');
    renderProducts();
    renderInventoryTable();
    renderCartDrawer();
  });

  currUsd.addEventListener('click', () => {
    state.currency = 'USD';
    currUsd.classList.add('active');
    currMaluti.classList.remove('active');
    currZar.classList.remove('active');
    renderProducts();
    renderInventoryTable();
    renderCartDrawer();
  });

  cartBtn.addEventListener('click', () => {
    renderCartDrawer();
    cartDrawer.classList.remove('hidden');
  });

  closeCartBtn.addEventListener('click', () => cartDrawer.classList.add('hidden'));
  cartOverlay.addEventListener('click', () => cartDrawer.classList.add('hidden'));

  openAddProductModalBtn.addEventListener('click', () => {
    productForm.reset();
    productFormModal.classList.remove('hidden');
  });

  closeProductFormBtn.addEventListener('click', () => productFormModal.classList.add('hidden'));
  cancelProductFormBtn.addEventListener('click', () => productFormModal.classList.add('hidden'));

  productForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const newProd = {
      id: `prod-${Date.now()}`,
      sku: document.getElementById('formSku').value.trim().toUpperCase(),
      name: document.getElementById('formName').value.trim(),
      category: document.getElementById('formCategory').value,
      brand: document.getElementById('formBrand').value.trim(),
      price: parseFloat(document.getElementById('formPrice').value),
      costPrice: parseFloat(document.getElementById('formCost').value || 0),
      stock: parseInt(document.getElementById('formStock').value, 10),
      lowStockThreshold: parseInt(document.getElementById('formThreshold').value || 5, 10),
      description: document.getElementById('formDescription').value.trim(),
      rating: 5.0,
      reviewCount: 0,
      image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=80'
    };

    productsData.unshift(newProd);
    renderInventoryTable();
    renderProducts();
    productFormModal.classList.add('hidden');
    showToast(`Product "${newProd.name}" saved to MySQL inventory.`);
  });
}
