document.addEventListener('DOMContentLoaded', () => {
  const sizeButtons = document.querySelectorAll('.size-btn');
  const selectedSizeInput = document.getElementById('selected-size');
  const addToCartBtn = document.getElementById('add-to-cart');
  const quantityControls = document.getElementById('quantity-controls');
  const quantityDisplay = document.getElementById('quantity-display');
  const btnIncrease = document.getElementById('btn-increase');
  const btnDecrease = document.getElementById('btn-decrease');
  const removeFromCartBtn = document.getElementById('remove-from-cart');
  const sizeCounter = document.getElementById('size-counter');

  let selectedSize = null;
  let maxQuantity = 1;
  let cartState = {};  // key: size, value: quantity

  sizeButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      sizeButtons.forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');

      selectedSize = btn.dataset.size;
      maxQuantity = parseInt(btn.dataset.quantity, 10);

      selectedSizeInput.value = selectedSize;

      const sizeKey = selectedSize;
      const quantityInCart = cartState[sizeKey] || 0;

      updateUIForSize(quantityInCart);
    });
  });

  document.getElementById('size-form').addEventListener('submit', (e) => {
    e.preventDefault();

    const form = e.target;
    const actionBtn = document.activeElement;
    const action = actionBtn?.value || 'add';

    if (!selectedSize) {
      alert('Пожалуйста, выберите размер');
      return;
    }

    const formData = new FormData(form);
    formData.set('size', selectedSize);
    formData.set('action', action);

    fetch(form.getAttribute('action'), {
      method: 'POST',
      body: formData,
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': getCookie('csrftoken'),
      },
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        if (action === 'add') {
          cartState[selectedSize] = 1;
        } else if (action === 'increase') {
          cartState[selectedSize]++;
        } else if (action === 'decrease') {
          if (cartState[selectedSize] > 1) {
            cartState[selectedSize]--;
          } else {
            delete cartState[selectedSize];
          }
        } else if (action === 'remove') {
          delete cartState[selectedSize];
         updateUIForSize(0);
         sizeButtons.forEach(b => b.classList.remove('selected'));
         selectedSize = null;
         selectedSizeInput.value = '';
        }
        updateUIForSize(cartState[selectedSize] || 0);
      } else {
        alert('Ошибка: ' + (data.error || 'неизвестная ошибка'));
      }
    });
  });

  function updateUIForSize(quantity) {
  if (quantity > 0) {
    quantityControls.style.display = 'flex';
    addToCartBtn.style.display = 'none';
    removeFromCartBtn.style.display = 'inline-block';
    quantityDisplay.textContent = quantity;
    sizeCounter.textContent = `Товаров размера ${selectedSize} в корзине: ${quantity}`;
  } else {
    quantityControls.style.display = 'none';
    addToCartBtn.style.display = 'inline-block';
    removeFromCartBtn.style.display = 'none';
    sizeCounter.textContent = '';
  }
  updateButtons(quantity);
}


  function updateButtons(quantity) {
    btnIncrease.disabled = quantity >= maxQuantity;
    btnDecrease.disabled = quantity <= 1;
  }

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // Инициализируем cartState из sessionStorage или пустого объекта
  if (window.initialCartState) {
    cartState = window.initialCartState;
  }
});
