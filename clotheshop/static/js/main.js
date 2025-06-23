document.addEventListener("DOMContentLoaded", function() {
    // FAQ аккордеон
    const questions = document.querySelectorAll(".faq-question");
    
    questions.forEach((btn) => {
        btn.addEventListener("click", () => {
            const item = btn.closest(".faq-item");
            
            document.querySelectorAll(".faq-item").forEach((el) => {
                if (el !== item) el.classList.remove("active");
            });
            
            item.classList.toggle("active");
        });
    });
    
    // Анимация статистических блоков
    const stats = document.querySelectorAll(".stat-block");
    
    stats.forEach(stat => {
        stat.addEventListener("mouseenter", function() {
            this.style.transform = this.style.transform.replace(/scale\([^)]+\)/, 'scale(1.1)');
        });
        
        stat.addEventListener("mouseleave", function() {
            this.style.transform = this.style.transform.replace(/scale\([^)]+\)/, 'scale(1)');
        });
    });
});


document.addEventListener("DOMContentLoaded", function() {
  const carousel = document.querySelector('.products-carousel');
  const prevBtn = document.querySelector('.carousel-prev');
  const nextBtn = document.querySelector('.carousel-next');
  
  if (!carousel || !prevBtn || !nextBtn) return;
  
  const products = document.querySelectorAll('.product-card');
  if (products.length === 0) return;
  
  const productWidth = products[0].offsetWidth + 32; // width + gap
  let currentIndex = 0;
  const visibleProducts = Math.floor(carousel.parentElement.offsetWidth / productWidth);
  
  function updateCarousel() {
    const offset = -currentIndex * productWidth;
    carousel.style.transform = `translateX(${offset}px)`;
    
    prevBtn.disabled = currentIndex === 0;
    nextBtn.disabled = currentIndex >= products.length - visibleProducts;
  }
  
  prevBtn.addEventListener('click', function() {
    if (currentIndex > 0) {
      currentIndex--;
      updateCarousel();
    }
  });
  
  nextBtn.addEventListener('click', function() {
    if (currentIndex < products.length - visibleProducts) {
      currentIndex++;
      updateCarousel();
    }
  });
  
  // Автопрокрутка
  let autoScrollInterval = setInterval(() => {
    if (currentIndex >= products.length - visibleProducts) {
      currentIndex = 0;
    } else {
      currentIndex++;
    }
    updateCarousel();
  }, 5000);
  
  carousel.addEventListener('mouseenter', () => {
    clearInterval(autoScrollInterval);
  });
  
  carousel.addEventListener('mouseleave', () => {
    autoScrollInterval = setInterval(() => {
      if (currentIndex >= products.length - visibleProducts) {
        currentIndex = 0;
      } else {
        currentIndex++;
      }
      updateCarousel();
    }, 5000);
  });
  
  // Инициализация
  updateCarousel();
  
  // Реакция на изменение размера окна
  window.addEventListener('resize', function() {
    currentIndex = 0;
    updateCarousel();
  });
});