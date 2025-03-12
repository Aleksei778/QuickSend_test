function handleNonChromeBrowser() {
    const isChrome = /Chrome/.test(navigator.userAgent) && /Google Inc/.test(navigator.vendor);
    const allTargetButtons = document.querySelectorAll('.startforfree, .hero-button.primary, .products-section button');

    if (!isChrome) {
        allTargetButtons.forEach(button => {
            button.setAttribute('data-non-chrome', 'true');
            button.setAttribute('data-ru', 'Только для Chrome');
            button.setAttribute('data-en', 'Chrome Only');
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
// Auth Simulation
function initializeAuthButtons() {
    const startFreeButton = document.querySelector(".startforfree");
    const signInButton = document.querySelector(".signin-button");

    if (startFreeButton) {
        startFreeButton.addEventListener("click", (e) => {
            e.preventDefault();
            simulateUserAuth();
        });
    }

    if (signInButton) {
        signInButton.addEventListener("click", (e) => {
            e.preventDefault();
            simulateUserAuth();
        });
    }
}

function simulateUserAuth() {
    const signInBtn = document.querySelector(".signin-button");
    const startFreeBtn = document.querySelector(".startforfree");
    const profileBtn = document.querySelector(".profile-button");

    if (signInBtn) signInBtn.style.display = "none";
    if (startFreeBtn) startFreeBtn.style.display = "none";
    if (profileBtn) profileBtn.style.display = "flex";
}

// Language Management
let currentLanguage = "ru";

const translations = {
    pricing: {
        ru: {
            currency: "₽",
            free: "Бесплатно",
            month: "/месяц",
            billed: "при оплате",
            annually: "за год"
        },
        en: {
            currency: "$",
            free: "Free",
            month: "/month",
            billed: "billed",
            annually: "yearly"
        }
    }
};

function updatePricing() {
    const priceElements = document.querySelectorAll('.price');
    const isAnnual = document.getElementById('billingToggle').checked;
    const currentTranslation = translations.pricing[currentLanguage];
    
    priceElements.forEach((element) => {
        const basePrice = parseFloat(element.getAttribute(`data-${currentLanguage}-price`));
        
        if (basePrice === 0) {
            element.innerHTML = currentTranslation.free;
            return;
        }
        
        if (isNaN(basePrice)) {
            console.error('Invalid price value:', element);
            return;
        }
        
        if (isAnnual) {
            const annualPrice = (basePrice * 12 * 0.8).toFixed(0.1);
            const monthlyPrice = (basePrice * 0.8).toFixed(0.1);
            
            element.innerHTML = `
                <span class="price-amount">${currentTranslation.currency}${monthlyPrice}</span>
                <span class="price-period">${currentTranslation.month}</span>
                <div class="annual-note">
                    ${currentTranslation.billed} ${currentTranslation.currency}${annualPrice} ${currentTranslation.annually}
                </div>
            `;
        } else {
            element.innerHTML = `
                <span class="price-amount">${currentTranslation.currency}${basePrice}</span>
                <span class="price-period">${currentTranslation.month}</span>
            `;
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
        const translatedText = element.getAttribute(`data-${currentLanguage}`);
        if (element.hasAttribute('data-non-chrome')) {
            updateButtonForNonChrome(element);
        } else {
            const icon = element.querySelector('i');
            if (icon) {
                const iconHtml = icon.outerHTML;
                element.innerHTML = iconHtml + ' ' + translatedText;
            } else {
                element.textContent = translatedText;
            }
        }
    });

    // Update language toggle
    const toggleSpan = document.querySelector('.language-toggle span');
    if (toggleSpan) {
        toggleSpan.textContent = currentLanguage.toUpperCase() === 'RU' ? 'EN' : 'RU';
    }

    // Preserve feature list icons
    const featureItems = document.querySelectorAll('.features-list li');
    featureItems.forEach(item => {
        const isDisabled = item.classList.contains('disabled');
        const translatedText = item.getAttribute(`data-${currentLanguage}`);
        const iconClass = isDisabled ? 'fa-times' : 'fa-check';
        item.innerHTML = `<i class="fas ${iconClass}"></i> ${translatedText}`;
    });

    // Update section title and description
    const sectionTitle = document.querySelector('.section-single h1');
    const sectionDesc = document.querySelector('.section-single p');
    if (sectionTitle) {
        sectionTitle.textContent = sectionTitle.getAttribute(`data-${currentLanguage}`);
    }
    if (sectionDesc) {
        sectionDesc.textContent = sectionDesc.getAttribute(`data-${currentLanguage}`);
    }

    updatePricing();
}


document.addEventListener("DOMContentLoaded", () => {

    document.querySelector(".startforfree").addEventListener("click", (e) => {
        e.preventDefault();
        simulateUserAuth();
    });

    document.querySelector(".signin-button").addEventListener("click", (e) => {
        e.preventDefault();
        simulateUserAuth();
    });

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
    
    const billingToggle = document.getElementById('billingToggle');
    if (billingToggle) {
        billingToggle.addEventListener('change', updatePricing);
    }

    updatePricing();

    handleNonChromeBrowser();

    initializeAuthButtons();

    initializeLanguageToggle();
});

document.getElementById('billingToggle').addEventListener('change', function() {
    const isAnnual = this.checked;
    const priceElements = document.querySelectorAll('.price');
    
    priceElements.forEach(element => {
        const monthlyPrice = parseFloat(element.getAttribute('data-monthly-price'));
        const annualPrice = parseFloat(element.getAttribute('data-annual-price'));
        
        if (monthlyPrice === 0) {
            element.textContent = 'Free';
            return;
        }
        
        if (isAnnual) {
            const annualMonthly = (annualPrice / 12).toFixed(2);
            element.innerHTML = `${annualMonthly}₽/month<br><small>Billed ${annualPrice}₽ annually</small>`;
        } else {
            element.textContent = `${monthlyPrice}₽/month`;
        }
    });
});