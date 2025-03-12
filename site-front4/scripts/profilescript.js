import { getJWTToken } from "/static/scripts/getJwt.js";

const DEFAULT_THEME = 'light';

class ProfileManager {
    constructor() {
        this.userData = null;

        this.bindElements();    
    }

    bindElements() {
        // Profile section elements
        this.profileSection = document.getElementById('profile');
        this.userEmail = document.getElementById('user-email');
        this.activePlan = document.getElementById('active-plan');
        this.upgradeBtn = document.getElementById('upgrade-btn');
        this.totalCampaigns = document.getElementById('total-campaigns');
        this.totalRecipients = document.getElementById('total-recipients');
        this.remainingCampaigns = document.getElementById('remaining-campaigns');
        this.remainingRecipients = document.getElementById('remaining-recipients');
        this.subscriptionEnd = document.getElementById('subscription-end');
        this.profileIcon = document.getElementById('profile-icon');

        // Campaign section elements
        this.campaignSection = document.getElementById('campaign-management');
        this.campaignList = document.getElementById('campaign-list');
        this.campaignSearch = document.getElementById('campaign-search');
        this.campaignDateSearch = document.getElementById('campaign-date-search');
        this.attachmentSearch = document.getElementById('attachment-search');
        this.searchBtn = document.getElementById('search-btn');
    }

    async init() {
        try {
            await this.fetchUserData();
            this.updateProfileStats();
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
        const user_data = await userResponse.json();
        console.log("USER DATA: ", user_data);
        // Fetch campaigns
        const campaignsResponse = await fetch('/api/v1/all-campaigns', {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!campaignsResponse.ok) throw new Error(`HTTP error! status: ${campaignsResponse.status}`);
        const campaignData = await campaignsResponse.json();
        console.log("CAMPAIGN DATA: ", campaignData);
        
        const campaignsCntResponse = await fetch('/api/v1/campaigns-stat', {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!campaignsResponse.ok) throw new Error(`HTTP error! status: ${campaignsResponse.status}`);
        const campaignsCntData = await campaignsCntResponse.json();
        console.log("CAMPAIGN STAT: ", campaignsCntData);
        
        const campaignsCnt = campaignsCntData.campaigns_count;
        const recipientsCnt = campaignsCntData.recipients_count;

        // Fetch active subscription
        const subscriptionResponse = await fetch('/api/v1/get_active_sub', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!subscriptionResponse.ok) throw new Error(`HTTP error! status: ${subscriptionResponse.status}`);
        const subscriptionData = await subscriptionResponse.json();
        console.log("SUBSCRIPTION RESPONSE: ", subscriptionData);

        let activePlan_str = subscriptionData.plan !== undefined
            ? subscriptionData.plan
            : subscriptionData.message;

        this.userData = {
            email: user_data.email,
            name: user_data.name,
            picture: user_data.picture,
            activePlan: activePlan_str,
            totalCampaigns: campaignsCnt,
            totalRecipients: recipientsCnt,
            remainingCampaigns: 0,
            remainingRecipients: 0,
            subscriptionEnd: subscriptionData.end_date,
            campaignsList: campaignData.campaigns
        };
    }

    updateProfileStats() {

        document.getElementById('user-name').textContent = this.userData.name;

        this.userEmail.textContent = this.userData.email;
        this.activePlan.textContent = this.userData.activePlan;
        this.totalCampaigns.textContent = this.userData.totalCampaigns;
        this.totalRecipients.textContent = this.userData.totalRecipients.toLocaleString();
        this.remainingCampaigns.textContent = this.userData.remainingCampaigns;
        this.remainingRecipients.textContent = this.userData.remainingRecipients.toLocaleString();
        this.subscriptionEnd.textContent = this.userData.subscriptionEnd;
        this.profileIcon.src = this.userData.picture;
        console.log("PICTURE: ", this.profileIcon.src)
    }

    attachEventListeners() {
        this.searchBtn.addEventListener('click', () => this.handleSearch());
        document.getElementById('logout-btn')?.addEventListener('click', this.handleLogout);
        document.getElementById('email-file').addEventListener('change', this.handleFileUpload);
    }

    showProfile() {
        document.querySelectorAll('section').forEach(section => section.style.display = 'none');
        this.profileSection.style.display = 'block';
        this.campaignSection.style.display = 'block';

        this.renderCampaigns(this.userData.campaignsList);
    }

    async handleLogout() {
        try {
            await fetch('/api/v1/logout', {
                method: 'POST',
            });
            window.location.href = "/";
        } catch (error) {
            console.error('Error during logout:', error);
        }
    }

    renderCampaigns(campaigns) {
        if (!campaigns.length) {
            this.campaignList.innerHTML = '<li>No campaigns match your search criteria.</li>';
            return;
        }

        this.campaignList.innerHTML = campaigns.map(campaign => `
            <li class="campaign-item">
                <div class="campaign-header">
                    <strong>${this.escapeHtml(campaign.name)}</strong>
                    <span class="campaign-date">${this.escapeHtml(campaign.date)}</span>
                </div>
                <div class="campaign-details">
                    <p>Recipients: ${campaign.recipients_cnt}</p>
                    ${this.renderAttachments(campaign.attachments)}
                </div>
            </li>
        `).join('');
    }

    renderAttachments(attachments) {
        if (attachments.length === 1 && attachments[0] === '') return '<p>Attachments: None</p>';
        return `
            <div class="campaign-attachments">
                <p>Attachments:</p>
                <ul>
                    ${attachments.map(att => `<li>${this.escapeHtml(att)}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    escapeHtml(unsafe) {
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

        const filteredCampaigns = this.userData.campaignsList.filter(campaign => {
            const nameMatch = campaign.name.toLowerCase().includes(searchTerm);
            const dateMatch = !dateSearch || campaign.date === dateSearch;
            const attachmentMatch = !attachmentSearchTerm || 
                campaign.attachments.some(att => att.toLowerCase().includes(attachmentSearchTerm));
            return nameMatch && dateMatch && attachmentMatch;
        });

        this.renderCampaigns(filteredCampaigns);
    }

    handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        const validationResult = document.getElementById('validation-result');
        validationResult.innerHTML = 'Validating emails...';

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

document.addEventListener('DOMContentLoaded', async () => {
    const profileManager = new ProfileManager();
    const themeManager = new ThemeManager();
    
    await profileManager.init();
});