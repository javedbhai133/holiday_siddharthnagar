from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import requests
from bs4 import BeautifulSoup

TOKEN = "8503291436:AAHKtdvy-VQw77tr-I8cEnPXnDZuOUEMO6k"

URL = "https://siddharthnagar.nic.in/notice/"
keywords = ["अवकाश", "Holiday", "बंद", "SDM", "DM"]

def check_holiday():
    try:
        r = requests.get(URL, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        notices = soup.find_all("a")

        for notice in notices:
            text = notice.get_text(strip=True)
            if any(word in text for word in keywords):
                return f"✅ *HOLIDAY POSSIBLE*\n\n📢 {text}\n\n⚠️ Official notice check kar lena"

        return "❌ *Aaj Siddharthnagar me holiday nahi hai*"

    except:
        return "⚠️ Website / Internet issue"

async def start(update: Update, context):
    await update.message.reply_text(
        "👋 Namaste!\n\n"
        "Type karo:\n"
        "👉 holiday\n"
        "👉 chhutti\n"
        "Aur main bataunga aaj ka status"
    )

async def reply(update: Update, context):
    msg = update.message.text.lower()
    if "holiday" in msg or "chhutti" in msg or "band" in msg:
        result = check_holiday()
        await update.message.reply_text(result, parse_mode="Markdown")
    else:
        await update.message.reply_text("❓ Sirf `holiday` ya `chhutti` likho")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

print("🤖 Telegram Holiday Bot Running...")
app.run_polling()