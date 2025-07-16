# 🔋 The Scribe's Desk — Subject-Specific AI Chatbot

Welcome to **The Scribe's Desk**, an elegant web-based AI chatbot designed to help students explore core Computer Science subjects interactively. This project leverages **OpenRouter's API** to generate context-specific, syllabus-constrained responses tailored to selected subjects.

---

## 🌟 Features

* 📚 **Subject-Aware AI Chat**: Choose from subjects like DBMS, DAA, ML, OS, AI, and DSA
* ✨ **Syllabus-Constrained Responses**: Each subject is strictly limited to its academic syllabus
* 🎨 **Elegant UI**: The parchment-style frontend brings a scholarly aesthetic
* ⚙️ **Custom Prompts for Each Subject**: Carefully crafted prompts to guide AI's behavior
* 🧠 **Powered by OpenRouter + Flask API**
* 🎯 **Frontend built with Tailwind CSS, JS, and HTML**

---

## 📂 Project Structure

```
├── app.py               # Flask backend that communicates with OpenRouter API
├── index.html           # Main HTML frontend interface
├── style.css            # Tailwind CSS-based custom styles
├── script.js            # Client-side JavaScript logic and DOM interaction
└── .env                 # Environment variables (API keys, settings) [Not included]
```

---

## 🚀 How to Run Locally

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/the-scribes-desk.git
cd the-scribes-desk
```

### 2. Install Requirements

Make sure you have Python 3.8+ installed.

```bash
pip install flask python-dotenv openai flask-cors
```

### 3. Setup `.env` File

Create a `.env` file in the root directory:

```ini
OPENROUTER_API_KEY=your_openrouter_api_key
YOUR_SITE_URL=http://127.0.0.1:5000
YOUR_SITE_NAME=The Scribe's Desk
OPENROUTER_TEMPERATURE=0.4
OPENROUTER_MAX_TOKENS=72000
```

### 4. Start the Flask Backend

```bash
python app.py
```

It will run on `http://127.0.0.1:5000`.

### 5. Open the Frontend

Simply open `index.html` in your browser.

> 📌 **Note**: For full functionality, serve it using a local web server (like Live Server or Python's `http.server` module) to avoid CORS issues.

---

## 📘 Subjects Supported

* MACHINE LEARNING - 1
* DBMS
* DESIGN AND ANALYSIS OF ALGORITHMS
* DATA STRUCTURES AND ALGORITHMS
* ARTIFICIAL INTELLIGENCE - 1
* OPERATING SYSTEMS

Each subject is mapped to a specific prompt design inside `app.py`, ensuring focused and relevant answers.


## 🛡️ License

This project is open-source under the [MIT License](LICENSE).

---

## 🤝 Contributions

Pull requests and suggestions are welcome! For major changes, please open an issue first.

---

## 📫 Contact

Developed by **Prabhas Gamini**
Connect on [LinkedIn](https://linkedin.com/in/prabhas-gamini-85a93a2b7/) | [GitHub](https://github.com/prabhasgamini)

---
