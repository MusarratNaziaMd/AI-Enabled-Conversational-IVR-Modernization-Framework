
**AI-Enabled Conversational IVR Modernization Framework** using **FastAPI** and **Twilio**.  
This project demonstrates a simple mobile service provider (MSP) IVR system that allows users to:

- Check data balance
- Recharge their plan
- Report issues via DTMF input or voice recording

The IVR is powered by Twilio for telephony integration and FastAPI as the backend server.

---

 **Features**

1. **Interactive Voice Response (IVR)**  
   Users can navigate menus using keypad input (DTMF).

2. **Recharge Functionality**  
   Users can input recharge amounts and receive confirmation messages.

3. **Issue Reporting**  
   Users can record their issues via voice, which are stored in the mock database.

4. **FastAPI Backend**  
   Handles call sessions, routing, and customer management.

---

 **Project Structure**

 AI-Enabled-Conversational-IVR-Modernization-Framework
AI-powered IVR system that modernizes customer support using FastAPI, Twilio, and conversational intelligence.


## Setup
1. Install Python 3.11 or above.
2. Clone the repository:
   git clone https://github.com/your-username/AI-Enabled-Conversational-IVR.git
3. Install dependencies:
   pip install -r requirements.txt
4. Run the FastAPI server:
   uvicorn msp_ivr_twilio:app --reload
5. Expose via ngrok for Twilio integration:
   ngrok http 8000
