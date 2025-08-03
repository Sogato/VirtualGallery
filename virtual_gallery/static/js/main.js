// static/js/main.js

document.addEventListener('DOMContentLoaded', function() {

    // ===== LOADING SCREEN =====
    const loadingScreen = document.createElement('div');
    loadingScreen.className = 'loading-screen';
    loadingScreen.innerHTML = `
        <div class="loading-content">
            <div class="loading-spinner"></div>
            <p class="loading-text">Загрузка галереи...</p>
        </div>
    `;
    document.body.appendChild(loadingScreen);

    // Hide loading screen when page is fully loaded
    window.addEventListener('load', function() {
        setTimeout(() => {
            loadingScreen.classList.add('fade-out');
            setTimeout(() => {
                loadingScreen.remove();
            }, 500);
        }, 300);
    });

    // ===== SMOOTH SCROLL =====
    // For all anchor links with hash
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

    // Scroll indicator functionality (if exists on page)
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

        // Hide scroll indicator when user scrolls
        let scrollTimeout;
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

    // ===== NAVBAR SCROLL EFFECT =====
    const navbar = document.querySelector('.main-header');
    let lastScroll = 0;

    window.addEventListener('scroll', function() {
        const currentScroll = window.pageYOffset;

        // Add shadow on scroll
        if (currentScroll > 10) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }

        // Hide/show navbar on scroll (optional - uncomment if wanted)
        /*
        if (currentScroll > lastScroll && currentScroll > 100) {
            navbar.classList.add('navbar-hidden');
        } else {
            navbar.classList.remove('navbar-hidden');
        }
        lastScroll = currentScroll;
        */
    });

    // ===== IMAGE LAZY LOADING =====
    // For browsers that don't support native lazy loading
    if ('loading' in HTMLImageElement.prototype) {
        // Browser supports native lazy loading
        const images = document.querySelectorAll('img[loading="lazy"]');
        images.forEach(img => {
            img.src = img.dataset.src || img.src;
        });
    } else {
        // Fallback for older browsers
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

    // ===== CAROUSEL ENHANCEMENTS =====
    const featuredCarousel = document.querySelector('#featuredCarousel');
    if (featuredCarousel) {
        // Pause carousel on hover (desktop only)
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

        // Keyboard navigation
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

    // ===== MOBILE MENU ENHANCEMENT =====
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');

    if (navbarToggler && navbarCollapse) {
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            const isClickInsideNav = navbarCollapse.contains(e.target);
            const isClickOnToggler = navbarToggler.contains(e.target);

            if (!isClickInsideNav && !isClickOnToggler && navbarCollapse.classList.contains('show')) {
                navbarToggler.click();
            }
        });

        // Close menu when clicking on a link
        const navLinks = navbarCollapse.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (navbarCollapse.classList.contains('show')) {
                    navbarToggler.click();
                }
            });
        });
    }

    // ===== ANIMATION ON SCROLL - IMPROVED =====
    const animateOnScroll = () => {
        const elements = document.querySelectorAll('[data-aos]');

        // Adjust trigger point based on device
        const isMobile = window.innerWidth < 768;
        const triggerPoint = isMobile ? 50 : 100; // Trigger animations earlier on mobile

        elements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const elementBottom = element.getBoundingClientRect().bottom;
            const isVisible = (elementTop < window.innerHeight - triggerPoint) && (elementBottom > 0);

            if (isVisible && !element.classList.contains('aos-animate')) {
                element.classList.add('aos-animate');
            }
        });
    };

    // Check on scroll and load
    window.addEventListener('scroll', animateOnScroll);
    window.addEventListener('resize', animateOnScroll);

    // Initial check with delay to ensure content is loaded
    setTimeout(animateOnScroll, 100);

    // ===== FORM VALIDATION ENHANCEMENT =====
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

    // ===== BACK TO TOP BUTTON =====
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

    // ===== RESPONSIVE HELPERS =====
    // Update carousel on window resize
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            // Rebuild carousel if needed
            const event = new Event('resize-carousel');
            document.dispatchEvent(event);
        }, 250);
    });

    console.log('Gallery site initialized');
});