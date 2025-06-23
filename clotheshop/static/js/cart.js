document.addEventListener('DOMContentLoaded', function() {
    console.log('Cart form initialization started');
    
    // Получаем элементы
    const elements = {
        modal: document.getElementById('order-modal'),
        openBtn: document.getElementById('open-order-modal'),
        closeBtn: document.getElementById('close-modal'),
        form: document.getElementById('order-form'),
        phoneInput: document.getElementById('phone-input'),
        nameInput: document.querySelector('input[name="name"]'),
        timeSlotSelect: document.querySelector('select[name="time_slot"]'),
        submitBtn: document.getElementById('submit-order-btn'),
        errorDiv: document.querySelector('.form-errors'),
        toggle: document.querySelector('.messenger-toggle')

    };

    // Проверяем наличие всех элементов
    for (const [key, element] of Object.entries(elements)) {
        if (!element && key !== 'toggle') {
            console.error(`Element ${key} not found`);
            return;
        }
    }

    // Получаем URL для отправки формы
    const submitUrl = elements.form.dataset.submitUrl;
    console.log('Form submit URL:', submitUrl);

    // Инициализация маски телефона
    function initPhoneMask() {
        if (typeof Inputmask !== 'undefined') {
            console.log('Initializing phone input mask');
            new Inputmask({
                mask: '99999999999',
                placeholder: '_',
                showMaskOnHover: false,
                showMaskOnFocus: true,
                clearIncomplete: false,
                autoUnmask: false,
                onincomplete: function() {
                    elements.phoneInput.classList.add('is-invalid');
                    validateForm();
                },
                oncomplete: function() {
                    elements.phoneInput.classList.remove('is-invalid');
                    validateForm();
                }
            }).mask(elements.phoneInput);
        } else {
            console.error('Inputmask library not loaded');
            elements.phoneInput.addEventListener('input', validateForm);
        }
    }

    // Показ ошибок
    function showError(message) {
        elements.errorDiv.textContent = message;
        elements.errorDiv.style.display = 'block';
        elements.errorDiv.classList.add('show');
    }

    // Скрытие ошибок
    function hideError() {
        elements.errorDiv.textContent = '';
        elements.errorDiv.style.display = 'none';
        elements.errorDiv.classList.remove('show');
    }

    // Валидация формы
    function validateForm() {
        const nameValue = elements.nameInput.value.trim();
        const nameValid = nameValue.length >= 2;
        let phoneValid = false;
        let timeValid = true;
        
        console.log('Validating form...');
        console.log('Name value:', nameValue, 'Name valid:', nameValid);
        console.log('Phone value:', elements.phoneInput.value);
        
        if (elements.phoneInput.inputmask) {
            phoneValid = elements.phoneInput.inputmask.isComplete();
            console.log('Inputmask available, phone valid:', phoneValid);
        } else {
            // Fallback validation if inputmask is not available
            const phoneValue = elements.phoneInput.value.replace(/\D/g, '');
            phoneValid = phoneValue.length === 11 && phoneValue.startsWith('7');
            console.log('No inputmask, phone value:', phoneValue, 'phone valid:', phoneValid);
        }

        // Проверяем время доставки
        if (elements.timeSlotSelect) {
            const selectedTime = elements.timeSlotSelect.value;
            timeValid = selectedTime && selectedTime !== 'closed';
            console.log('Time slot selected:', selectedTime, 'Time valid:', timeValid);
        }

        const isFormValid = nameValid && phoneValid && timeValid;
        elements.submitBtn.disabled = !isFormValid;
        
        // Скрываем ошибки если форма валидна
        if (isFormValid) {
            hideError();
        }
        
        console.log(`Form validation - Name: ${nameValid}, Phone: ${phoneValid}, Time: ${timeValid}, Form valid: ${isFormValid}, Button disabled: ${elements.submitBtn.disabled}`);
        return isFormValid;
    }

    // Отправка формы
    async function handleFormSubmit(event) {
    event.preventDefault();
    
    if (!validateForm()) {
        showError('Пожалуйста, заполните все поля правильно');
        return;
    }

    hideError();
    elements.submitBtn.disabled = true;
    elements.submitBtn.textContent = 'Отправка...';

    try {
        const formData = new FormData(elements.form);
        
        const response = await fetch(elements.form.dataset.submitUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': elements.form.querySelector('[name=csrfmiddlewaretoken]').value
            }
        });

        const data = await response.json();
        
        if (response.ok && data.success) {
            window.location.href = data.redirect_url;
        } else {
            // Обработка ошибок Django формы
            if (data.errors) {
                let errorMessages = [];
                for (const field in data.errors) {
                    if (Array.isArray(data.errors[field])) {
                        errorMessages.push(...data.errors[field]);
                    } else {
                        errorMessages.push(data.errors[field]);
                    }
                }
                showError(errorMessages.join(', '));
            } else {
                throw new Error('Ошибка сервера');
            }
        }
    } catch (error) {
        console.error('Form submission error:', error);
        showError('Ошибка при отправке: ' + error.message);
    } finally {
        elements.submitBtn.textContent = 'Сформировать заказ';
        elements.submitBtn.disabled = false;
    }
}

    // Управление модальным окном
    function setupModal() {
        elements.openBtn.addEventListener('click', () => {
            // Проверяем, что корзина не пуста перед открытием модального окна
            const cartItems = document.querySelectorAll('.cart-item');
            if (cartItems.length === 0) {
                showError('Ваша корзина пуста. Пожалуйста, добавьте товары перед оформлением заказа.');
                return;
            }
            
            elements.modal.classList.add('active');
            elements.nameInput.focus();
        });

        elements.closeBtn.addEventListener('click', () => {
            elements.modal.classList.remove('active');
            hideError(); // Скрываем ошибки при закрытии модального окна
        });

        elements.modal.addEventListener('click', (event) => {
            if (event.target === elements.modal) {
                elements.modal.classList.remove('active');
                hideError(); // Скрываем ошибки при закрытии модального окна
            }
        });
    }

    // Инициализация переключателя мессенджеров
    function initMessengerToggle() {
    if (!elements.toggle) return;
    
    let state = 'neutral';
    const hiddenInput = document.querySelector('input[name="preferred_messenger"]');
    
    // Обработчик клика вместо drag
    elements.toggle.addEventListener('click', function() {
        const knob = this.querySelector('.messenger-knob');
        
        if (this.classList.contains('telegram')) {
            setToggleState('whatsapp');
        } else if (this.classList.contains('whatsapp')) {
            setToggleState('neutral');
        } else {
            setToggleState('telegram');
        }
        
        hiddenInput.value = state;
        console.log('Selected messenger:', state); // Для отладки
    });

    function setToggleState(newState) {
        state = newState;
        elements.toggle.className = 'messenger-toggle';
        const knob = elements.toggle.querySelector('.messenger-knob');
        
        if (newState === 'telegram') {
            elements.toggle.classList.add('telegram');
            knob.textContent = 'Telegram';
        } else if (newState === 'whatsapp') {
            elements.toggle.classList.add('whatsapp');
            knob.textContent = 'WhatsApp';
        } else {
            knob.textContent = 'Не писать';
        }
    }
}

    // Инициализация всех компонентов
    function init() {
        initPhoneMask();
        setupModal();
        initMessengerToggle();
        
        elements.nameInput.addEventListener('input', validateForm);
        elements.phoneInput.addEventListener('input', validateForm);
        if (elements.timeSlotSelect) {
            elements.timeSlotSelect.addEventListener('change', validateForm);
        }
        elements.form.addEventListener('submit', handleFormSubmit);
        
        console.log('Cart form initialized successfully');
    }

    // Запускаем инициализацию
    init();
});