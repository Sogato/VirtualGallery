document.addEventListener('DOMContentLoaded', function() {
    // ===== Экран загрузки =====
    const loadingScreen = document.createElement('div');
    loadingScreen.className = 'loading-screen';
    loadingScreen.innerHTML = `
        <div class="loading-content">
            <div class="loading-spinner"></div>
            <p class="loading-text">Загрузка галереи...</p>
        </div>
    `;
    document.body.appendChild(loadingScreen);

    // Скрытие экрана загрузки после полной загрузки страницы
    window.addEventListener('load', function() {
        setTimeout(() => {
            loadingScreen.classList.add('fade-out');
            setTimeout(() => {
                loadingScreen.remove();
            }, 500);
        }, 300);
    });

    // ===== Плавная прокрутка к якорям =====
    // Для всех ссылок с хэшем
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Функционал индикатора прокрутки (если присутствует на странице)
    const scrollIndicator = document.querySelector('.scroll-indicator');
    if (scrollIndicator) {
        scrollIndicator.addEventListener('click', function() {
            const nextSection = document.querySelector('.featured-section');
            if (nextSection) {
                nextSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });

        // Скрытие индикатора прокрутки при скролле
        window.addEventListener('scroll', function() {
            if (window.scrollY > 100) {
                scrollIndicator.style.opacity = '0';
                scrollIndicator.style.pointerEvents = 'none';
            } else {
                scrollIndicator.style.opacity = '1';
                scrollIndicator.style.pointerEvents = 'auto';
            }
        });
    }

    // ===== Эффект навигационной панели при скролле =====
    const navbar = document.querySelector('.main-header');
    let lastScroll = 0;

    window.addEventListener('scroll', function() {
        const currentScroll = window.pageYOffset;

        // Добавление тени при скролле
        if (currentScroll > 10) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }

        // Скрытие/показ навигации при скролле (опционально - раскомментировать если нужно)
        if (currentScroll > lastScroll && currentScroll > 150) {
            navbar.classList.add('navbar-hidden');
        } else {
            navbar.classList.remove('navbar-hidden');
        }
        lastScroll = currentScroll;
    });

    // ===== Ленивая загрузка изображений =====
    // Для браузеров, поддерживающих native lazy loading
    if ('loading' in HTMLImageElement.prototype) {
        const images = document.querySelectorAll('img[loading="lazy"]');
        images.forEach(img => {
            img.src = img.dataset.src || img.src;
        });
    } else {
        // Фоллбэк для старых браузеров с использованием IntersectionObserver
        const lazyImages = document.querySelectorAll('img[data-lazy]');
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.add('loaded');
                    imageObserver.unobserve(img);
                }
            });
        });

        lazyImages.forEach(img => imageObserver.observe(img));
    }

    // ===== Улучшения для карусели =====
    const featuredCarousel = document.querySelector('#featuredCarousel');
    if (featuredCarousel) {
        // Пауза карусели при наведении (только для десктопа)
        if (window.innerWidth > 768) {
            featuredCarousel.addEventListener('mouseenter', function() {
                const carousel = bootstrap.Carousel.getInstance(this);
                if (carousel) carousel.pause();
            });

            featuredCarousel.addEventListener('mouseleave', function() {
                const carousel = bootstrap.Carousel.getInstance(this);
                if (carousel) carousel.cycle();
            });
        }

        // Навигация с клавиатуры
        document.addEventListener('keydown', function(e) {
            const carousel = bootstrap.Carousel.getInstance(featuredCarousel);
            if (carousel) {
                if (e.key === 'ArrowLeft') {
                    carousel.prev();
                } else if (e.key === 'ArrowRight') {
                    carousel.next();
                }
            }
        });
    }

    // ===== Улучшения для мобильного меню =====
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');

    if (navbarToggler && navbarCollapse) {
        // Закрытие меню при клике вне его
        document.addEventListener('click', function(e) {
            const isClickInsideNav = navbarCollapse.contains(e.target);
            const isClickOnToggler = navbarToggler.contains(e.target);

            if (!isClickInsideNav && !isClickOnToggler && navbarCollapse.classList.contains('show')) {
                navbarToggler.click();
            }
        });

        // Закрытие меню при клике на ссылку
        const navLinks = navbarCollapse.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (navbarCollapse.classList.contains('show')) {
                    navbarToggler.click();
                }
            });
        });
    }

    // ===== Анимация при скролле (улучшенная) =====
    const animateOnScroll = () => {
        const elements = document.querySelectorAll('[data-aos]');

        // Корректировка точки срабатывания в зависимости от устройства
        const isMobile = window.innerWidth < 768;
        const triggerPoint = isMobile ? 50 : 100; // Раньше на мобильных

        elements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const elementBottom = element.getBoundingClientRect().bottom;
            const isVisible = (elementTop < window.innerHeight - triggerPoint) && (elementBottom > 0);

            if (isVisible && !element.classList.contains('aos-animate')) {
                element.classList.add('aos-animate');
            }
        });
    };

    // Проверка при скролле и ресайзе
    window.addEventListener('scroll', animateOnScroll);
    window.addEventListener('resize', animateOnScroll);

    // Изначальная проверка с задержкой для загрузки контента
    setTimeout(animateOnScroll, 100);

    // ===== Улучшение валидации форм =====
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // ===== Кнопка "Наверх" =====
    const backToTopBtn = document.createElement('button');
    backToTopBtn.className = 'back-to-top';
    backToTopBtn.innerHTML = '↑';
    backToTopBtn.setAttribute('aria-label', 'Наверх');
    document.body.appendChild(backToTopBtn);

    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            backToTopBtn.classList.add('show');
        } else {
            backToTopBtn.classList.remove('show');
        }
    });

    backToTopBtn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // ===== Помощники для отзывчивости =====
    // Обновление карусели при ресайзе окна
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            // Диспатч события для перестройки карусели
            const event = new Event('resize-carousel');
            document.dispatchEvent(event);
        }, 250);
    });

    console.log('Gallery site initialized');
});