import asyncio
import threading
import os
from groq import Groq
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.account import UpdateStatusRequest
from flask import Flask
import requests

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION = os.environ.get("SESSION")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
RENDER_URL = os.environ.get("RENDER_URL")

groq_client = Groq(api_key=GROQ_API_KEY)
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
            requests.get(RENDER_URL)
            print("Ping yuborildi!")
        except Exception:
            pass
        import time
        time.sleep(240)

async def ask_groq(text):
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """Sen aqlli va empatiyali yordamchisan. Odamlar bilan tabiiy gaplashasan.
Qoidalar:
- Hech qachon bot yoki AI ekanligingni aytma
- O'zbek tilida oddiy, tabiiy gapir
- Avval odamning muammosini to'liq tushun, keyin javob ber
- Muammoni hal qilishga harakat qil, aniq va foydali maslahat ber
- Agar savol texnik bo'lsa — oddiy tilda tushuntir
- Agar emotional muammo bo'lsa — avval tingla, hamdardlik bildir
- Bilmagan narsani so'rasalar: "Hozir band, keyinroq gaplashamiz" de
- Doim samimiy va insoniy bo'l"""
                },
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Groq xato: {e}")
        return "Hozir band, keyinroq gaplashamiz 🙂"

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

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    if not event.is_private:
        return
    sender = await event.get_sender()
    if sender.bot:
        return
    try:
        await asyncio.sleep(1)
        reply = await ask_groq(event.text)
        await event.reply(reply)
    except Exception as e:
        print(f"Handler xato: {e}")

async def main():
    await client.start()
    print("Bot ishga tushdi!")
    try:
        await asyncio.gather(
            keep_online(),
            keep_alive(),
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
