<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SmartTel Voice IVR</title>
<style>
  body {
    font-family: 'Arial', sans-serif;
    background: linear-gradient(to right, #f5f7fa, #c3cfe2);
    text-align: center;
    padding: 50px;
  }
  h1 {
    color: #1f3c88;
    margin-bottom: 30px;
  }
  button {
    padding: 15px 40px;
    font-size: 20px;
    background-color: #1f3c88;
    color: white;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    transition: background 0.3s ease;
  }
  button:hover {
    background-color: #3f5fa8;
  }
  #log {
    margin-top: 40px;
    text-align: left;
    max-width: 700px;
    margin-left: auto;
    margin-right: auto;
    background: #ffffffd1;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0px 5px 15px rgba(0,0,0,0.2);
    height: 350px;
    overflow-y: auto;
  }
  .log-entry { margin-bottom: 10px; }
  .bot { color: #1f3c88; font-weight: bold; }
  .user { color: #333; font-weight: normal; }
</style>
</head>
<body>

<h1>🎤 SmartTel Voice IVR</h1>
<button id="startBtn">Start Voice IVR</button>

<div id="log"></div>

<script>
const logDiv = document.getElementById("log");
const startBtn = document.getElementById("startBtn");

function log(text, type="bot") {
  const entry = document.createElement("div");
  entry.className = "log-entry " + type;
  entry.textContent = text;
  logDiv.appendChild(entry);
  logDiv.scrollTop = logDiv.scrollHeight;
  console.log(text);
}

// ----------------- TTS -----------------
function speak(text) {
  return new Promise((resolve) => {
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = 'en-IN';
    utter.rate = 1;
    utter.onend = resolve;
    speechSynthesis.speak(utter);
    log(text, "bot");
  });
}

// ----------------- STT -----------------
function listen() {
  return new Promise((resolve, reject) => {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-IN';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onresult = (event) => {
      const text = event.results[0][0].transcript.toLowerCase();
      log(text, "user");
      resolve(text);
    };

    recognition.onerror = async (event) => {
      await speak("Sorry, I didn't catch that. Please speak clearly.");
      resolve(await listen());
    };

    recognition.start();
  });
}

// ----------------- Backend -----------------
async function callBackend(endpoint, data={}) {
  try {
    const res = await fetch(`http://127.0.0.1:5000/${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return await res.json();
  } catch(err) {
    console.error(err);
    await speak("Backend not responding. Please check server.");
    return null;
  }
}

// ----------------- Main Flow -----------------
async function mainFlow() {
  await speak("Welcome to SmartTel Voice IVR system.");
  await speak("Please say your customer ID.");

  let cid = await listen();
  cid = cid.replace(/\s/g, "");

  let customer = await callBackend("fetch_customer", { id: cid });

  if (!customer) {
    await speak(`Customer ID ${cid} not found. Would you like to register?`);
    let ans = await listen();
    if (ans.includes("yes")) {
      await speak("Please say your name.");
      let name = await listen();
      name = name.split(" ").map(w => w[0].toUpperCase() + w.slice(1)).join(" ");
      await callBackend("register", { id: cid, name: name });
      await speak(`Registration successful. Welcome ${name}!`);
      customer = await callBackend("fetch_customer", { id: cid });
    } else {
      await speak("Okay, please register later. Goodbye.");
      return;
    }
  } else {
    await speak(`Welcome back ${customer.name}.`);
  }

  let exit = false;

  while(!exit) {
    await speak("Main menu. You can say: check balance, plan details, offers, data packs, recharge, talk to customer care, network issue, sim activation, or exit.");
    let cmd = await listen();

    if (cmd.includes("balance")) {
      const res = await callBackend("check_balance", { id: cid });
      await speak(res.message);
    } else if (cmd.includes("plan")) {
      const res = await callBackend("plan_details", { id: cid });
      await speak(res.message);
    } else if (cmd.includes("offer")) {
      const res = await callBackend("offers", { id: cid });
      await speak(res.message);
    } else if (cmd.includes("data") || cmd.includes("upgrade")) {
      const res = await callBackend("data_packs", { id: cid });
      await speak(res.message);
    } else if (cmd.includes("recharge")) {
      await speak("Please say the amount: 199, 299, or 499 rupees.");
      const amt = await listen();
      const res = await callBackend("recharge", { id: cid, amount: amt });
      await speak(res.message);
    } else if (cmd.includes("customer") || cmd.includes("care") || cmd.includes("talk")) {
      const res = await callBackend("customer_care", { id: cid });
      await speak(res.message);
    } else if (cmd.includes("network")) {
      await speak("Network issue detected. Our technical team will optimize your area.");
    } else if (cmd.includes("sim") || cmd.includes("activation")) {
      await speak("SIM activation in progress. Please restart your phone and keep SIM inserted.");
    } else if (cmd.includes("exit") || cmd.includes("bye")) {
      await speak("Thank you for using SmartTel IVR. Goodbye!");
      exit = true;
    } else {
      await speak("Sorry, I didn't understand that. Please speak clearly.");
    }
  }
}

startBtn.onclick = async () => {
  startBtn.disabled = true;
  await mainFlow();
  startBtn.disabled = false;
};
</script>
</body>
</html>
