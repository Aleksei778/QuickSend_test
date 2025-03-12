export async function createModalWindow(text) {
    const mainDiv = document.createElement("div");
    mainDiv.className = "gmass-butterbar";

    const span = document.createElement("span");
    span.className = "gmass-butterbar-text";
    span.textContent = text;

    const closeButton = document.createElement('div');
    closeButton.className = 'gmass-butterbar-close';
    closeButton.setAttribute('role', 'button');
    closeButton.setAttribute('tabindex', '0');

    const innerDiv = document.createElement('div');
    
    closeButton.appendChild(innerDiv);
    mainDiv.appendChild(span);
    mainDiv.appendChild(closeButton);
    document.body.appendChild(mainDiv);

    const removeModal = () => {
        const modalWindow = document.querySelector(".gmass-butterbar");
        if (modalWindow) {
            modalWindow.remove(); // или modalWindow.style.display = 'none';
        }
    };
    
    // Обработчик клика на кнопку закрытия
    closeButton.addEventListener('click', () => {
        removeModal();
    });
    
    // Автоматическое закрытие через 5 секунд
    setTimeout(removeModal, 5000);
}