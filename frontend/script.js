// script.js

document.addEventListener('DOMContentLoaded', () => {
    console.log('script.js loaded and DOMContentLoaded event fired.');

    // Element references
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const subjectCards = document.querySelectorAll('.subject-card');
    const subjectSelectionScreen = document.getElementById('subject-selection');
    const chatbotContainer = document.getElementById('chatbot-container');
    const chatSubjectTitle = document.getElementById('chat-subject-title');
    const backButton = document.getElementById('back-button');

    let currentSubject = '';

    // Relative endpoint works directly when Flask serves the frontend
    const BACKEND_URL = '/chat';

    // Subject Card Selection
    subjectCards.forEach(card => {
        card.addEventListener('click', () => {
            currentSubject = card.getAttribute('data-subject');
            chatSubjectTitle.textContent = currentSubject;
            subjectSelectionScreen.classList.add('hidden');
            chatbotContainer.classList.remove('hidden');
            chatMessages.innerHTML = '';
            addMessage('The Scribe', `Hello! How may I assist you with ${currentSubject} today?`, false);
        });
    });

    // Back Button Handling
    backButton.addEventListener('click', () => {
        chatbotContainer.classList.add('hidden');
        subjectSelectionScreen.classList.remove('hidden');
        chatMessages.innerHTML = '';
        currentSubject = '';
    });

    // Message Renderer
    function addMessage(sender, text, isUser) {
        const messageContainer = document.createElement('div');
        messageContainer.className = `message ${isUser ? 'user-message' : 'bot-message'} self-${isUser ? 'end' : 'start'} mb-4`;

        let processedText = text;

        // Bolding processing
        processedText = processedText.replace(/\*(.*?)\*/g, '<strong>$1</strong>');

        // Line-by-line parsing for bullet lists and paragraphs
        const lines = processedText.split('\n');
        let htmlContent = '';
        let inList = false;

        lines.forEach(line => {
            const trimmed = line.trim();
            if (trimmed.startsWith('- ')) {
                if (!inList) {
                    htmlContent += '<ul class="list-disc pl-5 my-2">';
                    inList = true;
                }
                htmlContent += `<li>${trimmed.substring(2)}</li>`;
            } else {
                if (inList) {
                    htmlContent += '</ul>';
                    inList = false;
                }
                if (trimmed !== '') {
                    htmlContent += `<p class="mb-2">${trimmed}</p>`;
                }
            }
        });

        if (inList) {
            htmlContent += '</ul>';
        }

        messageContainer.innerHTML = `<span class="sender font-bold">${sender}:</span><div class="bot-text-content mt-1">${htmlContent}</div>`;
        chatMessages.appendChild(messageContainer);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // API Dispatch
    async function sendMessage() {
        const messageText = userInput.value.trim();
        if (!messageText) return;

        addMessage('You', messageText, true);
        userInput.value = '';

        sendButton.disabled = true;
        userInput.disabled = true;

        // Thinking Indicator
        const thinkingContainer = document.createElement('div');
        thinkingContainer.id = 'thinking-indicator';
        thinkingContainer.className = 'message bot-message self-start mb-4';
        thinkingContainer.innerHTML = '<span class="sender font-bold">The Scribe:</span><p class="text-gray-600 italic mt-1">Thinking...</p>';
        chatMessages.appendChild(thinkingContainer);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const response = await fetch(BACKEND_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: messageText, subject: currentSubject }),
            });

            const data = await response.json();

            // Remove Thinking Indicator
            const indicator = document.getElementById('thinking-indicator');
            if (indicator) indicator.remove();

            if (!response.ok) {
                throw new Error(data.error || `Server responded with status ${response.status}`);
            }

            addMessage('The Scribe', data.botResponse, false);

        } catch (error) {
            const indicator = document.getElementById('thinking-indicator');
            if (indicator) indicator.remove();

            addMessage('The Scribe', `Connection error: ${error.message}`, false);
        } finally {
            sendButton.disabled = false;
            userInput.disabled = false;
            userInput.focus();
        }
    }

    // Event Listeners
    if (sendButton) sendButton.addEventListener('click', sendMessage);
    if (userInput) {
        userInput.addEventListener('keypress', (event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }
        });
    }
});
