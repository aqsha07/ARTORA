/**
 * ARTORA Main JavaScript
 * Brand: ARTORA - Create Without Limits.
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Header scroll effect
  const header = document.querySelector('.site-header');
  window.addEventListener('scroll', () => {
    if (window.scrollY > 30) {
      header?.classList.add('scrolled');
    } else {
      header?.classList.remove('scrolled');
    }
  });

  // 2. Mobile Menu Toggle
  const mobileToggle = document.querySelector('.mobile-menu-toggle');
  const mobileDrawer = document.getElementById('mobileNavDrawer');
  const mobileDrawerClose = document.getElementById('closeMobileNav');

  mobileToggle?.addEventListener('click', () => {
    mobileDrawer?.classList.add('active');
  });

  mobileDrawerClose?.addEventListener('click', () => {
    mobileDrawer?.classList.remove('active');
  });

  // 3. Mini-Cart Drawer
  const openCartBtns = document.querySelectorAll('.open-cart-drawer');
  const cartBackdrop = document.getElementById('cartDrawerBackdrop');
  const closeCartBtn = document.getElementById('closeCartDrawer');

  openCartBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      openCartDrawer();
    });
  });

  closeCartBtn?.addEventListener('click', closeCartDrawer);
  cartBackdrop?.addEventListener('click', (e) => {
    if (e.target === cartBackdrop) closeCartDrawer();
  });

  function openCartDrawer() {
    refreshCartDrawer();
    cartBackdrop?.classList.add('active');
  }

  function closeCartDrawer() {
    cartBackdrop?.classList.remove('active');
  }

  // 4. Live Search Modal & Autocomplete
  const openSearchBtns = document.querySelectorAll('.open-search-modal');
  const searchBackdrop = document.getElementById('searchModalBackdrop');
  const closeSearchBtn = document.getElementById('closeSearchModal');
  const searchInput = document.getElementById('liveSearchInput');
  const searchResults = document.getElementById('liveSearchResults');

  openSearchBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      searchBackdrop?.classList.add('active');
      setTimeout(() => searchInput?.focus(), 100);
    });
  });

  closeSearchBtn?.addEventListener('click', () => {
    searchBackdrop?.classList.remove('active');
  });

  searchBackdrop?.addEventListener('click', (e) => {
    if (e.target === searchBackdrop) searchBackdrop.classList.remove('active');
  });

  let searchTimeout = null;
  searchInput?.addEventListener('input', (e) => {
    clearTimeout(searchTimeout);
    const query = e.target.value.trim();

    if (query.length < 2) {
      if (searchResults) {
        searchResults.innerHTML = '<p class="text-muted text-center" style="color: var(--charcoal-500); padding: 1.5rem;">Type at least 2 characters to search art supplies...</p>';
      }
      return;
    }

    searchTimeout = setTimeout(async () => {
      try {
        const res = await fetch(`/api/live-search?q=${encodeURIComponent(query)}`);
        const data = await res.json();

        if (!data.products.length && !data.categories.length) {
          searchResults.innerHTML = `<p class="text-muted text-center" style="color: var(--charcoal-500); padding: 1.5rem;">No art supplies found matching "<strong>${query}</strong>".</p>`;
          return;
        }

        let html = '';
        if (data.categories.length) {
          html += '<div style="margin-bottom: 0.8rem;"><span style="font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: var(--terracotta); letter-spacing: 0.08em;">Categories</span><div style="display: flex; gap: 0.5rem; margin-top: 0.4rem; flex-wrap: wrap;">';
          data.categories.forEach(c => {
            html += `<a href="/shop/category/${c.slug}" class="badge badge-sage" style="text-decoration: none; padding: 0.35rem 0.75rem;">${c.name}</a>`;
          });
          html += '</div></div>';
        }

        if (data.products.length) {
          html += '<div style="font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: var(--charcoal-600); letter-spacing: 0.08em; margin-bottom: 0.5rem;">Products</div>';
          data.products.forEach(p => {
            html += `
              <a href="/shop/product/${p.slug}" class="search-result-item">
                <img src="${p.image}" alt="${p.name}" class="search-result-img" />
                <div class="search-result-info">
                  <h4>${p.name}</h4>
                  <div class="search-result-cat">${p.category}</div>
                </div>
                <div class="search-result-price">${p.price_formatted}</div>
              </a>
            `;
          });
        }

        searchResults.innerHTML = html;
      } catch (err) {
        console.error('Search error:', err);
      }
    }, 250);
  });

  // 5. Global AJAX Add to Cart Handler
  document.addEventListener('submit', async (e) => {
    const form = e.target.closest('.ajax-add-to-cart-form');
    if (!form) return;

    e.preventDefault();
    const btn = form.querySelector('button[type="submit"]');
    const originalText = btn ? btn.innerHTML : '';
    if (btn) {
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Adding...';
      btn.disabled = true;
    }

    try {
      const formData = new FormData(form);
      const res = await fetch('/cart/add', {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        body: formData
      });
      const data = await res.json();

      if (data.success) {
        showToast(data.message, 'success');
        updateHeaderBadge(data.cart_count);
        openCartDrawer();
      } else {
        showToast(data.message || 'Error adding item.', 'danger');
      }
    } catch (err) {
      console.error(err);
      showToast('Network error while adding to cart.', 'danger');
    } finally {
      if (btn) {
        btn.innerHTML = originalText;
        btn.disabled = false;
      }
    }
  });

  // 6. Global Wishlist Toggle
  document.addEventListener('click', async (e) => {
    const btn = e.target.closest('.wishlist-toggle-btn');
    if (!btn) return;

    e.preventDefault();
    const productId = btn.dataset.productId;
    if (!productId) return;

    try {
      const res = await fetch(`/auth/wishlist/toggle/${productId}`, {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      });

      if (res.status === 401) {
        showToast('Please log in to add items to your wishlist.', 'warning');
        window.location.href = `/auth/login?next=${encodeURIComponent(window.location.pathname)}`;
        return;
      }

      const data = await res.json();
      if (data.success) {
        btn.classList.toggle('active', data.added);
        const icon = btn.querySelector('i');
        if (icon) {
          icon.className = data.added ? 'fa-solid fa-heart' : 'fa-regular fa-heart';
        }
        showToast(data.message, data.added ? 'success' : 'info');
      }
    } catch (err) {
      console.error(err);
    }
  });

  // 7. Auto-dismiss alerts
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    setTimeout(() => {
      alert.style.opacity = '0';
      alert.style.transform = 'translateX(100%)';
      alert.style.transition = 'all 0.3s ease-out';
      setTimeout(() => alert.remove(), 300);
    }, 4500);
  });
});

/** Helper: Update Header Cart Badge */
function updateHeaderBadge(count) {
  const badges = document.querySelectorAll('.header-cart-count');
  badges.forEach(b => {
    b.textContent = count;
    b.style.display = count > 0 ? 'flex' : 'none';
  });
}

/** Helper: Show Toast notification */
function showToast(message, type = 'info') {
  let container = document.querySelector('.flash-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'flash-container';
    document.body.appendChild(container);
  }

  const alert = document.createElement('div');
  alert.className = `alert alert-${type}`;
  alert.innerHTML = `
    <span>${message}</span>
    <button class="alert-close" onclick="this.parentElement.remove()"><i class="fa-solid fa-xmark"></i></button>
  `;
  container.appendChild(alert);

  setTimeout(() => {
    alert.style.opacity = '0';
    alert.style.transform = 'translateX(100%)';
    alert.style.transition = 'all 0.3s ease-out';
    setTimeout(() => alert.remove(), 300);
  }, 4000);
}

/** Helper: Refresh Slide-out Mini Cart */
async function refreshCartDrawer() {
  const itemsContainer = document.getElementById('cartDrawerItems');
  const subtotalEl = document.getElementById('cartDrawerSubtotal');
  const progressFill = document.getElementById('cartDrawerProgressFill');
  const progressText = document.getElementById('cartDrawerProgressText');

  if (!itemsContainer) return;

  try {
    const res = await fetch('/api/cart/summary');
    const data = await res.json();

    if (!data.items.length) {
      itemsContainer.innerHTML = `
        <div style="text-align: center; padding: 3rem 1rem; color: var(--charcoal-500);">
          <i class="fa-solid fa-paintbrush" style="font-size: 3rem; color: var(--border-ivory); margin-bottom: 1rem;"></i>
          <h4 style="font-family: var(--font-serif); color: var(--charcoal-900); margin-bottom: 0.5rem;">Your Art Cart is Empty</h4>
          <p style="font-size: 0.9rem; margin-bottom: 1.5rem;">Explore our curated paints, fine surfaces, and craft supplies.</p>
          <a href="/shop" class="btn btn-terracotta btn-sm">Explore Collection</a>
        </div>
      `;
      if (subtotalEl) subtotalEl.textContent = '₹0.00';
      if (progressFill) progressFill.style.width = '0%';
      if (progressText) progressText.innerHTML = 'Add items worth <strong>₹999.00</strong> to unlock Free Shipping.';
      return;
    }

    let html = '';
    data.items.forEach(item => {
      html += `
        <div class="mini-cart-item" data-id="${item.id}">
          <img src="${item.image_url}" alt="${item.name}" class="mini-cart-item-img" />
          <div class="mini-cart-item-info">
            <h4 class="mini-cart-item-title">${item.name}</h4>
            <div class="mini-cart-item-price">₹${item.price.toFixed(2)}</div>
            <div class="mini-qty-control">
              <button class="mini-qty-btn" onclick="updateMiniCartQty(${item.id}, ${item.quantity - 1})">-</button>
              <span class="mini-qty-display">${item.quantity}</span>
              <button class="mini-qty-btn" onclick="updateMiniCartQty(${item.id}, ${item.quantity + 1})">+</button>
            </div>
          </div>
          <button class="mini-item-remove-btn" onclick="removeMiniCartItem(${item.id})" title="Remove item">
            <i class="fa-solid fa-trash-can"></i>
          </button>
        </div>
      `;
    });

    itemsContainer.innerHTML = html;
    if (subtotalEl) subtotalEl.textContent = `₹${data.subtotal.toFixed(2)}`;
    if (progressFill) progressFill.style.width = `${data.shipping_progress}%`;
    if (progressText) {
      if (data.amount_needed_for_free_shipping > 0) {
        progressText.innerHTML = `Add items worth <strong>₹${data.amount_needed_for_free_shipping.toFixed(2)}</strong> to unlock Free Shipping.`;
      } else {
        progressText.innerHTML = `<i class="fa-solid fa-circle-check" style="color: var(--color-success);"></i> <strong>Congratulations!</strong> You qualify for Free Shipping.`;
      }
    }
  } catch (err) {
    console.error('Error refreshing mini-cart:', err);
  }
}

async function updateMiniCartQty(productId, qty) {
  try {
    const res = await fetch('/cart/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
      body: JSON.stringify({ product_id: productId, quantity: qty })
    });
    const data = await res.json();
    if (data.success) {
      updateHeaderBadge(data.summary.items_count);
      refreshCartDrawer();
    }
  } catch (err) {
    console.error(err);
  }
}

async function removeMiniCartItem(productId) {
  try {
    const res = await fetch(`/cart/remove/${productId}`, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    });
    const data = await res.json();
    if (data.success) {
      updateHeaderBadge(data.summary.items_count);
      refreshCartDrawer();
      showToast('Item removed from cart.', 'info');
    }
  } catch (err) {
    console.error(err);
  }
}
