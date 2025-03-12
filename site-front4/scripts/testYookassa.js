import { getJWTToken } from "/static/scripts/getJwt.js";

export async function testYookassa() {
    console.log("TESSST YOOKASSAA");

    const token = await getJWTToken();
    const testYookassaBtn = document.getElementById("yookassa_btn");

    const plan = "standart";
    const period = "month";
    const email = "aleksejparhomenko14192@gmail.com";

    const subData = {
        plan_type: plan,
        period: period,
        user_email: email
    }

    testYookassaBtn.addEventListener('click', async () => {
        const response = await fetch('/api/v1/yookassa/subscriptions/create', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(subData)
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log(data);
        console.log(data.confirmation_url);
        window.location.href = data.confirmation_url;
    });
}