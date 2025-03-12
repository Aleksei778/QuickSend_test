function handleNonChromeBrowser() {
    const isChrome = /Chrome/.test(navigator.userAgent) && /Google Inc/.test(navigator.vendor);
    const allTargetButtons = document.querySelectorAll('.startforfree, .hero-button.primary, .products-section button');

    if (!isChrome) {
        allTargetButtons.forEach(button => {
            button.setAttribute('data-non-chrome', 'true');
            button.setAttribute('data-ru', 'Только для Chrome');
            button.setAttribute('data-en', 'Chrome only');
            updateButtonForNonChrome(button);
        });
    }
}

function updateButtonForNonChrome(button) {
    button.style.backgroundColor = '#cccccc';
    button.style.cursor = 'not-allowed';
    button.style.boxShadow = 'none';

    const text = button.getAttribute(`data-${currentLanguage}`);
    if (text) {
        button.textContent = text;
    }
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
            element.innerHTML = `${currencySymbol}${price}<span class="price-period">${monthText}</span>`;
        }
    });
}

function initializeLanguageToggle() {
    const languageToggle = document.querySelector('.language-toggle');
    
    if (languageToggle) {
        languageToggle.removeEventListener('click', handleLanguageToggle);
        languageToggle.addEventListener('click', handleLanguageToggle);
    }
}

function handleLanguageToggle() {
    currentLanguage = currentLanguage === 'ru' ? 'en' : 'ru';
    
    const toggleSpan = document.querySelector('.language-toggle span');
    if (toggleSpan) {
        toggleSpan.textContent = currentLanguage === 'ru' ? 'EN' : 'RU';
    }
    
    document.documentElement.lang = currentLanguage;
    updateLanguage();
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

document.addEventListener("DOMContentLoaded", () => {

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
    
    initializeLanguageToggle();
    updateLanguage();
    handleNonChromeBrowser();
});