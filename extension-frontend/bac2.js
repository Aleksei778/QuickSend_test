try {
  console.log("Background script loaded");

  async function getJWTToken() {
    const response = await fetch('https://f069-78-30-229-174.ngrok-free.app/api/v1/refresh', { // http://127.0.0.1:8000/api/v1/refresh
      method: 'POST'
    });
    const data = await response.json();
    console.log(data);
    return data.access_token;
  }

  async function refreshToken() {
    try {
        const token = await getJWTToken();
        console.log(token);      
        const data = await response.json();
        if (data.access_token) {
            chrome.storage.local.set({ accessToken: data.access_token }, function() {
                console.log('Access token updated');
            });


            setTimeout(5000);
            
            const result_token = await chrome.storage.local.get(['accessToken']);
            const token = result_token.accessToken;

            console.log("Token after refresh: ", token);
        } else {
            console.error('Failed to refresh token');
        }
    } catch (error) {
        console.error('Error refreshing token:', error);
    }
  }
  console.log("Background script loaded #2");
  // Устанавливаем периодическое обновление токена
  chrome.alarms.create('refreshToken', { periodInMinutes: 10 });
  console.log("Background script loaded #3");
  // Обработчик для выполнения задачи по расписанию
  chrome.alarms.onAlarm.addListener((alarm) => {
    if (alarm.name === 'refreshToken') {
        console.log("REFRESH_TOKENNN");
        refreshToken();
    }
  });
  console.log("Background script loaded #4");
} catch (error) {
  console.log(error);
}

