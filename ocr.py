import os
import easyocr
from flask import Flask, request
import requests

# -----------------------------
# Config
# -----------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # Render এর Environment Variables এ রাখবেন
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # Render app URL + /<BOT_TOKEN>
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# OCR রিডার
reader = easyocr.Reader(['en', 'bn'], gpu=False)

# Flask app
app = Flask(__name__)

# -----------------------------
# Telegram API হেল্পার ফাংশন
# -----------------------------
def send_message(chat_id, text):
    url = f"{API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, json=payload)

# -----------------------------
# Webhook Endpoint
# -----------------------------
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()

    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]

        # যদি ছবি পাঠানো হয়
        if "photo" in message:
            file_id = message["photo"][-1]["file_id"]
            file_info = requests.get(f"{API_URL}/getFile?file_id={file_id}").json()
            file_path = file_info["result"]["file_path"]

            # ছবি ডাউনলোড
            file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
            img_path = "input.jpg"
            img_data = requests.get(file_url).content
            with open(img_path, "wb") as f:
                f.write(img_data)

            # OCR চালানো
            result = reader.readtext(img_path)
            extracted_text = "\n".join([d[1] for d in result])

            if extracted_text.strip() == "":
                send_message(chat_id, "⚠️ কোনো লেখা পাওয়া যায়নি। পরিষ্কার ছবি দিন।")
            else:
                formatted = f"""
<b>📝 OCR RESULT</b>
─────────────────────
<pre>{extracted_text}</pre>
─────────────────────
👑 Admin: SHADOW JOKER  
📢 Group: CYBER TEAM HELP  
📧 Email: cyberteamhelp369@gmail.com  
☎️ Contact: 01950178309
"""
                send_message(chat_id, formatted)

        else:
            send_message(chat_id, "📌 দয়া করে একটি ছবি পাঠান।")

    return {"ok": True}

# -----------------------------
# Root Route
# -----------------------------
@app.route("/")
def home():
    return "✅ OCR Bot is running!"

# -----------------------------
# Set Webhook (Run Once)
# -----------------------------
def set_webhook():
    url = f"{API_URL}/setWebhook?url={WEBHOOK_URL}/{BOT_TOKEN}"
    r = requests.get(url)
    print(r.json())

if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))