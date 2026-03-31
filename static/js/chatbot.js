document.addEventListener('DOMContentLoaded', () => {
    const socket = io.connect('http://localhost:5000');
    const chatToggle = document.getElementById('chatbotToggle');
    const chatWindow = document.getElementById('chatWindow');
    const closeChat = document.getElementById('closeChat');
    const chatMessages = document.getElementById('chatMessages');
    const chatInput = document.getElementById('chatInput');
    const sendMessage = document.getElementById('sendMessage');
    const getOrderId = () => window.currentOrderId || 'FT-8527';

    // Helper to inject error bubble
    const showErrorBubble = (msg) => {
        chatMessages.innerHTML += `
            <div class="bot-message message error" style="background-color: #fee2e2; color: #b91c1c; border-radius: 8px; padding: 8px; margin: 4px 0; font-size: 0.9em; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                ${msg}
            </div>
        `;
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };
    chatToggle.addEventListener('click', () => {
        chatWindow.style.display = chatWindow.style.display === 'none' ? 'flex' : 'none';
        if (chatWindow.style.display === 'flex') loadChatHistory();
    });

    closeChat.addEventListener('click', () => {
        chatWindow.style.display = 'none';
    });

    sendMessage.addEventListener('click', sendChatMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendChatMessage();
    });

    function showTypingIndicator() {
        if (!document.getElementById('typingIndicator')) {
            const typingHtml = `<div id="typingIndicator" class="bot-message message typing-indicator"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>`;
            chatMessages.innerHTML += typingHtml;
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    function removeTypingIndicator() {
        const el = document.getElementById('typingIndicator');
        if (el) el.remove();
    }

    window.sendQuickReply = function(text) {
        chatInput.value = text;
        sendChatMessage();
        const qrs = document.querySelectorAll('.hide-on-click');
        qrs.forEach(el => el.style.display = 'none');
    };

    function renderMessage(msg) {
        let html = `
            <div class="${msg.sender}-message message">
                ${msg.message}
                <div class="message-time">${new Date(msg.timestamp).toLocaleTimeString()}</div>
        `;
        
        if (msg.metadata) {
            const meta = msg.metadata;
            if (meta.type === 'location') {
                html += `
                    <div class="bot-widget location-widget">
                        <div class="tracking-progress">Tracking Progress: ${meta.progress}%</div>
                        <div class="progress-bar-container"><div class="progress-bar" style="width: ${meta.progress}%"></div></div>
                        <p class="eta-text">ETA: ${meta.eta} mins</p>
                    </div>
                `;
            } else if (meta.type === 'driver_card') {
                html += `
                    <div class="bot-widget driver-widget">
                        <div class="driver-info">
                            <strong>${meta.driver.name}</strong> 
                            <span class="rating">⭐ ${meta.driver.rating}</span>
                        </div>
                        <p class="vehicle-info">${meta.driver.vehicle} - ${meta.driver.licensePlate}</p>
                        <button class="action-btn call-driver-btn" onclick="alert('Calling ${meta.driver.phone}...')">📞 Call Driver</button>
                    </div>
                `;
            } else if (meta.type === 'offer_card') {
                html += `
                    <div class="bot-widget offer-widget">
                        <strong>${meta.offer.title}</strong>
                        <p>${meta.offer.description}</p>
                        <div class="offer-code">Code: <span>${meta.offer.code}</span></div>
                    </div>
                `;
            } else if (meta.type === 'quick_replies') {
                html += `
                    <div class="quick-replies hide-on-click">
                        <button class="quick-reply-btn" onclick="sendQuickReply('Track my order')">Track Order</button>
                        <button class="quick-reply-btn" onclick="sendQuickReply('Contact driver')">Call Driver</button>
                        <button class="quick-reply-btn" onclick="sendQuickReply('Show me offers')">Offers</button>
                        <button class="quick-reply-btn" onclick="sendQuickReply('How many eco-points?')">Points</button>
                    </div>
                `;
            }
        }
        html += `</div>`;
        return html;
    }

    function sendChatMessage() {
        const message = chatInput.value.trim();
        if (message) {
            console.log(`Sending message for ${getOrderId()}: ${message}`);
            // add user message locally to avoid waiting on socket ping trip and show typing
            const tempUserMsg = { sender: 'user', message: message, timestamp: new Date().toISOString() };
            chatMessages.innerHTML += renderMessage(tempUserMsg);
            chatInput.value = '';
            showTypingIndicator(); 
            chatMessages.scrollTop = chatMessages.scrollHeight;

            fetch(`/api/chat/${getOrderId()}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sender: 'user', message: message })
            })
            .then(response => {
                if (!response.ok) throw new Error(`Server returned ${response.status}`);
                return response.json();
            })
            .then(data => {
                if (!data.success) {
                    removeTypingIndicator();
                    console.error('Server error:', data.error);
                    showErrorBubble(`Failed to send message: ${data.error || 'Unknown error'}`);
                }
            })
            .catch(error => {
                removeTypingIndicator();
                console.error('Fetch error:', error);
                showErrorBubble(`Error sending message: ${error.message}. Check server status.`);
            });
        }
    }

    function loadChatHistory() {
        fetch(`/api/chat/${getOrderId()}`)
            .then(response => {
                if (!response.ok) throw new Error(`Server returned ${response.status}`);
                return response.json();
            })
            .then(data => {
                chatMessages.innerHTML = data.messages.map(msg => renderMessage(msg)).join('');
                chatMessages.scrollTop = chatMessages.scrollHeight;
            })
            .catch(error => {
                console.error('History fetch error:', error);
                chatMessages.innerHTML = '<div class="bot-message message">Error loading chat history. Check server status.</div>';
                chatMessages.scrollTop = chatMessages.scrollHeight;
            });
    }

    socket.onAny((eventName, msg) => {
        if (eventName === `chat_message_${getOrderId()}`) {
            console.log(`Received message for ${getOrderId()}:`, msg);
            // Remove typing indicator if it's there
            removeTypingIndicator();
            // Since we already rendered user message in sendChatMessage, ignore user echoes via socket
            if (msg.sender === 'bot') {
                chatMessages.innerHTML += renderMessage(msg);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        }
    });

    socket.on('connect', () => console.log('Socket.IO connected'));
    socket.on('disconnect', () => console.log('Socket.IO disconnected'));
    socket.on('connect_error', (error) => {
        console.error('Socket.IO connection error:', error);
        showErrorBubble('Socket.IO connection failed. Check server status.');
    });

    // Invoke loadChatHistory initially
    loadChatHistory();
});