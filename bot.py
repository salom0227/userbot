import asyncio
import threading
import os
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.account import UpdateStatusRequest
from flask import Flask
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION = os.environ.get("SESSION")
RENDER_URL = os.environ.get("RENDER_URL", "")
ANON_TOKEN = "8642757856:AAGDb_oRRDfEWMVX-dS53J8ZMYV8dYCT7G4"
OWNER_ID = 5971527578

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot ishlayapti!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def ping_self():
    while True:
        try:
            if RENDER_URL:
                requests.get(RENDER_URL)
        except Exception:
            pass
        import time
        time.sleep(240)

# ============ ANONIM BOT ============
user_map = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! 👋\n\n"
        "Bu yerda fikr va izohlaringizni anonim yubora olasiz.\n"
        "Xabaringizni yozing — kim ekanligingiz ma'lum bo'lmaydi! 📩"
    )

async def handle_anon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    if update.effective_chat.id == OWNER_ID:
        if update.message.reply_to_message:
            original = update.message.reply_to_message.message_id
            sender_id = user_map.get(original)
            if sender_id:
                await context.bot.send_message(sender_id, f"{text}")
        return

    sent = await context.bot.send_message(
        OWNER_ID,
        f"📩 Anonim xabar:\n\n{text}"
    )
    user_map[sent.message_id] = user.id
    await update.message.reply_text("✅ Xabaringiz yetkazildi!")

async def run_anon_bot():
    anon_app = ApplicationBuilder().token(ANON_TOKEN).build()
    anon_app.add_handler(CommandHandler("start", start))
    anon_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_anon))
    print("Anonim bot ishga tushdi!")
    await anon_app.initialize()
    await anon_app.start()
    await anon_app.updater.start_polling()
    await asyncio.Event().wait()

# ============ USERBOT ============
user_state = {}

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    # Faqat shaxsiy chat
    if not event.is_private:
        return
    # O'zidan kelgan xabar
    me = await client.get_me()
    if event.sender_id == me.id:
        return
    # Botlardan kelgan xabar
    sender = await event.get_sender()
    if sender.bot:
        return

    # 5 sekund kutish
    await asyncio.sleep(5)

    # Agar siz javob bergan bo'lsangiz — jim tur
    messages = await client.get_messages(event.sender_id, limit=1)
    if messages[0].out:
        return

    sender_id = str(event.sender_id)
    count = user_state.get(sender_id, 0)

    try:
        if count == 0:
            await event.reply("Assalomu alaykum! 👋")
        elif count == 1:
            await event.reply("Nima gap? 🙂")
        else:
            await event.reply("Hozir bandman, tez orada javob beraman! ⏳")
        user_state[sender_id] = count + 1
    except Exception as e:
        print(f"Handler xato: {e}")

async def keep_online():
    while True:
        try:
            await client(UpdateStatusRequest(offline=False))
        except Exception:
            pass
        await asyncio.sleep(240)

async def keep_alive():
    while True:
        try:
            await client.get_me()
        except Exception:
            pass
        await asyncio.sleep(60)

async def main():
    await client.start()
    print("Userbot ishga tushdi!")
    try:
        await asyncio.gather(
            keep_online(),
            keep_alive(),
            run_anon_bot(),
            client.run_until_disconnected()
        )
    except (KeyboardInterrupt, SystemExit, asyncio.CancelledError):
        pass
    finally:
        await client.disconnect()

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=ping_self, daemon=True).start()
    asyncio.run(main())
