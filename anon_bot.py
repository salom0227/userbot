import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = "8642757856:AAGDb_oRRDfEWMVX-dS53J8ZMYV8dYCT7G4"
OWNER_ID = 5971527578

user_map = {}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    if update.effective_chat.id == OWNER_ID:
        # Siz javob beryapsiz — foydalanuvchiga yuboring
        if update.message.reply_to_message:
            original = update.message.reply_to_message.message_id
            sender_id = user_map.get(original)
            if sender_id:
                await context.bot.send_message(sender_id, f"Javob: {text}")
        return

    # Foydalanuvchi yozdi — sizga forward
    sent = await context.bot.send_message(
        OWNER_ID,
        f"📩 Anonim xabar:\n\n{text}"
    )
    user_map[sent.message_id] = user.id
    await update.message.reply_text("Xabaringiz yetkazildi! ✅")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == '__main__':
    print("Anonim bot ishga tushdi!")
    app.run_polling()
