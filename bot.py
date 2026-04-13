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

# Customizable DM message content
PERSONAL_DM_MSG = """Hey {name}! 👋 

I saw you just joined the PWIOI group! I am your personal Mentor, Ravi.
If you want a referral for a smooth journey, have any doubts, or want to use my extra discount coupon (S0026), please send a direct message to my personal ID here: 
👉 @Ravi_Soni123

I'll reply to you directly from there!"""

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.new_chat_members:
        # Get the bot's username dynamically to create a direct link if needed
        bot_username = context.bot.username

        for user in update.message.new_chat_members:
            # Skip if the new member is a bot
            if user.is_bot:
                continue

            logger.info(f"New user joined: {user.full_name}")
            
            # Format the personal message with the user's name
            dm_text = PERSONAL_DM_MSG.format(name=user.first_name)

            # TRY TO SEND DIRECT MESSAGE (DM)
            try:
                await context.bot.send_message(chat_id=user.id, text=dm_text)
                logger.info(f"Successfully sent DM to {user.full_name}")
            
            except Exception as e:
                # If the bot is not allowed to DM the user, Telegram throws a Forbidden error.
                logger.warning(f"Could not DM {user.full_name}. Reason: {e}")
                
                # FALLBACK: Send a message in the group mentioning the user
                fallback_text = (
                    f"Welcome to the group, <a href='tg://user?id={user.id}'>{user.first_name}</a>! 🎉\n\n"
                    f"I tried to send you a welcome DM, but I am not allowed to initiate messages. "
                    f"Please start a chat with me here: @{bot_username} to get your personalized guide!"
                )
                await update.message.reply_text(text=fallback_text, parse_mode='HTML')

            # Also optionally send the main group welcome message
            try:
                await update.message.reply_text(WELCOME_MSG)
            except Exception as e:
                logger.error(f"Failed to send main welcome message: {e}")

if __name__ == "__main__":
    logger.info("Starting the bot...")
    
    import asyncio
    asyncio.set_event_loop(asyncio.new_event_loop())

    import threading
    import time
    import urllib.request
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

    def keep_alive():
        # Render automatically provides RENDER_EXTERNAL_URL, but we fallback to your app's explicit URL
        app_url = os.environ.get("RENDER_EXTERNAL_URL", "https://telegram-bot-77sm.onrender.com")
        while True:
            try:
                # Wait for 3 minutes before hitting the URL
                time.sleep(3 * 60)
                # Adding User-Agent so Render doesn't block the request as a bot
                req = urllib.request.Request(app_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                urllib.request.urlopen(req)
                logger.info(f"Cronjob: Successfully self-pinged {app_url} to keep app awake.")
            except Exception as e:
                logger.warning(f"Cronjob failed to ping: {e}")

    # Start the dummy web server
    threading.Thread(target=run_dummy_server, daemon=True).start()
    logger.info("Dummy web server started for Render's health check.")
    
    # Start the self-pinging keep-alive cronjob
    threading.Thread(target=keep_alive, daemon=True).start()
    logger.info("Internal Keep-Alive Cronjob started (Pinging every 3 mins).")
    # --------------------------------
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    
    logger.info("Bot is successfully polling! (Listening for events...)")
    app.run_polling()
