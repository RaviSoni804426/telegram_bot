from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

import os

TOKEN = "8439259468:AAGDZBkMlnVc0skX9LI71Ts6TjzxeV_16ns"  

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
            await update.message.reply_text(WELCOME_MSG)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

print("Bot is running...")
import asyncio

async def main():
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())