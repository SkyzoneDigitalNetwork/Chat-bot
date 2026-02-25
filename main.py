import os
import asyncio
import logging
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from groq import Groq

# Flask Server (Render-কে জাগিয়ে রাখার জন্য)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Alive!"

def run_flask():
    # Render ডিফল্টভাবে ১০,০০০ পোর্টে রান করে
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

client = Groq(api_key=GROQ_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("হ্যালো! আমি Llama-3.3-70b চালিত আপনার কোডিং অ্যাসিস্ট্যান্ট।")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_prompt = update.message.text
    try:
        # Llama-3.3-70b-versatile মডেল ব্যবহার করা হচ্ছে
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a highly skilled programmer. Provide expert solutions and clean code."},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.6,
        )
        response = completion.choices[0].message.content
        await update.message.reply_text(response)
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("দুঃখিত, বর্তমানে প্রসেস করতে সমস্যা হচ্ছে।")

async def main():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    # Flask সার্ভারকে আলাদা থ্রেডে চালানো যাতে বট ব্লক না হয়
    Thread(target=run_flask).start()

    async with application:
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        # বট চালু রাখার লুপ
        while True:
            await asyncio.sleep(10)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
