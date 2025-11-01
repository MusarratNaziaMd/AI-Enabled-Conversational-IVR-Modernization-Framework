import sqlite3
from datetime import datetime
import speech_recognition as sr
import pyttsx3
import time
import os

# ------------------ Voice Engine ------------------
def speak(text):
    print(f"🗣 BOT: {text}")
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[1].id)
        engine.setProperty('rate', 165)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
        time.sleep(0.3)
    except Exception as e:
        print(f"[Speech error] {e}")

def listen():
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
        speak("Sorry, I didn’t catch that.")
        return ""
    except sr.RequestError:
        speak("Speech service unavailable.")
        return ""

# ------------------ Database ------------------
def init_db():
    conn = sqlite3.connect("ivr.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id TEXT PRIMARY KEY,
            name TEXT,
            plan TEXT,
            balance REAL,
            phone TEXT,
            data_left TEXT
        )
    """)
    conn.commit()
    conn.close()

def fetch_customer(cid):
    conn = sqlite3.connect("ivr.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM customers WHERE id=?", (cid,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "name": row[1], "plan": row[2], "balance": row[3], "phone": row[4], "data_left": row[5]}
    return None

def save_customer(cid, name):
    conn = sqlite3.connect("ivr.db")
    conn.execute("""
        INSERT OR REPLACE INTO customers (id, name, plan, balance, phone, data_left)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (cid, name, "SmartPlan 299", 150.0, "9999999999", "1.5 GB"))
    conn.commit()
    conn.close()

# ------------------ Intents ------------------
def intent_check_balance(cust):
    reply = f"Your current balance is rupees {cust['balance']}."
    speak(reply)
    return reply

def intent_plan_details(cust):
    reply = f"Your current plan is {cust['plan']} with {cust['data_left']} data per day."
    speak(reply)
    return reply

def intent_data_packs(cust):
    speak(f"Your current plan is {cust['plan']} with {cust['data_left']} data per day.")
    speak("Available upgrades include: Premium 499 with 2.5 GB per day, and Super 699 with 4 GB per day. Would you like to upgrade?")
    ans = listen()
    if "yes" in ans:
        speak("Upgrading you to Premium Plan 499. Enjoy higher data speed and extra benefits!")
        cust['plan'] = "Premium 499"
        cust['data_left'] = "2.5 GB"
        conn = sqlite3.connect("ivr.db")
        conn.execute("UPDATE customers SET plan=?, data_left=? WHERE id=?", (cust['plan'], cust['data_left'], cust['id']))
        conn.commit()
        conn.close()
        speak("Upgrade successful.")
        return "Upgraded to Premium Plan."
    else:
        speak("No problem. You can upgrade anytime from the main menu.")
        return "Upgrade skipped."

def intent_offers(cust):
    speak("Here are your latest offers: 10% cashback on recharge above 299, double data on Premium plan, and weekend free calls on Super 699 plan.")
    return "Offers shared."

def intent_recharge(cust):
    speak("Here are some recharge options: 199, 299, or 499 rupees. Please say your choice.")
    choice = listen()
    if "199" in choice:
        amount = 199
    elif "299" in choice:
        amount = 299
    elif "499" in choice:
        amount = 499
    else:
        speak("Invalid option. Defaulting to 199 rupees.")
        amount = 199
    cust['balance'] += amount
    conn = sqlite3.connect("ivr.db")
    conn.execute("UPDATE customers SET balance=? WHERE id=?", (cust["balance"], cust["id"]))
    conn.commit()
    conn.close()
    reply = f"Recharge of rupees {amount} successful. New balance is {cust['balance']} rupees."
    speak(reply)
    return reply

def intent_recharge_issue(cust):
    speak("We have noted your recharge issue. It will be fixed within two hours. Sorry for the inconvenience.")
    return "Recharge issue noted."

def intent_network_issue(cust):
    speak("We have noted your network or signal issue. Our technical team will optimize your area network soon.")
    return "Network issue logged."

def intent_sim_issue(cust):
    speak("SIM activation will be completed shortly. Please keep your phone restarted and SIM inserted.")
    return "SIM activation under process."

def intent_customer_care(cust):
    speak("Connecting you to SmartTel customer care. Please describe your issue.")
    while True:
        issue = listen()
        if not issue:
            continue

        # Direct mapping from customer care
        if "menu" in issue or "main menu" in issue:
            speak("Opening main menu for you.")
            main_menu(cust)
            break
        elif "balance" in issue:
            intent_check_balance(cust)
        elif "plan" in issue:
            intent_plan_details(cust)
        elif "recharge issue" in issue:
            intent_recharge_issue(cust)
        elif "recharge" in issue:
            intent_recharge(cust)
        elif "data" in issue or "upgrade" in issue:
            intent_data_packs(cust)
        elif "offer" in issue:
            intent_offers(cust)
        elif "network" in issue or "signal" in issue or "coverage" in issue:
            intent_network_issue(cust)
        elif "sim" in issue or "activation" in issue:
            intent_sim_issue(cust)
        elif "thank" in issue:
            speak("Would you like to continue or exit?")
            ans = listen()
            if "exit" in ans:
                speak("Thank you for contacting SmartTel support. Have a nice day!")
                break
        elif "bye" in issue or "exit" in issue:
            speak("Thank you for contacting SmartTel support. Goodbye!")
            break
        else:
            speak("Sorry, could you please explain again?")
    return "Customer care ended."

def intent_exit(cust):
    speak("Thank you for using SmartTel IVR. Goodbye!")
    return "exit"

def intent_unknown(cust):
    speak("Sorry, I didn’t understand that.")
    return "unknown"

# ------------------ Menu ------------------
def detect_intent(user_text):
    if not user_text:
        return "unknown"
    if "balance" in user_text:
        return "check_balance"
    elif "plan" in user_text:
        return "plan_details"
    elif "offer" in user_text:
        return "offers"
    elif "data" in user_text or "upgrade" in user_text:
        return "data_packs"
    elif "recharge issue" in user_text:
        return "recharge_issue"
    elif "recharge" in user_text:
        return "recharge"
    elif "network" in user_text or "signal" in user_text:
        return "network_issue"
    elif "sim" in user_text or "activation" in user_text:
        return "sim_issue"
    elif "customer" in user_text or "care" in user_text or "talk" in user_text:
        return "customer_care"
    elif "exit" in user_text or "bye" in user_text:
        return "exit"
    else:
        return "unknown"

def main_menu(cust):
    while True:
        speak("Main menu. You can say check balance, plan details, offers, data packs, recharge, talk to customer care, or exit.")
        user_text = listen()
        intent = detect_intent(user_text)

        if intent == "check_balance":
            intent_check_balance(cust)
        elif intent == "plan_details":
            intent_plan_details(cust)
        elif intent == "offers":
            intent_offers(cust)
        elif intent == "data_packs":
            intent_data_packs(cust)
        elif intent == "recharge":
            intent_recharge(cust)
        elif intent == "recharge_issue":
            intent_recharge_issue(cust)
        elif intent == "network_issue":
            intent_network_issue(cust)
        elif intent == "sim_issue":
            intent_sim_issue(cust)
        elif intent == "customer_care":
            intent_customer_care(cust)
        elif intent == "exit":
            intent_exit(cust)
            break
        else:
            intent_unknown(cust)

# ------------------ Main ------------------
def main_ivr():
    init_db()
    save_customer("1001", "Aiza")

    speak("Welcome to SmartTel Hybrid Voice IVR system.")
    speak("Please say your customer I D, for example one zero zero one.")
    cid_text = listen().replace(" ", "")

    mapping = {"one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9", "zero": "0"}
    for w, n in mapping.items():
        cid_text = cid_text.replace(w, n)

    cust = fetch_customer(cid_text)
    if not cust:
        speak(f"Customer I D {cid_text} not found. Would you like to register?")
        ans = listen()
        if "yes" in ans:
            speak("Please say your name.")
            name = listen().title()
            save_customer(cid_text, name)
            speak(f"Registration successful. Welcome {name}!")
            cust = fetch_customer(cid_text)
        else:
            speak("Okay, please register later. Goodbye.")
            return

    speak(f"Welcome back {cust['name']}. Would you like to open the main menu or talk to customer care?")
    choice = listen()
    if "menu" in choice:
        main_menu(cust)
    elif "customer" in choice or "care" in choice or "talk" in choice:
        intent_customer_care(cust)
    else:
        speak("Opening main menu by default.")
        main_menu(cust)

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    print("🎤 Starting SmartTel Voice IVR...")
    main_ivr()
