function checkExtension() {
    const userAgent = navigator.userAgent;
    return userAgent.includes('QuickSend');
  }

document.addEventListener('DOMContentLoaded', () => {
    let flag = checkExtension();
    console.log(flag);
});