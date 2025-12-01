// script.js - Dnails por Diana Ortiz
// Lógica principal de interacción

// 1. Efecto de scroll en la barra de navegación
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
    if (window.scrollY > 10) {
        navbar.classList.add('bg-white/90', 'backdrop-blur-md', 'shadow-sm');
    } else {
        navbar.classList.remove('bg-white/90', 'backdrop-blur-md', 'shadow-sm');
    }
});

// 2. Alternar menú móvil
const mobileMenuButton = document.getElementById('mobile-menu-button');
const mobileMenu = document.getElementById('mobile-menu');

function closeMobileMenu() {
    if (mobileMenu && !mobileMenu.classList.contains('hidden')) {
        mobileMenu.classList.add('hidden');
    }
}

if (mobileMenuButton && mobileMenu) {
    mobileMenuButton.addEventListener('click', () => {
        mobileMenu.classList.toggle('hidden');
    });
}

// 3. Función para desplazarse a una sección
function scrollToSection(sectionId) {
    const targetElement = document.getElementById(sectionId);
    if (targetElement) {
        // Cierra el menú móvil si está abierto
        closeMobileMenu();
        // Desplázate a la sección
        targetElement.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// 4. Desplazamiento suave para enlaces de anclaje
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const targetId = this.getAttribute('href').substring(1); // Obtiene el ID sin el '#'
        if (targetId) {
            scrollToSection(targetId);
        }
    });
});

// 5. Cierre del menú móvil al hacer clic en un enlace interno
document.querySelectorAll('#mobile-menu a[href^="#"]').forEach(link => {
    link.addEventListener('click', closeMobileMenu);
});

// 6. Cierre del menú móvil al hacer clic fuera de él
document.addEventListener('click', function(event) {
    if (mobileMenu && !mobileMenu.contains(event.target) && !mobileMenuButton.contains(event.target)) {
        closeMobileMenu();
    }
});
// 7. Efecto BlurText (Adaptación de React a Vanilla JS + GSAP)
function initBlurText() {
    // Asegurarse de que GSAP y ScrollTrigger estén disponibles
    if (typeof gsap === 'undefined') {
        console.warn('GSAP no está cargado');
        return;
    }
    
    // Registrar ScrollTrigger si está disponible
    if (typeof ScrollTrigger !== 'undefined') {
        gsap.registerPlugin(ScrollTrigger);
    }

    const elements = document.querySelectorAll('.blur-text');

    elements.forEach(element => {
        // Evitar procesar elementos que ya tienen hijos (para no romper estructuras complejas)
        // o si ya fue procesado
        if (element.children.length > 0 && !element.dataset.processed) return;
        
        const text = element.innerText;
        const words = text.split(' ');
        
        element.innerHTML = '';
        element.dataset.processed = "true"; // Marcar como procesado
        
        words.forEach((word, index) => {
            const span = document.createElement('span');
            span.textContent = word + (index < words.length - 1 ? ' ' : '');
            span.style.display = 'inline-block';
            span.style.willChange = 'transform, filter, opacity';
            span.style.opacity = '0'; // Inicialmente invisible para evitar parpadeos
            element.appendChild(span);
        });

        gsap.fromTo(element.children, 
            {
                filter: 'blur(10px)',
                opacity: 0,
                y: -50
            },
            {
                filter: 'blur(0px)',
                opacity: 1,
                y: 0,
                duration: 0.8,
                stagger: 0.1,
                ease: "power3.out",
                scrollTrigger: {
                    trigger: element,
                    start: "top 90%", // Disparar un poco antes (más abajo en la pantalla)
                    toggleActions: "play none none reverse"
                }
            }
        );
    });
}

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    initBlurText();
});

// 8. Efecto Scroll Float (Adaptación de React a Vanilla JS + GSAP)
function initScrollFloat() {
    // Asegurarse de que GSAP y ScrollTrigger estén disponibles
    if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') return;

    const elements = document.querySelectorAll('.scroll-float');

    elements.forEach(element => {
        if (element.dataset.processed) return;
        element.dataset.processed = "true";

        const text = element.innerText;
        element.innerHTML = '';
        
        const textWrapper = document.createElement('span');
        textWrapper.className = 'scroll-float-text';
        
        text.split('').forEach(char => {
            const span = document.createElement('span');
            span.className = 'char';
            span.textContent = char === ' ' ? '\u00A0' : char;
            textWrapper.appendChild(span);
        });
        
        element.appendChild(textWrapper);

        const chars = textWrapper.querySelectorAll('.char');

        gsap.fromTo(chars, 
            {
                willChange: 'opacity, transform',
                opacity: 0,
                yPercent: 120,
                scaleY: 2.3,
                scaleX: 0.7,
                transformOrigin: '50% 0%'
            },
            {
                duration: 1,
                ease: 'back.inOut(2)',
                opacity: 1,
                yPercent: 0,
                scaleY: 1,
                scaleX: 1,
                stagger: 0.03,
                scrollTrigger: {
                    trigger: element,
                    start: 'center bottom+=50%',
                    end: 'bottom bottom-=40%',
                    scrub: true
                }
            }
        );
    });
}

// Agregar a la inicialización
document.addEventListener('DOMContentLoaded', () => {
    initScrollFloat();
});

// 9. Efecto de Destellos (Sparkles) al mover el mouse
function initSparkles() {
    const colors = ['#dcb4b4', '#c5a065', '#e5c590', '#ffffff'];
    let throttleTimer;

    document.addEventListener('mousemove', (e) => {
        if (throttleTimer) return;
        throttleTimer = setTimeout(() => {
            throttleTimer = null;
            createSparkle(e.clientX, e.clientY);
        }, 50); // Limitar la cantidad de partículas
    });

    function createSparkle(x, y) {
        const sparkle = document.createElement('div');
        sparkle.classList.add('sparkle');
        
        // Estilos inline para la posición y aleatoriedad
        const size = Math.random() * 10 + 5;
        const color = colors[Math.floor(Math.random() * colors.length)];
        
        sparkle.style.width = `${size}px`;
        sparkle.style.height = `${size}px`;
        sparkle.style.left = `${x}px`;
        sparkle.style.top = `${y}px`;
        sparkle.style.backgroundColor = color;
        sparkle.style.position = 'fixed';
        sparkle.style.borderRadius = '50%';
        sparkle.style.pointerEvents = 'none';
        sparkle.style.zIndex = '9999';
        sparkle.style.boxShadow = `0 0 ${size/2}px ${color}`;
        
        // Animación con GSAP
        document.body.appendChild(sparkle);
        
        gsap.to(sparkle, {
            x: (Math.random() - 0.5) * 50,
            y: (Math.random() - 0.5) * 50 + 20,
            opacity: 0,
            scale: 0,
            duration: 1,
            ease: "power1.out",
            onComplete: () => {
                sparkle.remove();
            }
        });
    }
}

// Agregar a la inicialización
document.addEventListener('DOMContentLoaded', () => {
    initSparkles();
});
