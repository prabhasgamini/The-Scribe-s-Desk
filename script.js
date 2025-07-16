// script.js

// Ensure the DOM is fully loaded before running the script
document.addEventListener('DOMContentLoaded', () => {
    // --- Initial Console Log to confirm script is loading and running ---
    console.log('script.js loaded and DOMContentLoaded event fired.');

    // --- Get references to all necessary HTML elements ---
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const subjectCards = document.querySelectorAll('.subject-card'); // Selects ALL subject cards
    const subjectSelectionScreen = document.getElementById('subject-selection'); // The main subject selection div
    const chatbotContainer = document.getElementById('chatbot-container'); // The main chatbot div
    const chatSubjectTitle = document.getElementById('chat-subject-title'); // The title in the chat header
    const backButton = document.getElementById('back-button'); // The back button in the chat header

    let currentSubject = ''; // Variable to store the currently selected subject

    // --- Basic validation and logging for HTML elements ---
    if (!chatMessages) console.error('Error: Element with ID "chat-messages" not found in script.js.');
    if (!userInput) console.error('Error: Element with ID "user-input" not found in script.js.');
    if (!sendButton) console.error('Error: Element with ID "send-button" not found in script.js.');
    if (!subjectSelectionScreen) console.error('Error: Element with ID "subject-selection" not found in script.js.');
    if (!chatbotContainer) console.error('Error: Element with ID "chatbot-container" not found in script.js.');
    if (!chatSubjectTitle) console.error('Error: Element with ID "chat-subject-title" not found in script.js.');
    if (!backButton) console.error('Error: Element with ID "back-button" not found in script.js.');
    if (subjectCards.length === 0) console.error('Error: No elements with class "subject-card" found in script.js.');

    // --- Event listener for Subject Card clicks ---
    subjectCards.forEach(card => {
        card.addEventListener('click', () => {
            currentSubject = card.getAttribute('data-subject');
            chatSubjectTitle.textContent = currentSubject; // Update chat header title
            subjectSelectionScreen.classList.add('hidden'); // Hide subject selection
            chatbotContainer.classList.remove('hidden'); // Show chatbot
            chatMessages.innerHTML = ''; // Clear previous messages
            console.log(`Subject selected: ${currentSubject}`);
            // Optional: Send an initial greeting from the bot based on the subject
            addMessage('The Scribe', `Hello! How may I assist you with ${currentSubject} today?`, false);
        });
    });

    // --- Event listener for Back Button ---
    backButton.addEventListener('click', () => {
        chatbotContainer.classList.add('hidden'); // Hide chatbot
        subjectSelectionScreen.classList.remove('hidden'); // Show subject selection
        chatMessages.innerHTML = ''; // Clear messages when going back
        currentSubject = ''; // Reset current subject
        console.log('Returned to subject selection.');
    });

    // --- Function to add messages to the chat interface ---
    function addMessage(sender, text, isUser) {
        const messageContainer = document.createElement('div');
        messageContainer.className = `message ${isUser ? 'user-message' : 'bot-message'} self-${isUser ? 'end' : 'start'} mb-4`;
        
        // Process text for readability: headings, bullet points, and line breaks
        let processedText = text;

        // 1. Convert *Text* to <span class="ai-heading">Text</span> for main points/headings
        // This regex specifically targets a line that contains only *text* or starts with *text*.
        // It's a heuristic, fine-tune if needed based on AI output patterns.
        processedText = processedText.replace(/^\*(.*?)\*$/gm, '<span class="ai-heading">$1</span>');
        
        // Also handle bolding within paragraphs if AI uses single * for it (less common with our prompt)
        processedText = processedText.replace(/(^|[^a-zA-Z0-9])\*([^\*]+?)\*([^a-zA-Z0-9]|$)/g, '$1<strong>$2</strong>$3');


        // 2. Convert raw bullet points (- item) into proper HTML list items
        // This will create <ul> and <li> elements.
        let lines = processedText.split('\n');
        let htmlContent = '';
        let inList = false;

        lines.forEach(line => {
            if (line.trim().startsWith('- ')) {
                if (!inList) {
                    htmlContent += '<ul>';
                    inList = true;
                }
                // Replace - with &bull; for a standard bullet, or keep it if CSS handles disc.
                // For direct HTML, `&bull;` is a good choice if you don't want `<ul>`
                // But `<ul><li>` is better for semantic HTML and CSS control.
                htmlContent += `<li>${line.trim().substring(2).trim()}</li>`;
            } else {
                if (inList) {
                    htmlContent += '</ul>';
                    inList = false;
                }
                // Convert remaining newlines to <br> for paragraphs
                if (line.trim() !== '') { // Only add paragraph if line is not empty after trim
                    htmlContent += `<p>${line.trim()}</p>`;
                } else { // Preserve single blank lines for paragraph separation if needed
                    htmlContent += '<br>';
                }
            }
        });
        if (inList) { // Close list if still open at the end
            htmlContent += '</ul>';
        }

        messageContainer.innerHTML = `<span class="sender">${sender}:</span><div class="bot-text-content">${htmlContent}</div>`;
        document.getElementById('chat-messages').appendChild(messageContainer);
        
        // Scroll to the bottom of the chat
        const chatMessagesElement = document.getElementById('chat-messages');
        chatMessagesElement.scrollTop = chatMessagesElement.scrollHeight;
    }

    // --- Function to send message to backend ---
    async function sendMessage() {
        const messageText = userInput.value.trim();
        if (!messageText) return;

        addMessage('You', messageText, true); // Display user message immediately
        userInput.value = ''; // Clear input field

        // Disable input and button while waiting for response
        sendButton.disabled = true;
        userInput.disabled = true;

        // Add a "Thinking..." message
        const thinkingMessageContainer = document.createElement('div');
        thinkingMessageContainer.className = 'message bot-message self-start mb-4';
        thinkingMessageContainer.innerHTML = '<span class="sender">The Scribe:</span><p class="text-gray-700 font-merriweather text-base md:text-lg leading-relaxed mt-1">Thinking...</p>';
        document.getElementById('chat-messages').appendChild(thinkingMessageContainer);
        chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll to show thinking message

        try {
            console.log("Sending message to backend...");
            const response = await fetch('http://127.0.0.1:5000/chat', { // Ensure this URL is correct
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: messageText, subject: currentSubject }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`HTTP error! status: ${response.status}, message: ${errorData.error}`);
            }

            const data = await response.json();
            console.log("Received response from backend:", data);

            // Remove "Thinking..." message
            if (chatMessages.lastChild && chatMessages.lastChild.querySelector('p') && chatMessages.lastChild.querySelector('p').textContent === 'Thinking...') {
                chatMessages.removeChild(chatMessages.lastChild);
            }
            
            addMessage('The Scribe', data.botResponse, false); // Display bot's response

        } catch (error) {
            console.error('Error sending message to backend:', error);
            // Remove "Thinking..." message if an error occurred before response
            if (chatMessages.lastChild && chatMessages.lastChild.querySelector('p') && chatMessages.lastChild.querySelector('p').textContent === 'Thinking...') {
                chatMessages.removeChild(chatMessages.lastChild);
            }
            addMessage('The Scribe', `Apologies, I encountered an error. Please try again or check the backend server. Details: ${error.message}`, false);
        } finally {
            // Re-enable input and button regardless of success or failure
            sendButton.disabled = false;
            userInput.disabled = false;
            userInput.focus(); // Return focus to the input field
        }
    }

    // --- Attach event listeners for sending messages ---
    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    } else {
        console.error('sendButton element not found, cannot attach click listener.');
    }

    if (userInput) {
        userInput.addEventListener('keypress', (event) => {
            // Check for Enter key press (without Shift key to allow newlines with Shift+Enter)
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault(); // Prevent default Enter behavior (e.g., new line in textarea)
                sendMessage(); // Call the send message function
            }
        });
    } else {
        console.error('userInput element not found, cannot attach keypress listener.');
    }
});
// End of script.js