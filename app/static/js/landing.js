(function () {
    'use strict';

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const isMobile = () => window.innerWidth < 768;

    /* ── Sticky nav ── */
    const nav = document.querySelector('.landing-nav');
    const toggle = document.querySelector('.landing-nav__toggle');
    const mobileMenu = document.querySelector('.landing-nav__mobile');

    if (nav) {
        window.addEventListener('scroll', () => {
            nav.classList.toggle('is-scrolled', window.scrollY > 8);
        }, { passive: true });
    }

    if (toggle && mobileMenu) {
        toggle.addEventListener('click', () => {
            const open = toggle.classList.toggle('is-open');
            mobileMenu.classList.toggle('is-open', open);
            toggle.setAttribute('aria-expanded', open);
        });

        mobileMenu.querySelectorAll('a').forEach((link) => {
            link.addEventListener('click', () => {
                toggle.classList.remove('is-open');
                mobileMenu.classList.remove('is-open');
                toggle.setAttribute('aria-expanded', 'false');
            });
        });
    }

    /* ── Intersection Observer reveals ── */
    function observeReveal(selector, options = {}) {
        const els = document.querySelectorAll(selector);
        if (!els.length) return;

        if (prefersReducedMotion) {
            els.forEach((el) => el.classList.add('is-visible'));
            return;
        }

        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('is-visible');
                        if (!options.repeat) observer.unobserve(entry.target);
                    }
                });
            },
            { threshold: options.threshold || 0.15, rootMargin: options.rootMargin || '0px 0px -40px 0px' }
        );

        els.forEach((el) => observer.observe(el));
    }

    observeReveal('.reveal');
    observeReveal('.reveal-scale');
    observeReveal('.stagger');
    observeReveal('.landing-flow', { threshold: 0.3 });

    /* ── Hero entrance sequence ── */
    function runHeroEntrance() {
        const items = document.querySelectorAll('[data-hero-order]');
        const mock = document.querySelector('.hero-mock');

        if (prefersReducedMotion) {
            items.forEach((el) => el.classList.add('is-visible'));
            if (mock) mock.classList.add('is-visible');
            animateDashboard(true);
            return;
        }

        items.forEach((el) => {
            const delay = parseInt(el.dataset.heroOrder, 10) * 80;
            setTimeout(() => el.classList.add('is-visible'), delay);
        });

        if (mock) {
            setTimeout(() => {
                mock.classList.add('is-visible');
                if (!isMobile()) mock.classList.add('is-floating');
                setTimeout(animateDashboard, 400);
            }, 500);
        }
    }

    /* ── KPI count-up ── */
    function animateCount(el, target, suffix = '') {
        if (prefersReducedMotion) {
            el.textContent = target + suffix;
            return;
        }
        const duration = 900;
        const start = performance.now();
        const from = 0;

        function tick(now) {
            const progress = Math.min((now - start) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            const val = Math.round(from + (target - from) * eased);
            el.textContent = val.toLocaleString() + suffix;
            if (progress < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
    }

    function animateDashboard(instant) {
        document.querySelectorAll('[data-count]').forEach((el) => {
            const target = parseFloat(el.dataset.count);
            const suffix = el.dataset.suffix || '';
            const isCurrency = el.dataset.currency === 'true';

            if (isCurrency) {
                if (prefersReducedMotion || instant) {
                    el.textContent = 'K ' + target.toLocaleString();
                } else {
                    const duration = 1000;
                    const start = performance.now();
                    function tick(now) {
                        const progress = Math.min((now - start) / duration, 1);
                        const eased = 1 - Math.pow(1 - progress, 3);
                        el.textContent = 'K ' + Math.round(target * eased).toLocaleString();
                        if (progress < 1) requestAnimationFrame(tick);
                    }
                    requestAnimationFrame(tick);
                }
            } else {
                animateCount(el, target, suffix);
            }
        });

        document.querySelectorAll('.chart-line').forEach((line) => line.classList.add('is-drawn'));

        document.querySelectorAll('.browser-mock__alert').forEach((alert, i) => {
            setTimeout(() => {
                alert.style.opacity = '1';
            }, prefersReducedMotion ? 0 : 800 + i * 200);
        });
    }

    /* ── Team card stagger ── */
    const teamCards = document.querySelectorAll('.landing-team-card');
    if (teamCards.length && !prefersReducedMotion) {
        const teamObserver = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        teamCards.forEach((card, i) => {
                            setTimeout(() => {
                                card.style.opacity = '1';
                                card.style.transform = 'translateY(0)';
                            }, i * 100);
                        });
                        teamObserver.disconnect();
                    }
                });
            },
            { threshold: 0.1 }
        );
        teamCards.forEach((card) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'opacity 0.5s cubic-bezier(0.22, 1, 0.36, 1), transform 0.5s cubic-bezier(0.22, 1, 0.36, 1)';
        });
        const teamSection = document.querySelector('#team');
        if (teamSection) teamObserver.observe(teamSection);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', runHeroEntrance);
    } else {
        runHeroEntrance();
    }
})();
