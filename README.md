# 🤖 AutoTriage.AI - Next Gen Customer Support

**AutoTriage.AI** is a "World Class" AI-powered support system that autonomously triages customer tickets, analyzes sentiment, suggests technical solutions, and escalates critical issues to management via SMTP.

Powered by **Google Gemini 3 (4B)**.

![UI Screenshot](https://via.placeholder.com/800x400?text=AutoTriage+AI+Dashboard) 
*(Replace with actual screenshot)*

---

## ✨ Features

- **🧠 Advanced AI Brain**: Powered by `gemma-3-4b-it` for blazing fast, accurate responses.
- **💬 Modern Chat Interface**: A beautiful, glassmorphism-inspired HTML5 chat widget with markdown support.
- **⚡ Real-time Triage**: Instantly categorizes tickets by **Priority**, **Sentiment**, and **Department**.
- **🚨 Smart Escalation**: Automatically detects **Critical** issues (e.g., "System Down") and emails the Boss via SMTP.
- **🧹 Auto-Response**: Handles ticket submission logic gracefully ("Yes, sure").
- **📊 Mission Control Dashboard**: A Streamlit-based admin panel to view the "Ticket Inbox" and live analytics.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- A Google Cloud API Key (for Gemini)
- (Optional) Gmail App Password (for SMTP alerts)

### 2. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/Dhruv63/autotraige_Gemini
cd autotraige_Gemini
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_google_api_key_here

# Optional: For Critical Email Alerts
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password
BOSS_EMAIL=manager@company.com
```

### 4. Running the System

**Step A: Start the Backend (Brain)**
This powers the chat interface and AI logic.
```bash
python api.py
```
*Server runs on: `http://localhost:5000`*

**Step B: Start the Dashboard (Mission Control)**
This opens the admin interface.
```bash
streamlit run streamlit_app.py
```
*Dashboard opens at: `http://localhost:8501`*

**Step C: Use the App**
Open `index.html` in your browser to chat with the bot!

---

## 📂 Project Structure

- `index.html` - The customer-facing Chat UI.
- `api.py` - Flask Wrapper that connects the UI to the AI Brain.
- `streamlit_app.py` - Admin Dashboard for ticket management.
- `support_ai/` - Core AI Logic (Analyzer, Agents, Pipeline).
- `ticket_results/` - JSON storage for submitted tickets.
- `.env` - Security configuration (Not pushed to Git).

---

## 🛠️ Tech Stack
- **AI Model**: Google Gemma 3 (4B)
- **Backend**: Flask + Python
- **Frontend**: HTML5 + CSS3 + Vanilla JS
- **Dashboard**: Streamlit
- **Tools**: Google Generative AI SDK, Scikit-Learn (TF-IDF)

---

## 🤝 Contributing
Feel free to fork and submit a Pull Request!

---
*Built with ❤️ by Dhruv.*
