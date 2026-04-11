import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Enable logging so you can see errors in your deployment dashboard (Heroku/Render) logs!
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 1. BEST PRACTICE: Fetch token from Environment Variables in deployment.
# It falls back to your string for local testing if the var is missing.
TOKEN = os.environ.get("TELEGRAM_TOKEN", "8439259468:AAGDZBkMlnVc0skX9LI71Ts6TjzxeV_16ns")

WELCOME_MSG = """🚀 Stop scrolling. This could change your path.
If you're serious about Tech, AI & Real Skills — read this.

Welcome to "PW Institute of Innovation (PWIOI)" 💻

🎯 Choose your path:
👨‍💻 4-Year Computer Science Program  
📊 2-Year Management Program  

⚡ Learn by building — not just theory  
🤝 Work with real mentors  
🚀 Real opportunities  

👉 Apply here:
https://forms.gle/GLjYLhY4yzaDbW3s6

📢 Updates:
https://t.me/+eldsFyM3WjIyMWI9

💬 Want referral? DM now  

Just start. 🚀
"""

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.new_chat_members:
        for user in update.message.new_chat_members:
            logger.info(f"New user joined: {user.full_name}")
            try:
                await update.message.reply_text(WELCOME_MSG)
            except Exception as e:
                logger.error(f"Failed to send welcome message: {e}")

if __name__ == "__main__":
    logger.info("Starting the bot...")
    
    # Render uses Python 3.14.3 by default where event loop isn't auto-created. 
    # This manually patches it so `python-telegram-bot` doesn't crash!
    import asyncio
    asyncio.set_event_loop(asyncio.new_event_loop())
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    
    logger.info("Bot is successfully polling! (Listening for events...)")
    app.run_polling()