/**
 * ARTORA Shopping Cart Page Script
 */

document.addEventListener('DOMContentLoaded', () => {
  const cartTable = document.querySelector('.cart-items-table');

  // Quantity updates on full cart page
  cartTable?.addEventListener('change', async (e) => {
    const input = e.target.closest('.cart-qty-input');
    if (!input) return;

    const productId = input.dataset.productId;
    const qty = parseInt(input.value) || 1;

    try {
      const res = await fetch('/cart/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
        body: JSON.stringify({ product_id: productId, quantity: qty })
      });
      const data = await res.json();
      if (data.success) {
        window.location.reload();
      }
    } catch (err) {
      console.error(err);
    }
  });
});
