async function removeToken() {
    await chrome.storage.local.remove('accessToken');
}

// Вместо DOMContentLoaded используем прямое выполнение
const logout_btn = document.getElementById("logout-button");
if (logout_btn) {
    logout_btn.addEventListener('click', async() => {
        await removeToken();
    });
    console.log("TOKEN WAS REMOVED");
} else {
    console.log("THERE IS NOO LOGOUT BTN");
}