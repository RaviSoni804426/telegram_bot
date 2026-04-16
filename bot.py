from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass

from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ParseMode
from telegram.error import NetworkError
from telegram.ext import Application, ApplicationBuilder, ContextTypes, MessageHandler, filters

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

GROUP_WELCOME_MSG = """🚀 Stop scrolling. This could change your path.
*Welcome to PW Institute of Innovation*

Traditional college ka time gaya. *PW IOI* is new-age learning focused on career, skills, Tech, AI & MBA-level Business/Leadership, not just degrees.
If you’re into *AI, Tech or Management*, let’s build your future together.

*Choose Your Track:*
1️⃣ *4 years B.Tech in CS & AI* : Computer Science, AI, and Coding.
2️⃣ *MBA*: Business, Strategy, Leadership for real world. 

*Why PW IOI?*
🔥 Practical Learning: No boring theory, only real-world projects.
🔥 Expert Mentors: Industry leaders se seekhne ka mauka.
🔥 Early Start: Internship opportunities from 1st year onwards.

👇 *Register for Priority Callback:*
[https://forms.gle/GLjYLhY4yzaDbW3s6](https://forms.gle/GLjYLhY4yzaDbW3s6)

*More Info:*
📍 [pwioi.com](https://www.pwioi.com) | 📍 [pwioi.club](https://pwioi.club)
"""

@dataclass(frozen=True)
class BotConfig:
    token: str
    webhook_url: str | None
    port: int
    retry_delay_seconds: int
    use_webhook: bool


def load_config() -> BotConfig:
    token = (
        os.environ.get("TELEGRAM_TOKEN")
        or os.environ.get("BOT_TOKEN")
        or os.environ.get("TOKEN")
        or ""
    ).strip()
    if not token:
        raise RuntimeError(
            "Missing bot token. Set TELEGRAM_TOKEN, BOT_TOKEN, or TOKEN before starting the bot."
        )

    bot_mode = (os.environ.get("BOT_MODE") or "").strip().lower()
    if bot_mode and bot_mode not in {"polling", "webhook"}:
        raise RuntimeError("Invalid BOT_MODE. Use 'polling' or 'webhook'.")

    explicit_webhook_url = (os.environ.get("WEBHOOK_URL") or "").strip() or None
    render_webhook_url = (os.environ.get("RENDER_EXTERNAL_URL") or "").strip() or None

    if explicit_webhook_url:
        explicit_webhook_url = explicit_webhook_url.rstrip("/")
    if render_webhook_url:
        render_webhook_url = render_webhook_url.rstrip("/")

    use_webhook = False
    webhook_url = None

    if bot_mode == "webhook":
        webhook_url = explicit_webhook_url or render_webhook_url
        if not webhook_url:
            raise RuntimeError("BOT_MODE=webhook requires WEBHOOK_URL or RENDER_EXTERNAL_URL.")
        use_webhook = True
    elif bot_mode == "polling":
        use_webhook = False
    elif render_webhook_url:
        webhook_url = render_webhook_url
        use_webhook = True
    elif explicit_webhook_url:
        logger.info("WEBHOOK_URL is set, but BOT_MODE is not 'webhook'. Starting in polling mode.")

    port = int(os.environ.get("PORT", "10000"))
    retry_delay_seconds = max(5, int(os.environ.get("BOT_RETRY_DELAY_SECONDS", "15")))

    return BotConfig(
        token=token,
        webhook_url=webhook_url,
        port=port,
        retry_delay_seconds=retry_delay_seconds,
        use_webhook=use_webhook,
    )


import asyncio

async def delete_message_later(bot, chat_id: int, message_id: int, delay_seconds: int) -> None:
    await asyncio.sleep(delay_seconds)
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
        logger.info("Deleted welcome message %s in chat %s", message_id, chat_id)
    except Exception as e:
        logger.warning("Failed to delete message: %s", e)


async def welcome_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    if not message or not message.new_chat_members:
        return

    members = [member for member in message.new_chat_members if not member.is_bot]
    if not members:
        return

    sent_msg = await message.reply_text(
        GROUP_WELCOME_MSG,
        disable_web_page_preview=True,
        parse_mode=ParseMode.MARKDOWN,
    )
    
    # Schedule deletion after 5 minutes (300 seconds)
    asyncio.create_task(
        delete_message_later(
            bot=context.bot,
            chat_id=sent_msg.chat_id,
            message_id=sent_msg.message_id,
            delay_seconds=300
        )
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Unhandled exception while processing an update", exc_info=context.error)


def build_application(config: BotConfig) -> Application:
    application = ApplicationBuilder().token(config.token).build()
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_members))
    application.add_error_handler(error_handler)
    return application


def run_application(application: Application, config: BotConfig) -> None:
    if config.use_webhook and config.webhook_url:
        webhook_path = config.token
        logger.info("Starting bot in webhook mode on port %s", config.port)
        application.run_webhook(
            listen="0.0.0.0",
            port=config.port,
            url_path=webhook_path,
            webhook_url=f"{config.webhook_url}/{webhook_path}",
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
        )
        return

    logger.info("Starting bot in polling mode")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


def main() -> None:
    config = load_config()

    while True:
        application = build_application(config)
        try:
            run_application(application, config)
            break
        except NetworkError as exc:
            logger.warning(
                "Telegram network error: %s. Retrying in %s seconds.",
                exc,
                config.retry_delay_seconds,
            )
            time.sleep(config.retry_delay_seconds)
        except Exception:
            logger.exception("Bot stopped unexpectedly.")
            raise


if __name__ == "__main__":
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    main()
