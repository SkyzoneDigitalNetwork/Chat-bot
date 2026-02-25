import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from groq import Groq

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Environment Variables থেকে Key সংগ্রহ
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

client = Groq(api_key=GROQ_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("হ্যালো! আমি আপনার কোডিং অ্যাসিস্ট্যান্ট। আমাকে যেকোনো প্রোগ্রামিং প্রশ্ন করুন।")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_prompt = update.message.text
    
    try:
        # Groq API call
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # কোডিংয়ের জন্য এই মডেলটি সেরা
            messages=[
                {"role": "system", "content": "You are an expert programmer. Provide clean, efficient code and explanations."},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5,
        )
        
        response = completion.choices[0].message.content
        await update.message.reply_text(response)
        
    except Exception as e:
        await update.message.reply_text(f"দুঃখিত, একটি সমস্যা হয়েছে: {str(e)}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    
    application.add_handler(start_handler)
    application.add_handler(msg_handler)
    
    application.run_polling()
