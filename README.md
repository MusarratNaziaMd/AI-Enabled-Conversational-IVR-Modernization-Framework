
# AI-Enabled Conversational IVR Modernization Framework

**Infosys Springboard Internship Project**

**Live Demo:** SmartTel Voice IVR - https://smarttel-ivr.onrender.com  

---

## 📘 Project Overview

This project modernizes traditional IVR (Interactive Voice Response) systems, typically built on legacy VoiceXML (VXML), by integrating **Conversational AI, Speech Recognition, and Text-to-Speech technologies**. The aim is to make IVRs **intelligent, interactive, and user-friendly**, reducing reliance on rigid call-tree structures, while providing a natural voice-based interface for customers.

---

## 🚀 Milestone Summary

| Milestone | Description |
|-----------|------------|
| **Milestone 1** | Study and documentation of legacy IVR workflows using VXML. |
| **Milestone 2** | Twilio-based AI IVR backend developed and tested for core functionalities such as balance inquiry, recharge, and customer care. |
| **Milestone 3** | Web-based voice IVR using Python Speech-to-Text and Text-to-Speech, created due to Twilio call limitations in the free trial. |
| **Milestone 4** | Final integration, full-cycle testing, frontend deployment, and production rollout via **Render**. Includes a complete web-based voice IVR interface. |

---

## 🧠 Key Features 
- **Web-Based Interactive Voice IVR**
  - Users interact through voice commands directly on the web page.
  - Real-time Speech-to-Text (STT) and Text-to-Speech (TTS) responses.  
- **Full Voice-First Flow**
  - System welcomes users and requests Customer ID.
  - Automatically handles registration if the Customer ID is not found.
  - Interactive dialogue continues until the user says **“exit”** or **“thank you”**.
- **Smart Intent Handling**
  - **Account Actions:** Check balance, view plan, see offers, recharge, upgrade data plan.  
  - **Customer Care:** Network issues, SIM issues, recharge or payment issues, general support.
- **Dynamic Backend Logic**
  - SQLite database stores customer info, balances, and plan details.
  - Safe session handling, retry mechanisms, and voice prompt confirmations.
- **Frontend Features**
  - Responsive HTML/CSS interface with modern styling and menu visualization.
  - Voice prompts for menus and user input feedback.
  - Visual logs of user-bot conversation with scrollable chat area.

---

## ⚙️ Technical Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| Framework | Flask |
| Frontend | HTML, CSS, JavaScript (responsive design, voice interaction) |
| Speech Recognition | `speech_recognition` |
| Text-to-Speech | `pyttsx3` |
| Database | SQLite |
| Rate Limiting | `Flask-Limiter` (to prevent abuse) |
| Deployment | Render (production-ready backend URL) |
| AI / NLU | Rule-based intent mapping for predefined customer actions |

---

## 🧩 Installation & Running Locally

1. Clone the repo:

```bash
git clone https://github.com/MusarratNaziaMd/AI-Enabled-Conversational-IVR-Modernization-Framework/
cd AI-Enabled-Conversational-IVR-Modernization-Framework
````

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the backend locally:

```bash
python milestone4_backend.py
```


---

## 💬 Example Conversation (Milestone 4)

```
System: “Welcome to SmartTel Voice IVR. Please say your Customer ID.”
User: “1001”
System: “Welcome back Aiza! Do you want the main menu or talk to customer care?”
User: “Main menu”
System: “Check balance, Plan details, Latest offers, Data upgrade, Recharge, Talk to customer care.”
User: “Recharge”
System: “Please choose a pack – ₹99, ₹249, ₹399, or custom amount.”
User: “₹249”
System: “Recharge successful! Would you like to continue or exit?”
```

---

## 🧱 Architecture Flow

```
User Voice → Browser STT → Frontend JS → Flask Backend API → Intent Mapping → Database Operations → TTS Response → Voice Output
```

* **Frontend** handles voice capture, menu rendering, and safe STT/TTS interaction.
* **Backend** handles database operations, intent processing, registration, and logging.
* **SQLite DB** stores persistent customer data for balance, plans, and usage.
* **Render Deployment** ensures the system is production-ready and accessible online.

---

## 🧪 Testing (Milestone 4)

* Full-cycle **unit tests** included in `milestone4_backend.py` using **pytest**.
* Tests cover:

  * Customer registration and retrieval
  * Intent processing for balance, recharge, plan upgrade, and customer care
  * End-to-end session simulation
  * Logging verification
* Rate-limiting and safety checks are applied to prevent abuse in production.

---

## 🌐 Deployment

* The project backend is deployed on **Render**:

**Production URL:** [https://smarttel-ivr.onrender.com](https://smarttel-ivr.onrender.com)

* The frontend connects to this backend URL for live voice interactions.
* Deployment ensures **automatic scaling, HTTPS, and persistent logs**.

---

## 📝 Notes

* Milestone 2 was limited by Twilio’s free trial, so Milestone 3 introduced a fully web-based voice IVR using **Python speech modules**.
* Milestone 4 integrates a **user-friendly web frontend**, **safe STT/TTS**, **robust backend with logging**, and **production deployment**.
* All customer interactions, including registration, recharge, and support queries, are fully voice-driven.

---

## 🔧 Future Enhancements

* AI-powered **NLU for more natural conversations** instead of rule-based intent mapping.
* Integration with **live backend services** for payments and plan management.
* Multi-language support for STT/TTS.
* Analytics dashboard for customer usage tracking and call flow optimization.


```
