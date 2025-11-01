# msp_ivr_twilio.py
from fastapi import FastAPI, Form
from fastapi.responses import Response
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

# -----------------------------
# Twilio Credentials
# -----------------------------
  

TWILIO_ACCOUNT_SID = ""
TWILIO_AUTH_TOKEN = ""
TWILIO_NUMBER = "+1"
VERIFIED_NUMBER = '+91'                # Your verified number

# msp_ivr_twilio.py

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# -----------------------------
# FastAPI app
# -----------------------------
app = FastAPI(title="MSP AI-IVR Twilio Demo")

# -----------------------------
# Mock customer database
# -----------------------------
customers = {
    "1001": {"name": "Alice", "plan": "Data 2GB/day", "balance": "500MB", "issues": []},
    "1002": {"name": "Bob", "plan": "Unlimited Calls", "balance": "1GB", "issues": ["Network drop"]},
}

# Session storage for call context
call_sessions = {}

# -----------------------------
# Make a test call from Twilio
# -----------------------------

@app.get("/")
def home():
      return {"status": "MSP IVR running"}


def make_call():
    ngrok_url = "https://ned-ecalcarate-blankly.ngrok-free.dev/twilio/start/" 
    try:
        call = client.calls.create(
            to=VERIFIED_NUMBER,
            from_=TWILIO_NUMBER,
            url=ngrok_url
        )
        return {"message": "Test call initiated", "call_sid": call.sid}
    except Exception as e:
        return {"message": "Call failed", "error": str(e)}


# -----------------------------
# Twilio IVR Start Endpoint
# -----------------------------
@app.post("/twilio/start")
def twilio_start(CallSid: str = Form(...), From: str = Form(...)):
    call_sessions[CallSid] = {"customer_id": "1001", "step": "main_menu"}  # demo customer
    resp = VoiceResponse()
    gather = resp.gather(num_digits=1, action="/twilio/handle_input", method="POST")
    gather.say("Welcome to SmartTel Customer Support!", voice="alice")
    gather.say("Press 1 to check balance. Press 2 to recharge. Press 3 to report an issue.", voice="alice")
    return Response(content=str(resp), media_type="application/xml")


# -----------------------------
# Handle DTMF Input
# -----------------------------
@app.post("/twilio/handle_input")
def twilio_handle_input(Digits: str = Form(...), CallSid: str = Form(...)):
    digits = Digits
    call_id = CallSid
    response = VoiceResponse()
    
    session = call_sessions.get(call_id)
    if not session:
        response.say("Session not found. Ending call.", voice="alice")
        response.hangup()
        return Response(content=str(response), media_type="application/xml")
    
    customer = customers[session["customer_id"]]
    
    if session["step"] == "main_menu":
        if digits == "1":
            session["step"] = "main_menu"
            response.say(f"Your remaining data balance is {customer['balance']}.", voice="alice")
            response.redirect("/twilio/start")
        elif digits == "2":
            session["step"] = "recharge_plan"
            gather = response.gather(num_digits=4, action="/twilio/handle_input", method="POST")
            gather.say(f"Your current plan is {customer['plan']}. Enter recharge amount.", voice="alice")
        elif digits == "3":
            session["step"] = "report_issue"
            response.say("Please describe your issue after the beep.", voice="alice")
            response.record(max_length=30, action="/twilio/recording")
        else:
            response.say("Invalid input. Returning to main menu.", voice="alice")
            response.redirect("/twilio/start")
    elif session["step"] == "recharge_plan":
        session["step"] = "main_menu"
        response.say(f"Recharge of {digits} successful for {customer['name']}.", voice="alice")
        response.redirect("/twilio/start")
    
    return Response(content=str(response), media_type="application/xml")


# -----------------------------
# Handle Recorded Issues
# -----------------------------
@app.post("/twilio/recording")
def twilio_recording(RecordingUrl: str = Form(...), CallSid: str = Form(...)):
    session = call_sessions.get(CallSid)
    if session:
        customer = customers[session["customer_id"]]
        customer["issues"].append(f"Voice message: {RecordingUrl}")
        session["step"] = "main_menu"
    
    resp = VoiceResponse()
    resp.say("Your issue has been recorded. Our support team will contact you.", voice="alice")
    resp.redirect("/twilio/start")
    return Response(content=str(resp), media_type="application/xml")


# -----------------------------
# Optional: Check customer info
# -----------------------------
@app.get("/ivr/status/{customer_id}")
def customer_status(customer_id: str):
    if customer_id not in customers:
        return {"error": "Customer not found"}
    return customers[customer_id]
