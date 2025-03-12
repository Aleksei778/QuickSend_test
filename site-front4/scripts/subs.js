import { getJWTToken } from "/static/scripts/getJwt.js";
import { createModalWindow } from "/static/scripts/createModalWindow.js";

async function startTrial() {
    const token = await getJWTToken();
    if (!token) {
        throw new Error('No token available');
    }

    const startTrialBtns = document.querySelectorAll(".start_trial_btn");
    for (const btn of startTrialBtns) {
        btn.addEventListener('click', async () => {
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
            createModalWindow("7-day trial subscription activated");
        });   
    }
}

async function startStandartPlan() {
    const startStandartBtns = document.querySelectorAll(".payment-method");

    const token = await getJWTToken();
    startStandartBtns.addEventListener('click', async () => {
        const response = await fetch('/api/v1/subscribe/standart/month', {
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

async function startPremiumPlan() {
    const startStandartBtns = document.querySelectorAll(".payment-method");
}

async function handleStandartBtn() {
    standartBtn = document.getElementById("start_standart_btn");
    standartBtn.addEventListener('click', async () => {
        await startStandartPlan();
    });
}

async function handlePremiumBtn() {
    premiumBtn = document.getElementById("start_premium_btn");
    premiumBtn.addEventListener('click', async () => {
        await startPremiumPlan();
    });
}

document.addEventListener('DOMContentLoaded', async function() {
    await startTrial();
    await handleStandartBtn();
    await handlePremiumBtn();
});