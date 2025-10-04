async function getJWTToken() {
    const response = await fetch('http://127.0.0.1:8000/api/v1/get_jwt');
    const data = await response.json();
    console.log(data);
    return data.access_token;
}

window.onload = async () => {
    const token = await getJWTToken();
    console.log(token);

    chrome.storage.local.set({ accessToken: token }, function() {
        console.log('Access token saved');
    });
};