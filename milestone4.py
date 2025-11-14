from flask import Flask, request, jsonify
import sqlite3
import os
import logging
from logging.handlers import RotatingFileHandler

# ------------------ Logging Setup ------------------
os.makedirs("logs", exist_ok=True)
logger = logging.getLogger("ivr_web")
if not logger.handlers:
    logger.setLevel(logging.DEBUG)
    handler = RotatingFileHandler("logs/ivr_web.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# ------------------ Flask App ------------------
app = Flask(__name__)
DB_FILE = "ivr_web.db"

# ------------------ Database ------------------
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
        return {"id": row[0], "name": row[1], "plan": row[2], "balance": row[3], "phone": row[4], "data_left": row[5]}
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
    return f"Your current balance is rupees {cust['balance']}."

def intent_plan_details(cust):
    return f"Your current plan is {cust['plan']} with {cust['data_left']} data per day."

def intent_data_packs(cust, upgrade=False):
    if upgrade:
        cust['plan'] = "Premium 499"
        cust['data_left'] = "2.5 GB"
        conn = sqlite3.connect(DB_FILE)
        conn.execute("UPDATE customers SET plan=?, data_left=? WHERE id=?", (cust['plan'], cust['data_left'], cust['id']))
        conn.commit()
        conn.close()
        return "Upgraded to Premium Plan."
    return f"Current plan: {cust['plan']}, {cust['data_left']} per day. Available upgrades: Premium 499 (2.5 GB/day), Super 699 (4 GB/day)."

def intent_offers(cust):
    return "Latest offers: 10% cashback on recharge above 299, double data on Premium plan, weekend free calls on Super 699 plan."

def intent_recharge(cust, amount):
    cust['balance'] += float(amount)
    conn = sqlite3.connect(DB_FILE)
    conn.execute("UPDATE customers SET balance=? WHERE id=?", (cust["balance"], cust["id"]))
    conn.commit()
    conn.close()
    return f"Recharge of rupees {amount} successful. New balance is {cust['balance']} rupees."

def intent_recharge_issue(cust):
    return "Recharge issue logged. It will be fixed within two hours."

def intent_network_issue(cust):
    return "Network/signal issue noted. Our technical team will optimize your area."

def intent_sim_issue(cust):
    return "SIM activation in process. Please restart your phone and keep SIM inserted."

def intent_customer_care(cust, issue):
    # simplified for web
    issue = issue.lower()
    if "balance" in issue:
        return intent_check_balance(cust)
    elif "plan" in issue:
        return intent_plan_details(cust)
    elif "recharge" in issue:
        return intent_recharge_issue(cust)
    elif "data" in issue or "upgrade" in issue:
        return intent_data_packs(cust)
    elif "offer" in issue:
        return intent_offers(cust)
    elif "network" in issue:
        return intent_network_issue(cust)
    elif "sim" in issue:
        return intent_sim_issue(cust)
    else:
        return "Sorry, I did not understand your issue."

def detect_intent(user_text):
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

# ------------------ API Routes ------------------
@app.route("/fetch_customer", methods=["POST"])
def api_fetch_customer():
    data = request.json
    cid = data.get("id")
    cust = fetch_customer(cid)
    if cust:
        return jsonify(cust)
    else:
        return jsonify({"error": "Customer not found"}), 404

@app.route("/register", methods=["POST"])
def api_register():
    data = request.json
    cid = data.get("id")
    name = data.get("name")
    save_customer(cid, name)
    return jsonify({"message": f"Customer {name} registered successfully."})

@app.route("/intent", methods=["POST"])
def api_intent():
    data = request.json
    cid = data.get("id")
    user_text = data.get("text", "")
    upgrade = data.get("upgrade", False)
    amount = data.get("amount", 0)
    cust = fetch_customer(cid)
    if not cust:
        return jsonify({"error": "Customer not found"}), 404
    intent = detect_intent(user_text)
    if intent == "check_balance":
        return jsonify({"message": intent_check_balance(cust)})
    elif intent == "plan_details":
        return jsonify({"message": intent_plan_details(cust)})
    elif intent == "offers":
        return jsonify({"message": intent_offers(cust)})
    elif intent == "data_packs":
        return jsonify({"message": intent_data_packs(cust, upgrade)})
    elif intent == "recharge":
        return jsonify({"message": intent_recharge(cust, amount)})
    elif intent == "recharge_issue":
        return jsonify({"message": intent_recharge_issue(cust)})
    elif intent == "network_issue":
        return jsonify({"message": intent_network_issue(cust)})
    elif intent == "sim_issue":
        return jsonify({"message": intent_sim_issue(cust)})
    elif intent == "customer_care":
        issue = user_text
        return jsonify({"message": intent_customer_care(cust, issue)})
    elif intent == "exit":
        return jsonify({"message": "exit"})
    else:
        return jsonify({"message": "Sorry, I did not understand."})

# ------------------ Main ------------------
if __name__ == "__main__":
    init_db()
    # optional: prepopulate a customer
    save_customer("1001", "Aiza")
    logger.info("Starting Flask IVR backend...")
    app.run(host="0.0.0.0", port=5000, debug=True)
