import { getJWTToken } from "/static/scripts/getJwt.js";

async function animateCounters() {
    console.log('animateCounters');
    const token = await getJWTToken();
    if (!token) {
        throw new Error('No token available');
    }

    const campaignsResponse = await fetch('/api/v1/campaigns-stat', {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const campaignData = await campaignsResponse.json();
    console.log("CAMPAIGN STAT: ", campaignData);
        
    const campaignsCnt = document.getElementById('campaignCount');
    const recipientsCnt = document.getElementById('emailCount');

    campaignsCnt.textContent = parseInt(campaignData['campaigns_count']);
    recipientsCnt.textContent = parseInt(campaignData['recipients_count']);
}

document.addEventListener('DOMContentLoaded', async function() {
    await animateCounters();
});