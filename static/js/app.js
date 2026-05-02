let currentSessionId = null;

document.addEventListener('DOMContentLoaded', () => {
    // 1. Sahifa yuklanganda URL'da UUID bormi yoki yo'qligini tekshirish
    const pathParts = window.location.pathname.split('/');
    const uuidFromUrl = pathParts.find(part => part.length > 30); 
    
    if (uuidFromUrl) {
        loadSession(uuidFromUrl);
    }

    loadChatHistory();

    const sendBtn = document.getElementById('send-btn');
    const userInput = document.getElementById('user-input');

    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    const toggleSendButton = () => {
        const hasText = userInput.value.trim().length > 0;
        sendBtn.classList.toggle('inactive', !hasText);
        sendBtn.disabled = !hasText;
    };

    userInput.addEventListener('input', toggleSendButton);
    toggleSendButton();

    // Yangi chat tugmasi
    const newChatBtn = document.getElementById('new-chat-btn');
    if (newChatBtn) {
        newChatBtn.addEventListener('click', () => {
            currentSessionId = null;
            window.history.pushState({}, '', '/'); 
            document.getElementById('messages-list').innerHTML = '';
            // Yangi chatda welcome-screen qaytib chiqishi kerak
            document.getElementById('welcome-screen').style.display = 'flex';
            document.querySelectorAll('#chat-history-list .list-group-item').forEach(el => el.classList.remove('active'));
        });
    }
});

// Sidebar navigatsiyasi
async function loadChatHistory() {
    try {
        const response = await fetch('/api/chats/');
        const sessions = await response.json();
        const list = document.getElementById('chat-history-list');
        list.innerHTML = '';

        sessions.forEach(session => {
            const item = document.createElement('div');
            const isActive = currentSessionId === session.id ? 'active' : '';
            item.className = `list-group-item list-group-item-action text-truncate ${isActive}`;
            item.style.cursor = 'pointer';
            item.innerText = session.title || "Yangi chat";
            item.onclick = () => {
                window.history.pushState({}, '', `/chat/${session.id}/`);
                loadSession(session.id);
            };
            list.appendChild(item);
        });
    } catch (err) {
        console.error("Tarixni yuklashda xato:", err);
    }
}

// Tanlangan sessiyani (eski chatni) yuklash
async function loadSession(id) {
    currentSessionId = id;
    
    const response = await fetch(`/api/chats/${id}/`);
    const data = await response.json();
    
    const messagesList = document.getElementById('messages-list');
    const welcomeScreen = document.getElementById('welcome-screen');
    
    messagesList.innerHTML = '';
    
    // Agar xabarlar bo'lsa, welcome-screen'ni yashiramiz
    if (data.messages && data.messages.length > 0) {
        if (welcomeScreen) welcomeScreen.style.display = 'none';
        data.messages.forEach(msg => appendMessage(msg.sender_type, msg.text));
    }
    
    document.querySelectorAll('#chat-history-list .list-group-item').forEach(el => el.classList.remove('active'));
    loadChatHistory(); 
}

// Xabar yuborish mantiqi
async function sendMessage() {
    const input = document.getElementById('user-input');
    const text = input.value.trim();
    const welcomeScreen = document.getElementById('welcome-screen');
    
    if (!text) return;

    input.value = '';
    // Birinchi savol yuborilishi bilan welcome-screen yashiriladi
    if (welcomeScreen) welcomeScreen.style.display = 'none';
    
    appendMessage('user', text);

    try {
        if (!currentSessionId) {
            const sessionRes = await fetch('/api/chats/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF_TOKEN },
                body: JSON.stringify({ title: text.substring(0, 30) })
            });
            const newSession = await sessionRes.json();
            currentSessionId = newSession.id;
            window.history.pushState({}, '', `/chat/${currentSessionId}/`);
            loadChatHistory();
        }

        const response = await fetch(`/api/chats/${currentSessionId}/send_message/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF_TOKEN },
            body: JSON.stringify({ text: text })
        });
        const data = await response.json();
        appendMessage('bot', data.bot_message.text);
    } catch (err) {
        console.error(err);
        appendMessage('bot', "Xatolik: AI bilan aloqa uzildi.");
    }
}

function appendMessage(sender, text) {
    const list = document.getElementById('messages-list');
    const div = document.createElement('div');
    div.className = `message-row ${sender}-row mb-4 d-flex ${sender === 'user' ? 'justify-content-end' : 'justify-content-start'}`;
    
    const innerHtml = sender === 'user' 
        ? `<div class="text p-3 bg-secondary rounded-4 text-white" style="max-width: 80%;">${text}</div>`
        : `<div class="text p-3 text-light" style="max-width: 85%; line-height: 1.6;">${text}</div>`;
    
    div.innerHTML = innerHtml;
    list.appendChild(div);
    
    const container = document.getElementById('chat-container');
    container.scrollTop = container.scrollHeight;
}