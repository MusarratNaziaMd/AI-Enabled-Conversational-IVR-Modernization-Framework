f# ivr_singlefile.py
"""
Single-file IVR + tests.

Usage:
  # Run voice IVR (uses microphone + speakers)
  python ivr_singlefile.py

  # Run tests (no microphone/speaker required)
  python ivr_singlefile.py test

You can also run tests with pytest:
  pytest ivr_singlefile.py -q

Notes:
- Tests mock listen() and speak() so they do not use audio hardware.
- logs are written to logs/ivr.log
"""

import os
import sqlite3
import time
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler

# The original audio libraries (used when running IVR normally)
import speech_recognition as sr
import pyttsx3

# ------------------ Logging Setup ------------------
os.makedirs("logs", exist_ok=True)
logger = logging.getLogger("ivr")
if not logger.handlers:
    logger.setLevel(logging.DEBUG)
    handler = RotatingFileHandler("logs/ivr.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

# ------------------ Voice Engine ------------------
def speak(text):
    """Speak text out loud (TTS) and print to console."""
    print(f"🗣 BOT: {text}")
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        # try to choose a female voice if available
        if len(voices) > 1:
            engine.setProperty('voice', voices[1].id)
        engine.setProperty('rate', 165)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
        time.sleep(0.3)
    except Exception as e:
        # Don't crash the program if TTS fails; log the error
        logger.exception(f"[Speech error] {e}")
        print(f"[Speech error] {e}")

def listen():
    """Listen from microphone and return recognized text (lowercased)."""
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
DB_FILE = "ivr.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
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
    logger.info("Database initialized")

def fetch_customer(cid):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM customers WHERE id=?", (cid,))
    row = cur.fetchone()
    conn.close()
    if row:
        cust = {"id": row[0], "name": row[1], "plan": row[2], "balance": row[3], "phone": row[4], "data_left": row[5]}
        logger.info(f"Fetched customer {cid}: {cust}")
        return cust
    logger.info(f"Customer {cid} not found")
    return None

def save_customer(cid, name):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        INSERT OR REPLACE INTO customers (id, name, plan, balance, phone, data_left)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (cid, name, "SmartPlan 299", 150.0, "9999999999", "1.5 GB"))
    conn.commit()
    conn.close()
    logger.info(f"Saved customer {cid} ({name})")

# ------------------ Intents ------------------
def intent_check_balance(cust):
    reply = f"Your current balance is rupees {cust['balance']}."
    logger.info(f"Intent: check_balance for {cust.get('id')}")
    speak(reply)
    return reply

def intent_plan_details(cust):
    reply = f"Your current plan is {cust['plan']} with {cust['data_left']} data per day."
    logger.info(f"Intent: plan_details for {cust.get('id')}")
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
        conn = sqlite3.connect(DB_FILE)
        conn.execute("UPDATE customers SET plan=?, data_left=? WHERE id=?", (cust['plan'], cust['data_left'], cust['id']))
        conn.commit()
        conn.close()
        speak("Upgrade successful.")
        logger.info(f"Customer {cust.get('id')} upgraded to {cust['plan']}")
        return "Upgraded to Premium Plan."
    else:
        speak("No problem. You can upgrade anytime from the main menu.")
        logger.info(f"Customer {cust.get('id')} skipped upgrade")
        return "Upgrade skipped."

def intent_offers(cust):
    speak("Here are your latest offers: 10% cashback on recharge above 299, double data on Premium plan, and weekend free calls on Super 699 plan.")
    logger.info(f"Intent: offers for {cust.get('id')}")
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
    conn = sqlite3.connect(DB_FILE)
    conn.execute("UPDATE customers SET balance=? WHERE id=?", (cust["balance"], cust["id"]))
    conn.commit()
    conn.close()
    reply = f"Recharge of rupees {amount} successful. New balance is {cust['balance']} rupees."
    speak(reply)
    logger.info(f"Customer {cust.get('id')} recharged {amount}. New balance {cust['balance']}")
    return reply

def intent_recharge_issue(cust):
    speak("We have noted your recharge issue. It will be fixed within two hours. Sorry for the inconvenience.")
    logger.info(f"Intent: recharge_issue for {cust.get('id')}")
    return "Recharge issue noted."

def intent_network_issue(cust):
    speak("We have noted your network or signal issue. Our technical team will optimize your area network soon.")
    logger.info(f"Intent: network_issue for {cust.get('id')}")
    return "Network issue logged."

def intent_sim_issue(cust):
    speak("SIM activation will be completed shortly. Please keep your phone restarted and SIM inserted.")
    logger.info(f"Intent: sim_issue for {cust.get('id')}")
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
    logger.info(f"Customer care session ended for {cust.get('id')}")
    return "Customer care ended."

def intent_exit(cust):
    speak("Thank you for using SmartTel IVR. Goodbye!")
    logger.info(f"Intent: exit for {cust.get('id')}")
    return "exit"

def intent_unknown(cust):
    speak("Sorry, I didn’t understand that.")
    logger.info("Intent: unknown")
    return "unknown"

# ------------------ Menu ------------------
def detect_intent(user_text):
    if not user_text:
        return "unknown"
    text = user_text.lower()
    if "balance" in text:
        return "check_balance"
    elif "plan" in text:
        return "plan_details"
    elif "offer" in text:
        return "offers"
    elif "data" in text or "upgrade" in text:
        return "data_packs"
    elif "recharge issue" in text:
        return "recharge_issue"
    elif "recharge" in text:
        return "recharge"
    elif "network" in text or "signal" in text:
        return "network_issue"
    elif "sim" in text or "activation" in text:
        return "sim_issue"
    elif "customer" in text or "care" in text or "talk" in text:
        return "customer_care"
    elif "exit" in text or "bye" in text:
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

# ------------------ Tests ------------------
# All tests are below. They mock listen() and speak() when needed so that tests don't
# use microphone or speakers. Tests use pytest conventions.

def _cleanup_db():
    try:
        os.remove(DB_FILE)
    except FileNotFoundError:
        pass

# Unit tests
def test_db_save_and_fetch():
    _cleanup_db()
    init_db()
    save_customer("9001", "UnitUser")
    c = fetch_customer("9001")
    assert c is not None
    assert c["name"] == "UnitUser"
    assert c["plan"].startswith("SmartPlan")

def test_detect_intent_cases():
    assert detect_intent("please tell my balance") == "check_balance"
    assert detect_intent("what is my plan") == "plan_details"
    assert detect_intent("i want to recharge") == "recharge"
    assert detect_intent("my sim activation") == "sim_issue"
    assert detect_intent("") == "unknown"
    assert detect_intent("some random thing") == "unknown"

# Integration tests: simulate functions by monkeypatching listen/speak
def test_intent_recharge_monkeypatch(monkeypatch):
    _cleanup_db()
    init_db()
    save_customer("3003", "RechargeUser")
    cust = fetch_customer("3003")
    # monkeypatch listen to return "199"
    monkeypatch.setattr(_name_ + ".listen", lambda: "199")
    # monkeypatch speak to no-op to avoid TTS
    monkeypatch.setattr(_name_ + ".speak", lambda txt: None)
    res = intent_recharge(cust)
    assert "Recharge of rupees 199" in res
    updated = fetch_customer("3003")
    assert updated["balance"] == 150.0 + 199

def test_intent_data_packs_upgrade(monkeypatch):
    _cleanup_db()
    init_db()
    save_customer("4004", "DataUser")
    cust = fetch_customer("4004")
    seq = iter(["yes"])
    monkeypatch.setattr(_name_ + ".listen", lambda: next(seq))
    monkeypatch.setattr(_name_ + ".speak", lambda txt: None)
    res = intent_data_packs(cust)
    # may return string indicating upgrade or update DB
    assert "Upgraded" in res or fetch_customer("4004")["data_left"] == "2.5 GB"

# E2E simulation (full flow) using monkeypatch
def test_e2e_full_flow(monkeypatch):
    _cleanup_db()
    init_db()
    save_customer("1001", "Aiza")
    # Sequence for listen(): customer id, choice 'menu', 'check my balance', 'exit'
    seq = iter([
        "one zero zero one",  # customer id
        "menu",               # choose main menu
        "check my balance",   # check balance
        "exit"                # exit
    ])
    monkeypatch.setattr(_name_ + ".listen", lambda: next(seq))
    monkeypatch.setattr(_name_ + ".speak", lambda txt: None)
    # Run main_ivr which will consume the sequence
    main_ivr()
    # After flow, ensure customer exists
    c = fetch_customer("1001")
    assert c is not None and c["name"] == "Aiza"

# Error handling test: listen returns empty string first, then a valid response
def test_error_handling_listen_empty(monkeypatch):
    _cleanup_db()
    init_db()
    save_customer("5005", "ErrUser")
    cust = fetch_customer("5005")
    seq = iter(["", "menu", "exit"])  # first empty (simulate noise), then menu, then exit
    monkeypatch.setattr(_name_ + ".listen", lambda: next(seq))
    monkeypatch.setattr(_name_ + ".speak", lambda txt: None)
    # call main_menu which will handle empty listen
    main_menu(cust)
    # if no exception, pass
    assert True

# Performance-ish test (quick)
def test_detect_intent_performance():
    start = time.time()
    for _ in range(200):
        detect_intent("please tell my balance")
    end = time.time()
    avg = (end - start) / 200
    # tolerate slow machines; assert reasonable speed
    assert avg < 0.05

# Logging test
def test_logging_written(monkeypatch):
    _cleanup_db()
    init_db()
    save_customer("7007", "LogUser")
    c = fetch_customer("7007")
    # monkeypatch speak to no-op
    monkeypatch.setattr(_name_ + ".speak", lambda txt: None)
    _ = intent_check_balance(c)
    assert os.path.exists("logs/ivr.log")
    with open("logs/ivr.log", "r", encoding="utf-8") as f:
        content = f.read()
    assert len(content.strip()) > 0

# ------------------ CLI ------------------
if _name_ == "_main_":
    import sys
    if len(sys.argv) > 1 and sys.argv[1].lower() in ("test", "tests", "--test"):
        print("Running tests with pytest...")
        import pytest
        # run pytest on this file
        exit_code = pytest.main([_file_, "-q"])
        sys.exit(exit_code)
    else:
        # Run the voice IVR (uses listen() and speak())
        os.system('cls' if os.name == 'nt' else 'clear')
        print("🎤 Starting SmartTel Voice IVR...")
        try:
            main_ivr()
        except KeyboardInterrupt:
            print("\nInterrupted by user. Exiting.")
        except Exception as e:
            logger.exception(f"Fatal error in IVR: {e}")
            print(f"Fatal error: {e}")
