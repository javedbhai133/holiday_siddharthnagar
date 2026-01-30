from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests
from bs4 import BeautifulSoup
from datetime import datetime

TOKEN = "8503291436:AAHKtdvy-VQw77tr-I8cEnPXnDZuOUEMO6k"

KEYWORDS = ["अवकाश", "Holiday", "बंद", "SDM", "DM"]

# 🌍 District → Official Notice URL
DISTRICTS = {
    "siddharthnagar": "https://siddharthnagar.nic.in/notice/",
    "gorakhpur": "https://gorakhpur.nic.in/notice/",
    "basti": "https://basti.nic.in/notice/",
    "maharajganj": "https://maharajganj.nic.in/notice/"
}

# 🔍 Holiday checker
def check_holiday(url):
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        notices = soup.find_all("a")

        for notice in notices:
            text = notice.get_text(strip=True)
            if any(word in text for word in KEYWORDS):
                return True, text

        return False, None
    except:
        return None, None

# 🤖 JARVIS UI builder
def jarvis_ui(district, is_holiday, notice):
    date = datetime.now().strftime("%d %B %Y")
    district_name = district.title()

    if is_holiday:
        msg = (
            "🤖 *JARVIS REPORT*\n\n"
            f"📍 *District:* {district_name}\n"
            f"📅 *Date:* {date}\n\n"
            "✅ *Holiday Detected*\n\n"
            f"📢 _{notice}_\n\n"
            "⚠️ Recommendation: Official confirmation advised.\n\n"
            "🧠 *Status:* SYSTEM GREEN\n\n"
            "— _MADE BY JAVED_"
        )
    else:
        msg = (
            "🤖 *JARVIS REPORT*\n\n"
            f"📍 *District:* {district_name}\n"
            f"📅 *Date:* {date}\n\n"
            "❌ *No Holiday Detected*\n"
            "🏫 Schools / Offices operating normally.\n\n"
            "🧠 *Status:* SYSTEM NORMAL\n\n"
            "— _MADE BY JAVED_"
        )

    keyboard = [
        [
            InlineKeyboardButton("🔄 Recheck", callback_data=f"recheck|{district}"),
            InlineKeyboardButton("📍 Change District", callback_data="districts")
        ]
    ]

    return msg, InlineKeyboardMarkup(keyboard)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *JARVIS ONLINE*\n\n"
        "Main multiple districts ke holiday detect karta hoon.\n\n"
        "✍️ Command use karo:\n"
        "`holiday siddharthnagar`\n"
        "`holiday gorakhpur`\n"
        "`holiday basti`\n\n"
        "👥 Group me bhi kaam karta hoon.\n\n"
        "— _MADE BY JAVED_",
        parse_mode="Markdown"
    )

# 📍 District list
async def district_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton(d.title(), callback_data=f"check|{d}")]
        for d in DISTRICTS
    ]
    await update.message.reply_text(
        "📍 *Select District:*",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown"
    )

# 🧠 Text handler
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if text.startswith("holiday"):
        parts = text.split()
        if len(parts) < 2:
            await update.message.reply_text("⚠️ District likho\nExample: `holiday siddharthnagar`",
                                            parse_mode="Markdown")
            return

        district = parts[1]
        if district not in DISTRICTS:
            await update.message.reply_text("❌ District not supported yet")
            return

        is_holiday, notice = check_holiday(DISTRICTS[district])
        if is_holiday is None:
            await update.message.reply_text("⚠️ Website error, try later")
            return

        msg, kb = jarvis_ui(district, is_holiday, notice)
        await update.message.reply_text(msg, reply_markup=kb, parse_mode="Markdown")

# ▶️ Button handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "districts":
        await district_list(query, context)

    elif data.startswith("check|") or data.startswith("recheck|"):
        district = data.split("|")[1]
        is_holiday, notice = check_holiday(DISTRICTS[district])
        msg, kb = jarvis_ui(district, is_holiday, notice)
        await query.edit_message_text(msg, reply_markup=kb, parse_mode="Markdown")

# 🚀 RUN
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(CommandHandler("districts", district_list))
app.add_handler(filters.CallbackQueryHandler(button_handler))

print("🤖 JARVIS Holiday Bot Running | MADE BY JAVED")
app.run_polling()

