



 AI-Enabled Conversational IVR Modernization Framework (Milestone 3)

 📘 Project Overview

This project is part of my **Infosys Springboard Internship**.
It aims to modernize traditional IVR (Interactive Voice Response) systems built on VoiceXML (VXML) by integrating **Conversational AI** and speech technologies.
The goal is to make IVRs more natural, intelligent, and user-friendly with minimal rework of existing assets.


🚀 Milestone Summary

| Milestone       | Description                                                                                                                               |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Milestone 1** | Study of legacy IVR workflows using VXML                                                                                                  |
| **Milestone 2** | Twilio-based AI IVR backend developed and tested                                                                                          |
| **Milestone 3** | **Web-based voice IVR** built with Python Speech-to-Text and Text-to-Speech, created **due to Twilio call limitations in the free trial** |

---

 🧠 Key Features

* Fully **voice-based** backend (no frontend required)
* **Speech-to-Text (STT)** using `speech_recognition`
* **Text-to-Speech (TTS)** using `pyttsx3`
* Smart **intent mapping** for:

  * Recharge, Check Balance, Offers, Data Packs, Upgrade to Premium
  * Customer Care: Network Issue, SIM Issue, Recharge Issue, Data Pack Issue
* Interactive dialogue until user says “exit” or “thank you”
* Dynamic recharge options and plan details

---

## ⚙️ Tech Stack

| Component          | Technology                      |
| ------------------ | ------------------------------- |
| Language           | Python 3.10 +                   |
| Framework          | FastAPI                         |
| Speech Recognition | `speech_recognition`, `pyaudio` |
| Text-to-Speech     | `pyttsx3`                       |
| Database           | SQLite                          |
| AI/NLU             | Rule-based Intent Mapping       |

---

## 🧩 Installation

```bash
pip install fastapi uvicorn pyttsx3 SpeechRecognition pyaudio
python nazia_ivr_backend.py
```

---

## 💬 Example Conversation

**System:** “Welcome to SmartTel Modern IVR! Please say or enter your Customer ID.”
**User:** “1001”
**System:** “Hi Aiza! Would you like the main menu or talk to customer care?”
**User:** “Recharge.”
**System:** “Please choose a pack – ₹99, ₹249, ₹399 or custom amount.”
**User:** “₹249.”
**System:** “Recharge successful! Would you like to continue or exit?”

---

## 🧱 Architecture Flow

```
User Voice → Speech-to-Text → Intent Mapping → Backend Logic → Text-to-Speech → Voice Output
```

---

## 🧾 Note

> During Milestone 2, Twilio IVR was implemented successfully,
> but due to **Twilio free-trial call restrictions**,
> this **web-based voice IVR** version was developed for Milestone 3 using Python’s local speech modules.

