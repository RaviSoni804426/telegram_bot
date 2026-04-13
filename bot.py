from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from html import escape

from dotenv import load_dotenv
from telegram import Update
from telegram.error import Forbidden, NetworkError, TelegramError
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

WELCOME_MSG = """Stop scrolling. This could change your path.

If you're serious about Tech, AI and real skills, read this.

Welcome to PW Institute of Innovation (PWIOI)

Choose your path:
4-Year Computer Science Program
2-Year Management Program

Learn by building, not just theory
Work with real mentors
Real opportunities

Apply here:
https://forms.gle/GLjYLhY4yzaDbW3s6

Updates:
PWIOI - https://www.pwioi.com
Life At PWIOI - https://www.pwioi.club

Want a referral or have doubts? DM @Ravi_Soni123 or use coupon code S0026 for an extra discount.

Just start.
"""

PERSONAL_DM_TEMPLATE = """Hey {name}!

I saw you just joined the PWIOI group. I am your personal mentor, Ravi.
If you want a referral for a smooth journey, have any doubts, or want to use my extra discount coupon (S0026), please send a direct message to my personal ID here:
@Ravi_Soni123

I'll reply to you directly from there."""


@dataclass(frozen=True)
class BotConfig:
    token: str
    webhook_url: str | None
    port: int
    retry_delay_seconds: int


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

    webhook_url = (
        os.environ.get("WEBHOOK_URL")
        or os.environ.get("RENDER_EXTERNAL_URL")
        or ""
    ).strip() or None
    if webhook_url:
        webhook_url = webhook_url.rstrip("/")

    port = int(os.environ.get("PORT", "10000"))
    retry_delay_seconds = max(5, int(os.environ.get("BOT_RETRY_DELAY_SECONDS", "15")))

    return BotConfig(
        token=token,
        webhook_url=webhook_url,
        port=port,
        retry_delay_seconds=retry_delay_seconds,
    )


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    first_name = update.effective_user.first_name if update.effective_user else "there"
    await update.message.reply_text(PERSONAL_DM_TEMPLATE.format(name=first_name))


async def welcome_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    if not message or not message.new_chat_members:
        return

    members = [member for member in message.new_chat_members if not member.is_bot]
    if not members:
        return

    bot_username = context.bot.username

    for member in members:
        display_name = member.first_name or member.full_name or "there"
        dm_text = PERSONAL_DM_TEMPLATE.format(name=display_name)
        try:
            await context.bot.send_message(chat_id=member.id, text=dm_text)
            logger.info("Sent DM to %s (%s)", member.full_name, member.id)
        except Forbidden:
            logger.info("Telegram blocked the DM to %s (%s)", member.full_name, member.id)
            await message.reply_text(
                text=build_dm_fallback_text(member, bot_username),
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
        except TelegramError as exc:
            logger.warning("Failed to send DM to %s (%s): %s", member.full_name, member.id, exc)
            await message.reply_text(
                text=build_dm_fallback_text(member, bot_username),
                parse_mode="HTML",
                disable_web_page_preview=True,
            )

    await message.reply_text(WELCOME_MSG, disable_web_page_preview=True)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Unhandled exception while processing an update", exc_info=context.error)


def build_dm_fallback_text(member, bot_username: str | None) -> str:
    safe_name = escape(member.first_name or member.full_name or "there")
    start_hint = (
        f"Please start a chat with me here: @{escape(bot_username)} so I can message you directly."
        if bot_username
        else "Please open my profile and press Start so I can message you directly."
    )
    return (
        f"Welcome to the group, <a href='tg://user?id={member.id}'>{safe_name}</a>!\n\n"
        "I tried to send you a welcome DM, but Telegram does not allow bots to message a user before they press Start.\n"
        f"{start_hint}"
    )


def build_application(config: BotConfig) -> Application:
    application = ApplicationBuilder().token(config.token).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_members))
    application.add_error_handler(error_handler)
    return application


def run_application(application: Application, config: BotConfig) -> None:
    if config.webhook_url:
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
    main()
