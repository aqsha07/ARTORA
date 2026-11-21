/**
 * ARTORA Checkout & Razorpay Test Mode Handler
 */

document.addEventListener('DOMContentLoaded', () => {
  const checkoutForm = document.getElementById('checkoutForm');
  const paymentCards = document.querySelectorAll('.payment-method-card');
  const paymentMethodInput = document.getElementById('selectedPaymentMethod');
  const placeOrderBtn = document.getElementById('placeOrderBtn');

  // 1. Payment method selection cards
  paymentCards.forEach(card => {
    card.addEventListener('click', () => {
      paymentCards.forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');
      const method = card.dataset.method;
      if (paymentMethodInput) paymentMethodInput.value = method;
    });
  });

  // 2. Form submission & Razorpay integration
  checkoutForm?.addEventListener('submit', async (e) => {
    const selectedMethod = paymentMethodInput?.value || 'razorpay';

    if (selectedMethod === 'cod' || selectedMethod === 'mock_test') {
      // Direct submission for COD or Mock
      return true;
    }

    // Razorpay Flow
    e.preventDefault();
    if (placeOrderBtn) {
      placeOrderBtn.disabled = true;
      placeOrderBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Initializing Secure Gateway...';
    }

    try {
      // Create Razorpay Order
      const res = await fetch('/checkout/create-razorpay-order', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const orderData = await res.json();

      if (!orderData.success) {
        showToast(orderData.message || 'Unable to initialize payment.', 'danger');
        resetPlaceOrderBtn();
        return;
      }

      // Check if Razorpay JS SDK loaded
      if (typeof Razorpay !== 'undefined') {
        const options = {
          key: orderData.key_id,
          amount: orderData.amount,
          currency: orderData.currency,
          name: orderData.store_name || 'ARTORA',
          description: orderData.description || 'Art Supplies & Essentials',
          image: 'https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=200&q=80',
          order_id: orderData.razorpay_order_id,
          prefill: {
            name: document.getElementById('shippingFullName')?.value || '',
            email: document.getElementById('shippingEmail')?.value || '',
            contact: document.getElementById('shippingPhone')?.value || ''
          },
          theme: {
            color: '#C86D51' // ARTORA signature Terracotta
          },
          handler: function (response) {
            // Fill hidden verification inputs
            document.getElementById('razorpayPaymentId').value = response.razorpay_payment_id || '';
            document.getElementById('razorpayOrderId').value = response.razorpay_order_id || '';
            document.getElementById('razorpaySignature').value = response.razorpay_signature || '';
            checkoutForm.submit();
          },
          modal: {
            ondismiss: function () {
              resetPlaceOrderBtn();
              showToast('Payment window closed. You can re-attempt anytime.', 'warning');
            }
          }
        };

        const rzp = new Razorpay(options);
        rzp.on('payment.failed', function (response) {
          showToast(`Payment failed: ${response.error.description}`, 'danger');
          resetPlaceOrderBtn();
        });
        rzp.open();
      } else {
        // Fallback test simulation if external Razorpay script is blocked or offline
        showTestPaymentFallback(orderData.razorpay_order_id);
      }
    } catch (err) {
      console.error(err);
      showTestPaymentFallback('order_test_' + Date.now());
    }
  });

  function resetPlaceOrderBtn() {
    if (placeOrderBtn) {
      placeOrderBtn.disabled = false;
      placeOrderBtn.innerHTML = 'Complete Order & Pay <i class="fa-solid fa-arrow-right"></i>';
    }
  }

  function showTestPaymentFallback(orderId) {
    const modal = document.createElement('div');
    modal.className = 'quick-view-backdrop active';
    modal.innerHTML = `
      <div class="auth-card" style="text-align: center; max-width: 440px;">
        <div style="width: 60px; height: 60px; background-color: var(--terracotta-light); color: var(--terracotta); border-radius: var(--radius-pill); display: flex; align-items: center; justify-content: center; font-size: 1.8rem; margin: 0 auto 1rem;">
          <i class="fa-solid fa-shield-halved"></i>
        </div>
        <h3 style="font-family: var(--font-serif); margin-bottom: 0.5rem;">Razorpay Test Sandbox</h3>
        <p style="font-size: 0.9rem; color: var(--charcoal-600); margin-bottom: 1.5rem;">
          Simulate an instant verified payment for Order <code>${orderId}</code>.
        </p>
        <button id="confirmTestPaymentBtn" class="btn btn-terracotta btn-block" style="margin-bottom: 0.75rem;">
          <i class="fa-solid fa-circle-check"></i> Authorize Test Payment
        </button>
        <button id="cancelTestPaymentBtn" class="btn btn-block" style="background: none; border: 1px solid var(--border-ivory); color: var(--charcoal-700);">
          Cancel
        </button>
      </div>
    `;
    document.body.appendChild(modal);

    document.getElementById('confirmTestPaymentBtn')?.addEventListener('click', () => {
      document.getElementById('razorpayPaymentId').value = 'pay_simulated_' + Math.random().toString(36).substring(7);
      document.getElementById('razorpayOrderId').value = orderId;
      modal.remove();
      checkoutForm.submit();
    });

    document.getElementById('cancelTestPaymentBtn')?.addEventListener('click', () => {
      modal.remove();
      resetPlaceOrderBtn();
    });
  }
});
