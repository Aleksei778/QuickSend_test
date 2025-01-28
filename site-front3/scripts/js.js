function handleNonChromeBrowser() {
    const isChrome = /Chrome/.test(navigator.userAgent) && /Google Inc/.test(navigator.vendor);
    
    // Select all relevant buttons
    const allTargetButtons = document.querySelectorAll('.startforfree, .hero-button.primary, .products-section button');
    
    if (!isChrome) {
        allTargetButtons.forEach(button => {
            button.setAttribute('data-non-chrome', 'true');
            button.setAttribute('data-ru', 'Доступно только для Chrome');
            button.setAttribute('data-en', 'Available only for Chrome');
            updateButtonForNonChrome(button);
        });
    }
}

function updateButtonForNonChrome(button) {
    // Apply non-Chrome styling
    button.style.backgroundColor = '#cccccc';
    button.style.cursor = 'not-allowed';
    button.style.pointerEvents = 'none';
    button.style.boxShadow = 'none';
    
    // Set text based on current language
    button.textContent = button.getAttribute(`data-${currentLanguage}`);
}

// Sparkles Effect
function createSparkle(x, y) {
    const sparkle = document.createElement("div");
    sparkle.className = "sparkle";
    sparkle.style.left = x + "px";
    sparkle.style.top = y + "px";
    document.body.appendChild(sparkle);

    setTimeout(() => {
        sparkle.remove();
    }, 800);
}

function addSparkles(event) {
    const button = event.target;
    const rect = button.getBoundingClientRect();
    const buttonWidth = rect.width;
    const buttonHeight = rect.height;

    for (let i = 0; i < 20; i++) {
        const x = rect.left + Math.random() * buttonWidth;
        const y = rect.top + Math.random() * buttonHeight;
        createSparkle(x, y);
    }
}

// Authentication Simulation
function simulateUserAuth() {
    document.querySelector(".signin-button").style.display = "none";
    document.querySelector(".startforfree").style.display = "none";
    document.querySelector(".profile-button").style.display = "flex";
}

// Language Management
let currentLanguage = "ru";

const translations = {
    pricing: {
        ru: {
            currency: "₽",
            free: "Бесплатно",
            month: "/месяц",
        },
        en: {
            currency: "$",
            free: "Free",
            month: "/month",
        },
    },
};

function updatePricing() {
    const priceElements = document.querySelectorAll(".price");
    priceElements.forEach((element) => {
        const price = element.getAttribute(`data-${currentLanguage}-price`);
        const currencySymbol = translations.pricing[currentLanguage].currency;
        const monthText = translations.pricing[currentLanguage].month;

        if (price === "0") {
            element.textContent = translations.pricing[currentLanguage].free;
        } else {
            element.textContent = `${currencySymbol}${price}${monthText}`;
        }
    });
}

function updateLanguage() {
    const elements = document.querySelectorAll("[data-ru][data-en]");
    elements.forEach((element) => {
        if (element.hasAttribute('data-non-chrome')) {
            updateButtonForNonChrome(element);
        } else {
            element.textContent = element.getAttribute(`data-${currentLanguage}`);
        }
    });
    updatePricing();
}


function toggleLanguage() {
    currentLanguage = currentLanguage === "ru" ? "en" : "ru";
    updateLanguage();
    document.documentElement.lang = currentLanguage;
    const toggleText = document.querySelector(".language-toggle span");
    toggleText.textContent = currentLanguage === "ru" ? "EN" : "RU";
}

// Event Listeners
document.addEventListener("DOMContentLoaded", () => {
    // Button sparkles - exclude nav-menu items
    const buttons = document.querySelectorAll(".button:not(.nav-menu a)");
    buttons.forEach((button) => {
        button.addEventListener("click", addSparkles);
    });
   
    document.getElementById("current-year").textContent = new Date().getFullYear();

    // Smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
        anchor.addEventListener("click", function (e) {
            e.preventDefault();
            const targetId = this.getAttribute("href").substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: "smooth",
                });
            }
        });
    });

    document.querySelector(".language-toggle").addEventListener("click", toggleLanguage);

    updateLanguage();
    handleNonChromeBrowser();
});

document.addEventListener('DOMContentLoaded', function() {
    const heroElements = document.querySelectorAll('.hero-section h1, .hero-section p, .hero-buttons, .chill-guy, .chill-girl');
    heroElements.forEach(el => {
      el.classList.add('fade-in');
      setTimeout(() => el.classList.add('visible'), 200);
    });

    const animatedSections = document.querySelectorAll('.whyquicksend-section, .stats-section, .pricing-section, .products-section');
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          if (!entry.target.classList.contains('contact-us-section')) {
            const elements = entry.target.querySelectorAll('.advantage, .stat-item, .pricing-column, .product-card');
            elements.forEach((el, index) => {
              el.classList.add('fade-in');
              setTimeout(() => el.classList.add('visible'), index * 200);
            });
          }
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.15,
      rootMargin: '20px'
    });
  
    animatedSections.forEach(section => {
      section.querySelectorAll('.advantage, .stat-item, .pricing-column, .product-card')
        .forEach(el => el.classList.add('fade-in'));
      observer.observe(section);
    });
  });
  