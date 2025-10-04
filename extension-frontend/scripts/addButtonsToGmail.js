// SVG icons as strings
const svgIcons = {
    table: `<?xml version="1.0" encoding="utf-8"?>
        <!-- Uploaded to: SVG Repo, www.svgrepo.com, Generator: SVG Repo Mixer Tools -->
        <svg width="24" height="24" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
        <g id="list-square-2" transform="translate(-2 -2)">
            <rect id="secondary" fill="#1a73e8" width="18" height="18" rx="1" transform="translate(3 3)"/>
            <line id="primary-upstroke" x1="0.1" transform="translate(16.45 8)" fill="none" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5"/>
            <line id="primary-upstroke-2" data-name="primary-upstroke" x1="0.1" transform="translate(16.45 12)" fill="none" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5"/>
            <line id="primary-upstroke-3" data-name="primary-upstroke" x1="0.1" transform="translate(16.45 16)" fill="none" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5"/>
            <path id="primary" d="M12,8H7m0,4h5M7,16h5M20,3H4A1,1,0,0,0,3,4V20a1,1,0,0,0,1,1H20a1,1,0,0,0,1-1V4A1,1,0,0,0,20,3Z" fill="none" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
        </g>
        </svg>`,

    profile: `<?xml version="1.0" encoding="utf-8"?>
        <!-- Uploaded to: SVG Repo, www.svgrepo.com, Generator: SVG Repo Mixer Tools -->
        <svg width="24" height="24" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
        <g id="user-square" transform="translate(-2 -2)">
            <path id="secondary" fill="#1a73e8" d="M20,3H4A1,1,0,0,0,3,4V20a1,1,0,0,0,1,1H7V20a5,5,0,0,1,5-5,4,4,0,1,1,4-4,4,4,0,0,1-4,4,5,5,0,0,1,5,5v1h3a1,1,0,0,0,1-1V4A1,1,0,0,0,20,3Z"/>
            <path id="primary" d="M12,15h0a5,5,0,0,0-5,5v1H17V20A5,5,0,0,0,12,15Zm0-8a4,4,0,1,0,4,4A4,4,0,0,0,12,7Zm8,14H4a1,1,0,0,1-1-1V4A1,1,0,0,1,4,3H20a1,1,0,0,1,1,1V20A1,1,0,0,1,20,21Z" fill="none" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
        </g>
        </svg>`,

    website: `<?xml version="1.0" encoding="utf-8"?><!-- Uploaded to: SVG Repo, www.svgrepo.com, Generator: SVG Repo Mixer Tools -->
        <svg fill="#000000" width="24" height="24" viewBox="0 0 24 24" id="world" data-name="Flat Line" xmlns="http://www.w3.org/2000/svg" class="icon flat-line"><ellipse id="secondary" cx="12" cy="12" rx="3" ry="9" style="fill: #1a73e8; stroke-width: 2;"></ellipse><path id="primary" d="M21,12a9,9,0,1,1-9-9A9,9,0,0,1,21,12ZM12,3c-1.66,0-3,4-3,9s1.34,9,3,9,3-4,3-9S13.66,3,12,3Z" style="fill: none; stroke: rgb(0, 0, 0); stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path><path id="primary-2" data-name="primary" d="M19.2,17.4a9.7,9.7,0,0,0-4.42-2.1,13,13,0,0,0-5.56,0A9.7,9.7,0,0,0,4.8,17.4" style="fill: none; stroke: rgb(0, 0, 0); stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path><path id="primary-3" data-name="primary" d="M19.2,6.6a9.7,9.7,0,0,1-4.42,2.1A12.53,12.53,0,0,1,12,9a12.53,12.53,0,0,1-2.78-.3A9.7,9.7,0,0,1,4.8,6.6" style="fill: none; stroke: rgb(0, 0, 0); stroke-linecap: round; stroke-linejoin: round; stroke-width: 2;"></path></svg>`
};

function createButton(id, iconKey, title) {
    const button = document.createElement('button');
    button.id = id;
    button.className = 'custom-icon-button';
    button.title = title;
    button.innerHTML = svgIcons[iconKey];
    return button;
}

async function addParseTablesButton() {
    const result_token = await chrome.storage.local.get(['accessToken']);
    if (!result_token.accessToken) {
        console.log('Token not found');
        return;
    } else {
        const token = result_token.accessToken;
        const subscriptionResponse = await fetch('http://127.0.0.1:8000/api/v1/get_active_sub', {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const subscriptionData = await subscriptionResponse.json();
        console.log("SUBSCRIPTION RESPONSE: ", subscriptionData);
    
        if (subscriptionData.plan === undefined || subscriptionData.plan === "free_trial") {
            return;
        }
    
        const button = createButton('table-button', 'table', 'Parse recipients from GoogleSheets');
        addButtonToPage(button);
    }
}

function addProfileButton() {
    const button = createButton('profile-button', 'profile', 'Go to your profile');
    // Добавляем обработчик события 'click', который будет перенаправлять на сайт
    button.addEventListener('click', async function() {
        const result_token = await chrome.storage.local.get(['accessToken']);
        const token = result_token.accessToken;
        console.log("Токен после удаления, ", token);
        if (!token) {
            window.open('http://127.0.0.1:8000/api/v1/login', '_blank');
            
        } else {
            window.open('http://127.0.0.1:8000/profile', '_blank');   
        }
    });
    addButtonToPage(button);
}

function removeToken() {
    chrome.storage.local.remove(['accessToken'], function() {
        console.log('Access token removed');
    });
}

function addWebsiteButton() {
    const button = createButton('website-button', 'website', 'Link to our website');
    // Добавляем обработчик события 'click', который будет перенаправлять на сайт
    button.addEventListener('click', function() {
        window.open('http://5.159.102.196', '_blank');
    });
    addButtonToPage(button);
}

function addButtonToPage(button) {
    const elems = document.getElementsByClassName("zo");
    if (elems.length === 0) {
        console.log("Element not found");
        return;
    }
    const elem = elems[0];
    elem.parentNode.insertBefore(button, elem);
}

// Check for OAuth callback on page load
window.addEventListener('load', () => {
    setTimeout(async () => {
        await addParseTablesButton();
        addProfileButton();
        addWebsiteButton();
    }, 5000);
});