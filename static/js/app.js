let currentChatId = null;

// 1. Sahifa yuklanganda chatlar tarixini olish
document.addEventListener('DOMContentLoaded', () => {
    loadChatHistory();
});

// 2. Chatlar tarixini yuklash (Sidebar uchun)
async function loadChatHistory() {
    try {
        const response = await fetch('/api/chat/sessions/');
        const data = await response.json();
        const historyList = document.getElementById('chat-history-list');
        historyList.innerHTML = '';

        data.forEach(chat => {
            const item = document.createElement('a');
            item.className = 'list-group-item list-group-item-action';
            item.innerText = chat.title;
            item.onclick = () => loadChatMessages(chat.id);
            historyList.appendChild(item);
        });
    } catch (error) {
        console.error('Tarixni yuklashda xato:', error);
    }
}

// 3. Konkret bir chatni ochish
async function loadChatMessages(uuid) {
    currentChatId = uuid;
    document.getElementById('welcome-screen').classList.add('d-none');
    const messagesList = document.getElementById('messages-list');
    messagesList.innerHTML = '<p class="text-center">Yuklanmoqda...</p>';

    try {
        const response = await fetch(`/api/chat/sessions/${uuid}/`);
        const chat = await response.json();
        messagesList.innerHTML = '';

        chat.messages.forEach(msg => {
            appendMessage(msg.sender_type, msg.text);
        });
    } catch (error) {
        console.error('Xabarlarni yuklashda xato:', error);
    }
}

// 4. Xabar yuborish
async function sendMessage() {
    const input = document.getElementById('user-input');
    const text = input.value.trim();
    if (!text) return;

    // Agar chat hali ochilmagan bo'lsa, yangi sessiya yaratamiz
    if (!currentChatId) {
        await createNewChat(text);
        return;
    }

    input.value = '';
    appendMessage('user', text);

    try {
        const response = await fetch(`/api/chat/sessions/${currentChatId}/send_message/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken') // Django CSRF xavfsizligi uchun
            },
            body: JSON.stringify({ text: text })
        });
        const data = await response.json();
        
        appendMessage('bot', data.bot_message.text);
        
        // Agar title o'zgargan bo'lsa, sidebarni yangilaymiz
        loadChatHistory(); 
    } catch (error) {
        console.error('Xabar yuborishda xato:', error);
    }
}

// 5. Yangi chat sessiyasini yaratish
async function createNewChat(initialText) {
    try {
        const response = await fetch('/api/chat/sessions/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ title: 'Yangi suhbat' })
        });
        const newChat = await response.json();
        currentChatId = newChat.id;
        await sendMessage(); // Sessiya yaratilgach, xabarni yuboramiz
    } catch (error) {
        console.error('Yangi chat yaratishda xato:', error);
    }
}

// 6. Ekranga xabarni chiqarish (UI)
function appendMessage(sender, text) {
    const messagesList = document.getElementById('messages-list');
    const rowClass = sender === 'user' ? 'user-row' : 'bot-row';
    const icon = sender === 'user' ? 'fa-user' : 'fa-robot';
    const color = sender === 'user' ? 'text-info' : 'text-success';

    const msgHtml = `
        <div class="message-row ${rowClass}">
            <div class="message-content">
                <div class="avatar bg-dark d-flex align-items-center justify-content-center">
                    <i class="fas ${icon} ${color}"></i>
                </div>
                <div class="text">${text}</div>
            </div>
        </div>
    `;
    messagesList.insertAdjacentHTML('beforeend', msgHtml);
    document.getElementById('chat-container').scrollTop = document.getElementById('chat-container').scrollHeight;
}

// Django CSRF tokenni olish uchun yordamchi funksiya
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Tugmalarga event qo'shish
document.getElementById('send-btn').onclick = sendMessage;
document.getElementById('user-input').onkeypress = (e) => { if(e.key === 'Enter') sendMessage(); };
document.getElementById('new-chat-btn').onclick = () => {
    currentChatId = null;
    document.getElementById('messages-list').innerHTML = '';
    document.getElementById('welcome-screen').classList.remove('d-none');
};