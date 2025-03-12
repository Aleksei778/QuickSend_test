import { getJWTToken } from "/static/scripts/getJwt.js";

async function disableStartTrialBtns() {
    const token = await getJWTToken();
    if (!token) {
        throw new Error('No token available');
    }

    const usedTrialResponse = await fetch('/api/v1/has_already_use_trial', {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const usedTrial = await usedTrialResponse.json();
    console.log("HAS USED TRIAL: ", usedTrial.message);

    if (usedTrial.message === "Yes") {
        const startTrialBtns = document.querySelectorAll(".start_trial_btn");
        for (const btn of startTrialBtns) {
            btn.style.display = "none";
        }
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    await disableStartTrialBtns();
});