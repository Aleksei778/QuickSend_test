import { getJWTToken } from "/static/scripts/checkAuth.js";

async function startTrial() {
    const startTrialBtn = document.getElementById("start_trial_btn");

    const token = await getJWTToken();
    startTrialBtn.addEventListener('click', async () => {
        const response = await fetch('/api/v1/start_trial', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('start trial response:', data);
    });
}

async function startBasicPlan() {
    const startBasicBtn = document.getElementById("start_basic_btn");

    const token = await getJWTToken();
    startBasicBtn.addEventListener('click', async () => {
        const response = await fetch('/api/v1/subscribe/basic/month', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('start basic response:', data);
    });
}

document.addEventListener('DOMContentLoaded', async function() {
    await startTrial();
    await startBasicPlan();
});