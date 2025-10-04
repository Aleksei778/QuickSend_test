async function createModalWindow(text) {
    console.log("createModalWindow");

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

function getTimeZone() {
  return new Promise((resolve, reject) => {
      chrome.storage.local.get(['timeZone'], (result) => {
          if (chrome.runtime.lastError) {
              reject(chrome.runtime.lastError);
          } else {
              resolve(result.timeZone);
          }
      });
  });
}

async function getFiles(composeWindow) {
    const hrefs = [];
    const att_nodes = composeWindow.getElementsByClassName("dL");
    for (const node of att_nodes) {
      const attachmentInput = node.querySelector('input[name="attach"]');
      if (attachmentInput) {
        const lnk = node.querySelector('a');
        if (lnk && lnk.querySelectorAll('div').length == 2) {
          const divs = lnk.querySelectorAll('div');
          const filename = divs[0].innerText;
          const filesize = divs[1].innerText;
  
          hrefs.push({url: lnk.href, filename: filename, filesize: filesize});
        }
      }
    }
  
    return hrefs;
  }
  
  async function fetchAttachment(gmailUrl) {
    try {
        const response = await fetch(gmailUrl, {
            credentials: 'include'
        });
  
        if (!response.ok) {
            throw new Error('failed to fetch attachment');
        }
  
        const blob = await response.blob();
        return blob;
    } catch (error) {
        console.error('Error fetching attachment:', error);
        throw error;
    }
  }
  
  
  
  async function sendToServer(emailData) {
    try {
        const formData = new FormData();
        const hrefs = await getFiles();
        
        for (const href of hrefs) {
          const blob = await fetchAttachment(href.url);
          formData.append('files', blob, href.filename);
        }
  
        formData.append('body', JSON.stringify(emailData));
  
        const response = await fetch('http://127.0.0.1:8000/api/v1/process_attachment', {
            method: 'POST',
            body: formData
        });
  
        if (!response.ok) {
            throw new Error('Failed to upload to server');
        }
  
        return await response.json();
  
    } catch(error) {
        console.error('Error sending attachment to server:', error);
        throw error;
    }
  }

  async function getEmailData(composeWindow) {
    const emailData = {
        recipients: [],
        subject: '',
        body: '',
        date: '',
        time: '',
        timezone: ''
    };

    try {
        // Check if this is a full-screen compose window
        const isFullScreen = composeWindow.closest('.aSD') !== null;
        
        // Get recipients - handle both normal and full-screen modes
        let recipientNodes;
        if (isFullScreen) {
            // Full-screen mode uses a different class for recipient containers
            recipientNodes = composeWindow.querySelectorAll('.aH9 .afV');
        } else {
            recipientNodes = composeWindow.querySelectorAll('.afV');
        }
        
        emailData.recipients = Array.from(recipientNodes).map(node => node.getAttribute('data-hovercard-id'));
        
        // Process recipients including quicksend groups
        for (const [index, rep] of emailData.recipients.entries()) {
            if (typeof rep === 'string' && rep.includes('recipients') && rep.includes('quicksend')) {
                const uniqueId = rep.split('id_')[1].split('@')[0];
                const data = await chrome.storage.local.get([uniqueId]);
                const emails = data[uniqueId].realEmails;
                
                emailData.recipients.splice(index, 1);
                emailData.recipients.push(...emails);
            }
        }

        // Get subject - handle both modes
        let subjectField;
        if (isFullScreen) {
            subjectField = composeWindow.querySelector('.aXjCH input[name="subjectbox"]');
        } else {
            subjectField = composeWindow.querySelector('input[name="subjectbox"]');
        }
        emailData.subject = subjectField ? subjectField.value : '';

        // Get message body - handle both modes
        let messageBody;
        if (isFullScreen) {
            messageBody = composeWindow.querySelector('.Am.Al.editable');
        } else {
            messageBody = composeWindow.querySelector('div[role="textbox"][contenteditable="true"]');
        }
        emailData.body = messageBody ? messageBody.innerHTML : '';

        // Get campaign date and time
        const date = composeWindow.querySelector('#campaign-date');
        const time = composeWindow.querySelector('#campaign-time');
        const now = new Date();

        if (date && time) {
            const inputDateTime = new Date(`${date.value}T${time.value}`);
            
            const timeZone = await getTimeZone();
            if (timeZone) {
                emailData.timezone = timeZone;
            }

            if (inputDateTime < now) {
                emailData.date = '';
                emailData.time = '';
            } else {
                emailData.date = date.value;
                emailData.time = time.value;
            }
        }

        return emailData;
    } catch (error) {
        console.error('Error parsing email data:', error);
        throw new Error('Failed to parse email data');
    }
}

function createDropdownWindow() {
    const dropdownWindow = document.createElement('div');
    dropdownWindow.className = 'dropdown-window';

    // Create header
    const header = document.createElement('h3');
    header.textContent = 'Campaign Parameters';
    header.id = 'paramsHeader';
    dropdownWindow.appendChild(header);

    const datePicker = document.createElement("input");
    datePicker.type = "date";
    datePicker.id = "campaign-date";
    datePicker.name = "campaign-date";
    datePicker.lang = "en";

    const labelForDatePicker = document.createElement("label");
    labelForDatePicker.textContent = "Campaign Date: ";
    labelForDatePicker.htmlFor = "campaign-date";

    const timePicker = document.createElement("input");
    timePicker.type = "time";
    timePicker.id = "campaign-time";
    timePicker.name = "campaign-time";
    timePicker.lang = "en";

    const labelForTimePicker = document.createElement("label");
    labelForTimePicker.textContent = "Campaign Time: ";
    labelForTimePicker.htmlFor = "campaign-time";

    const p = document.createElement("p");
    p.textContent = "** Both date and time must be specified for the campaign to be scheduled";
    p.id = "warning-message";

    dropdownWindow.appendChild(labelForDatePicker);
    dropdownWindow.appendChild(datePicker);
    dropdownWindow.appendChild(document.createElement('br'));
    dropdownWindow.appendChild(labelForTimePicker);
    dropdownWindow.appendChild(timePicker);
    dropdownWindow.appendChild(p);

    dropdownWindow.style.display = 'none';
    return dropdownWindow;
}

function addCustomButton(composeWindow) {
    // Check if buttons already exist in this compose window
    if (composeWindow.querySelector('.custom-send-button')) return;
    
    const sendButton = composeWindow.querySelector('.T-I.J-J5-Ji.aoO.v7.T-I-atl.L3');
    if (!sendButton) return;

    // Create QuickSend button
    const customButton = document.createElement('button');
    customButton.innerText = "QuickSend";
    customButton.className = 'custom-send-button';
    customButton.style.marginLeft = "10px";
    customButton.style.position = 'relative';
    customButton.title = 'Click to this QuickSend button instead of Send to send individual emails';

    // Create dropdown button
    const customButtonL = document.createElement('button');
    customButtonL.innerText = "▼";
    customButtonL.className = 'custom-sendL-button';
    customButtonL.style.marginLeft = "0px";
    customButtonL.style.position = 'relative';
    customButtonL.title = 'QuickSend settings';

    // Create dropdown window for this compose window
    const dropdownWindow = createDropdownWindow();
    sendButton.parentNode.appendChild(dropdownWindow);

    // Add click handler for QuickSend button
    customButton.addEventListener('click', async () => {
        customButton.disabled = true;
        setTimeout(() => {
            customButton.disabled = false;
        }, 10000);

        const emailData = await getEmailData(composeWindow);
        console.log(emailData);
        startCampaign(emailData, composeWindow);
    });

    // Add click handler for dropdown button
    customButtonL.addEventListener('click', () => {
        const isHidden = dropdownWindow.style.display === 'none';
        dropdownWindow.style.display = isHidden ? 'block' : 'none';
        customButtonL.innerText = isHidden ? "▲" : "▼";
    });

    // Add buttons to the compose window
    sendButton.parentNode.parentNode.appendChild(customButton);
    sendButton.parentNode.parentNode.appendChild(customButtonL);
}

// Function to check for new compose windows
function checkForComposeWindows() {
  // Ищем все окна написания письма, включая полноразмерные
  const composeWindows = document.querySelectorAll('div.AD, div.aSt');

  composeWindows.forEach(composeWindow => {
      addCustomButton(composeWindow);
  });
}

async function startCampaign(data, composeWindow) {
    try {
      console.log("Получение токена при отправке");

      const result_token = await chrome.storage.local.get(['accessToken']);
      const token = result_token.accessToken;

      const formData = new FormData();
      const hrefs = await getFiles(composeWindow);
        
      for (const href of hrefs) {
        const blob = await fetchAttachment(href.url);
        formData.append('files', blob, href.filename);
      }
  
      formData.append('body', JSON.stringify(data));

      const response = await fetch('http://127.0.0.1:8000/api/v1/start-campaign1', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      if (formData.time && formData.date) {
        await createModalWindow(`Кампания была запланирована на ${formData.date} ${formData.time}`);
      } else {
        await createModalWindow("Кампания была начата");
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Failed to start campaign:', error);
      throw error;
    }
  }   

// Start checking for compose windows after page load
window.addEventListener('load', () => {
    // Периодически проверяем наличие окна для нового письма
    setInterval(checkForComposeWindows, 1000);

    const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    console.log("THERE IS TIMEZONE", timeZone);

    // Сохраняем таймзону в хранилище
    chrome.storage.local.set({ timeZone }, () => {
      console.log(`Таймзона сохранена: ${timeZone}`);
    });
});