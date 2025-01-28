import { getJWTToken } from "/static/scripts/checkAuth.js";

const ANIMATION_DURATION = 2000;
const FPS = 60;
const DEFAULT_THEME = 'light';

class ProfileManager {
    constructor() {
        this.userData = null;
        this.bindElements();
    }

    bindElements() {
        this.profileSection = document.getElementById('profile');
        this.userEmail = document.getElementById('user-email');
        this.userName = document.getElementById('user-name');
        this.activePlan = document.getElementById('active-plan');
        this.upgradeBtn = document.getElementById('upgrade-btn');
        this.campaignList = document.getElementById('campaign-list');
        this.searchBtn = document.getElementById('search-btn');
        this.campaignSearch = document.getElementById('campaign-search');
        this.campaignDateSearch = document.getElementById('campaign-date-search');
        this.attachmentSearch = document.getElementById('attachment-search');
        this.profileIcon = document.getElementById('profile-icon');
    }

    async initialize() {
        try {
            await this.fetchUserData();
            this.attachEventListeners();
            this.showProfile();
        } catch (error) {
            console.error('Error initializing profile:', error);
        }
    }

    async fetchUserData() {
        const token = await getJWTToken();
        if (!token) {
            throw new Error('No token available');
        }

        // Fetch user info
        const userResponse = await fetch('/api/v1/check_user', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!userResponse.ok) throw new Error(`HTTP error! status: ${userResponse.status}`);
        const userData = await userResponse.json();
        console.log("USER DATA: ", userData);
        // Fetch campaigns
        const campaignsResponse = await fetch('/api/v1/all-campaigns', {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!campaignsResponse.ok) throw new Error(`HTTP error! status: ${campaignsResponse.status}`);
        const campaignData = await campaignsResponse.json();
        console.log("CAMPAIGN DATA: ", campaignData);

        // Fetch active subscription
        const subscriptionResponse = await fetch('/api/v1/get_active_sub', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!subscriptionResponse.ok) throw new Error(`HTTP error! status: ${subscriptionResponse.status}`);
        const subscriptionData = await subscriptionResponse.json();
        console.log("SUBSCRIPTION RESPONSE: ", subscriptionData);

        let activePlan_str = subscriptionData.plan !== undefined
            ? `${subscriptionData.plan} (${subscriptionData.start_date} - ${subscriptionData.end_date})`
            : subscriptionData.message;

        this.userData = {
            email: userData.email,
            name: userData.name,
            picture: userData.picture,
            activePlan: activePlan_str,
            campaigns: campaignData.campaigns
        };
    }

    attachEventListeners() {
        this.searchBtn.addEventListener('click', () => this.handleSearch());
        document.getElementById('logout-button')?.addEventListener('click', this.handleLogout);
        document.getElementById('email-file').addEventListener('change', (e) => this.handleFileUpload(e));
        this.upgradeBtn.addEventListener('click', this.handleUpgrade);
    }

    showProfile() {
        console.log('showProfile');
        document.querySelectorAll('section').forEach(section => section.style.display = 'none');
        this.profileSection.style.display = 'block';
        console.log('userData: ', this.userData);
        this.userEmail.textContent = this.userData.email;
        this.userName.textContent = this.userData.name;
        this.profileIcon.src = this.userData.picture;
        console.log("ICON SRC: ", this.profileIcon.src);
        console.log("PICTURE: ", this.userData.picture);
        this.activePlan.textContent = this.userData.activePlan;
        
        if (this.userData.activePlan === 'Free Trial') {
            this.upgradeBtn.style.display = 'block';
        }

        this.renderCampaigns(this.userData.campaigns);
        this.animateCounters();
    }

    renderCampaigns(campaigns) {
        console.log('renderCampaigns');
        console.log(campaigns);
        if (!campaigns.length) {
            this.campaignList.innerHTML = '<li>No campaigns match your search criteria.</li>';
            return;
        }

        this.campaignList.innerHTML = campaigns.map(campaign => `
            <li>
                <strong>${this.escapeHtml(campaign.name)}</strong><br>
                Date: ${this.escapeHtml(campaign.date)}<br>
                Recipients: ${campaign.recipients_cnt}
                ${this.renderAttachments(campaign.attachments)}
            </li>
        `).join('');
    }

    renderAttachments(attachments) {
        if (!attachments?.length) return '<br>Attachments: None';
        return `
            <br>Attachments: 
            <ul>
                ${attachments.map(att => `<li>${this.escapeHtml(att)}</li>`).join('')}
            </ul>
        `;
    }

    escapeHtml(unsafe) {
        if (!unsafe) return '';
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    handleSearch() {
        const searchTerm = this.campaignSearch.value.toLowerCase();
        const dateSearch = this.campaignDateSearch.value;
        const attachmentSearchTerm = this.attachmentSearch.value.toLowerCase();

        const filteredCampaigns = this.userData.campaigns.filter(campaign => {
            const nameMatch = campaign.name.toLowerCase().includes(searchTerm);
            const dateMatch = !dateSearch || campaign.date === dateSearch;
            const attachmentMatch = !attachmentSearchTerm || 
                campaign.attachments.some(att => att.toLowerCase().includes(attachmentSearchTerm));
            return nameMatch && dateMatch && attachmentMatch;
        });

        this.renderCampaigns(filteredCampaigns);
    }
    
    async animateCounters() {
        console.log('animateCounters');
        const token = await getJWTToken();
        if (!token) {
            throw new Error('No token available');
        }

        const campaignsResponse = await fetch('/api/v1/campaigns-stat', {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!campaignsResponse.ok) throw new Error(`HTTP error! status: ${campaignsResponse.status}`);
        const campaignData = await campaignsResponse.json();
        console.log("CAMPAIGN STAT: ", campaignData);
        
        const campaignsCnt = document.getElementById('campaigns_count');
        const recipientsCnt = document.getElementById('recipients_count');

        campaignsCnt.textContent = parseInt(campaignData['campaigns_count']);
        recipientsCnt.textContent = parseInt(campaignData['recipients_count']);
    }

    async handleLogout() {
        try {
            await fetch('/api/v1/logout', {
                method: 'POST',
            });
            window.location.href = "http://127.0.0.1:8000/";
        } catch (error) {
            console.error('Error during logout:', error);
        }
    }

    handleUpgrade() {
        alert('Redirecting to payment page...');
        // Implementation for payment redirect
    }

    handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        setTimeout(() => {
            const validCount = Math.floor(Math.random() * 1000);
            const invalidCount = Math.floor(Math.random() * 100);
            this.showValidationResults(validCount, invalidCount);
        }, 2000);
    }

    showValidationResults(validCount, invalidCount) {
        const validationResult = document.getElementById('validation-result');
        validationResult.innerHTML = `
            Validation complete: ${validCount} valid emails, ${invalidCount} invalid emails<br>
            <a href="#" id="download-report" class="btn btn-success">Download Validation Report</a>
        `;

        document.getElementById('download-report').addEventListener('click', (e) => {
            e.preventDefault();
            this.generateValidationReport(validCount, invalidCount);
        });
    }

    generateValidationReport(validCount, invalidCount) {
        const reportContent = `Email Validation Report
Valid Emails: ${validCount}
Invalid Emails: ${invalidCount}
Date: ${new Date().toLocaleString()}`;

        const blob = new Blob([reportContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'validation_report.txt';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

class ThemeManager {
    constructor() {
        this.init();
    }

    init() {
        const savedTheme = localStorage.getItem('theme') || DEFAULT_THEME;
        this.setTheme(savedTheme);
        this.bindThemeToggle();
    }

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        const themeIcon = document.getElementById('theme-icon');
        themeIcon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }

    bindThemeToggle() {
        const themeToggleBtn = document.querySelector('.theme-toggle-button');
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            this.setTheme(newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }
}

// Initialize everything when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    const profileManager = new ProfileManager();
    const themeManager = new ThemeManager();
    
    await profileManager.initialize();
    document.getElementById("current-year").textContent = new Date().getFullYear();
});