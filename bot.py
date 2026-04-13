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
 PWIOI- https://www.pwioi.com
 Life At PWIOI- https://www.pwioi.club


💬 Want referral for smooth journey or any doubts? DM now(@Ravi_Soni123)  or just use coupon code-S0026 for extra discount.

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
    
    import asyncio
    asyncio.set_event_loop(asyncio.new_event_loop())

    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class DummyHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Telegram Bot is online and polling!")

    def run_dummy_server():
        port = int(os.environ.get("PORT", 10000))
        server = HTTPServer(("0.0.0.0", port), DummyHandler)
        server.serve_forever()

    threading.Thread(target=run_dummy_server, daemon=True).start()
    logger.info("Dummy web server started for Render's health check.")
    # --------------------------------
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    
    logger.info("Bot is successfully polling! (Listening for events...)")
    app.run_polling()
