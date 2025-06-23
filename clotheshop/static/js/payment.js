document.addEventListener("DOMContentLoaded", function () {
    const questions = document.querySelectorAll(".faq-question");

    questions.forEach((btn) => {
        btn.addEventListener("click", () => {
            const item = btn.closest(".faq-item");

            // Закрываем все кроме текущего
            document.querySelectorAll(".faq-item").forEach((el) => {
                if (el !== item) el.classList.remove("active");
            });

            item.classList.toggle("active");
        });
    });
});
