import { getJWTToken } from "/static/scripts/getJwt.js";

async function checkAuth() {
    try {
        console.log("hi");
        // Сначала получаем JWT токен
        const token = await getJWTToken();
        
        if (!token) {
            throw new Error('No token available');
        }

        console.log(token);

        // Делаем запрос с токеном в заголовке
        const response = await fetch('/api/v1/check_user', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Auth response:', data);

        if (data.name && data.email) {
            console.log('nohh');

            // Обновляем UI для авторизованного пользователя
            document.querySelector('.signin-button').style.display = 'none';
            document.querySelector('.profile-button').style.display = 'flex';
            
            // Если есть информация о подписке
            if (data.subscription_status) {
                document.getElementById('subscription-status').textContent = 
                    data.subscription_status || 'Unknown';
            }
        } else {
            console.log('Oops');
            // Обновляем UI для неавторизованного пользователя
            document.querySelector('.signin-button').style.display = 'flex';
            document.querySelector('.profile-button').style.display = 'none';
        }
    } catch (error) {
        console.error('Error checking auth status:', error);
        // В случае ошибки показываем кнопку входа
        document.querySelector('.signin-button').style.display = 'flex';
        document.querySelector('.profile-button').style.display = 'none';
    }
}

document.addEventListener('DOMContentLoaded', async function() {
    await checkAuth();
});