/**
 * ARTORA Shop & Product Interactions
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Gallery Thumbnail Switcher
  const thumbnails = document.querySelectorAll('.thumbnail-btn');
  const mainImage = document.querySelector('.main-gallery-image');

  thumbnails.forEach(btn => {
    btn.addEventListener('click', () => {
      thumbnails.forEach(t => t.classList.remove('active'));
      btn.classList.add('active');
      const newSrc = btn.dataset.fullSrc;
      if (mainImage && newSrc) {
        mainImage.style.opacity = '0.3';
        setTimeout(() => {
          mainImage.src = newSrc;
          mainImage.style.opacity = '1';
        }, 150);
      }
    });
  });

  // 2. Quantity Stepper in Product Detail & Modal
  document.addEventListener('click', (e) => {
    const stepBtn = e.target.closest('.qty-step-btn');
    if (!stepBtn) return;

    const action = stepBtn.dataset.action;
    const input = stepBtn.parentElement.querySelector('.qty-input');
    if (!input) return;

    let currentVal = parseInt(input.value) || 1;
    if (action === 'increment') {
      input.value = currentVal + 1;
    } else if (action === 'decrement' && currentVal > 1) {
      input.value = currentVal - 1;
    }
  });

  // 3. Quick-View Modal Trigger
  const qvBackdrop = document.getElementById('quickViewBackdrop');
  const qvCloseBtn = document.getElementById('closeQuickView');

  qvCloseBtn?.addEventListener('click', () => {
    qvBackdrop?.classList.remove('active');
  });

  qvBackdrop?.addEventListener('click', (e) => {
    if (e.target === qvBackdrop) qvBackdrop.classList.remove('active');
  });

  document.addEventListener('click', async (e) => {
    const qvBtn = e.target.closest('.quick-view-btn');
    if (!qvBtn) return;

    e.preventDefault();
    const productId = qvBtn.dataset.productId;
    if (!productId) return;

    try {
      const res = await fetch(`/api/product/${productId}/quick-view`);
      const data = await res.json();

      const modalImg = document.getElementById('qvModalImage');
      const modalTitle = document.getElementById('qvModalTitle');
      const modalCat = document.getElementById('qvModalCategory');
      const modalPrice = document.getElementById('qvModalPrice');
      const modalCompare = document.getElementById('qvModalCompare');
      const modalDesc = document.getElementById('qvModalDesc');
      const modalRating = document.getElementById('qvModalRating');
      const modalInputId = document.getElementById('qvModalProductId');
      const modalFullLink = document.getElementById('qvModalFullLink');

      if (modalImg) modalImg.src = data.image_url;
      if (modalTitle) modalTitle.textContent = data.name;
      if (modalCat) modalCat.textContent = data.category;
      if (modalPrice) modalPrice.textContent = data.price_formatted;
      if (modalCompare) {
        modalCompare.textContent = data.compare_formatted || '';
        modalCompare.style.display = data.compare_formatted ? 'inline-block' : 'none';
      }
      if (modalDesc) modalDesc.textContent = data.short_description;
      if (modalRating) modalRating.textContent = `${data.rating} (${data.reviews_count} reviews)`;
      if (modalInputId) modalInputId.value = data.id;
      if (modalFullLink) modalFullLink.href = `/shop/product/${data.slug}`;

      qvBackdrop?.classList.add('active');
    } catch (err) {
      console.error('Quick view error:', err);
    }
  });
});
