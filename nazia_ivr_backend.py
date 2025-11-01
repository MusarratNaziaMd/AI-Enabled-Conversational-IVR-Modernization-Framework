import sqlite3
import pyttsx3
import speech_recognition as sr
import time
from datetime import datetime

# =====================================================
# 🧩 BACKEND DATABASE SETUP
# =====================================================

def init_db():
    conn = sqlite3.connect("ivr.db")
    cur = conn.cursor()

    # Customer table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id TEXT PRIMARY KEY,
            name TEXT,
            plan TEXT,
            balance REAL,
            phone TEXT
        )
    """)

    # Conversation history
    cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            user_msg TEXT,
            bot_reply TEXT,
            timestamp TEXT
        )
    """)

    # Insert sample customers if empty
    cur.execute("SELECT COUNT(*) FROM customers")
    if cur.fetchone()[0] == 0:
        customers = [
            ("1001", "Aiza", "Smart 299", 245.50, "9876543210"),
            ("1002", "Rahul", "Pro 499", 512.75, "9123456789"),
        ]
        cur.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?)", customers)
        conn.commit()

    conn.close()

init_db()


# =====================================================
# 🔊 SPEECH UTILITIES (Offline)
# =====================================================

engine = pyttsx3.init()
engine.setProperty('rate', 170)
engine.setProperty('volume', 1.0)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)  # female if available

def speak(text):
    """Convert text to speech"""
    print(f"🗣 BOT: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    """Listen to microphone and recognize speech"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n🎧 Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio, language='en-IN')
        print(f"👤 YOU: {text}")
        return text.lower()
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
        return ""
    except sr.RequestError:
        speak("Speech recognition service unavailable.")
        return ""


# =====================================================
# 🗄 DATABASE HELPER FUNCTIONS
# =====================================================

def fetch_customer(cid):
    conn = sqlite3.connect("ivr.db")
    cur = conn.cursor()
    cur.execute("SELECT id, name, plan, balance, phone FROM customers WHERE id=?", (cid,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "name": row[1], "plan": row[2], "balance": row[3], "phone": row[4]}
    return None

def register_customer(cid, name, phone):
    conn = sqlite3.connect("ivr.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO customers (id, name, plan, balance, phone) VALUES (?, ?, ?, ?, ?)",
                (cid, name, "Starter 199", 100.0, phone))
    conn.commit()
    conn.close()

def save_history(cid, user_msg, bot_reply):
    conn = sqlite3.connect("ivr.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO history (customer_id, user_msg, bot_reply, timestamp) VALUES (?, ?, ?, ?)",
                (cid, user_msg, bot_reply, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()


# =====================================================
# 💬 INTENT RECOGNITION
# =====================================================

def get_intent(user_text):
    """Determine intent from user speech"""
    if "balance" in user_text:
        return "balance"
    elif "plan" in user_text:
        return "plan"
    elif "recharge" in user_text:
        return "recharge"
    elif "customer care" in user_text or "support" in user_text:
        return "customer_care"
    elif "register" in user_text or "new user" in user_text:
        return "register"
    elif "exit" in user_text or "bye" in user_text or "end" in user_text:
        return "exit"
    else:
        return "unknown"


# =====================================================
# 🎯 MAIN IVR FLOW
# =====================================================

def main_ivr():
    speak("Welcome to SmartTel Hybrid I V R.")
    speak("Please say your Customer I D number.")

    cid = listen().replace(" ", "")
    if not cid:
        speak("No input detected. Please try again later.")
        return

    cust = fetch_customer(cid)

    if not cust:
        speak(f"Customer I D {cid} not found. Would you like to register?")
        ans = listen()
        if "yes" in ans:
            speak("Please say your name.")
            name = listen().title()
            speak("Please say your phone number.")
            phone = listen().replace(" ", "")
            register_customer(cid, name, phone)
            speak(f"Registration successful for {name}. You can now use our services.")
            cust = fetch_customer(cid)
        else:
            speak("Okay, registration cancelled. Goodbye.")
            return

    speak(f"Welcome back {cust['name']}. How can I help you today?")

    while True:
        speak("You can say: Check balance, Plan details, Recharge, Customer care, or Exit.")
        user_text = listen()
        if not user_text:
            continue

        intent = get_intent(user_text)

        if intent == "balance":
            reply = f"Your current balance is rupees {cust['balance']}."
        elif intent == "plan":
            reply = f"Your plan is {cust['plan']}. It includes unlimited calls and one point five G B data per day."
        elif intent == "recharge":
            new_balance = cust["balance"] + 100
            conn = sqlite3.connect("ivr.db")
            conn.execute("UPDATE customers SET balance=? WHERE id=?", (new_balance, cust["id"]))
            conn.commit()
            conn.close()
            cust["balance"] = new_balance
            reply = f"Recharge successful. One hundred rupees added. New balance is {new_balance}."
        elif intent == "customer_care":
            reply = "Connecting to customer care. Please hold. This is a demo simulation."
        elif intent == "exit":
            reply = "Thank you for using SmartTel I V R. Goodbye!"
            speak(reply)
            save_history(cust["id"], user_text, reply)
            break
        else:
            reply = "Sorry, I didn't understand that. Please say again."

        speak(reply)
        save_history(cust["id"], user_text, reply)
        time.sleep(1)


# =====================================================
# 🚀 RUN THE IVR
# =====================================================

if __name__ == "__main__":
    print("🎤 Starting SmartTel Offline Voice IVR...")
    main_ivr()
