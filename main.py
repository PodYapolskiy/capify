#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import os
import logging
from datetime import datetime

from telegram import ForceReply, Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ContextTypes, filters
from telegram.ext import CommandHandler, MessageHandler

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def track_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_data = context.user_data

    date: str = user_data.get("date", "DD.MM.YYYY")
    amount: int = user_data.get("amount", 0)
    category: str = user_data.get("category", "bruh")
    subcategory: str = user_data.get("subcategory", "subbruh")
    description: str = user_data.get("description", "")

    await update.message.reply_text(
        "So, you've decided to track a transaction.\n"
        + "Here are it's info:\n"
        + f"date = {date}\n"
        + f"amount = {amount}\n"
        + f"category = {category}\n"
        + f"subcategory = {subcategory}\n"
        + f"description = {description}"
    )

    print(context.user_data)


def is_date(input_str: str):
    try:
        datetime.strptime(input_str, "%d.%m.%Y")
        return True
    except ValueError:
        return False


def is_amount(input_str: str):
    input_str = input_str.strip()
    if len(input_str) == 0:
        return False
    if input_str[0] == "-":
        return input_str[1:].isnumeric()
    return input_str.isnumeric()


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # categories
    CATEGORIES = {
        "Everyday": [
            "Food",
            "Restaurant",
        ],
        "Investments": ["Stocks", "Funds"],
    }

    # subcategories
    SUBCATEGORIES = []
    for k in CATEGORIES.keys():
        SUBCATEGORIES.extend(CATEGORIES[k])

    # text of message
    text = update.message.text.strip()

    if is_date(text):  # date input
        context.user_data["date"] = text
        await update.message.reply_text(
            f"Transaction date: {context.user_data['date']}"
        )

    elif is_amount(text):  # amount input
        context.user_data["amount"] = int(text)
        await update.message.reply_text(
            f"Transaction amount: {context.user_data['amount']}"
        )

    elif text in CATEGORIES:  # category input
        context.user_data["category"] = text
        await update.message.reply_text(
            f"Transaction category: {context.user_data['category']}"
        )

    elif text in SUBCATEGORIES:  # subcategory input
        context.user_data["subcategory"] = text
        await update.message.reply_text(
            f"Transaction subcategory: {context.user_data['subcategory']}"
        )

    else:  # description input
        context.user_data["description"] = text
        await update.message.reply_text(
            f"Transaction description: {context.user_data['description']}"
        )


async def keyboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Edit", callback_data="1"),
            InlineKeyboardButton("Confirm", callback_data="2"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Edit or Confirm transaction's data:\n"
        + f'Date: {context.user_data.get("date", "DD.MM.YYYY")}\n'
        + f'Amount: {context.user_data.get("amount", 0)}\n'
        + f'Category: {context.user_data.get("category", "Cat")}\n'
        + f'Subcategory: {context.user_data.get("subcategory", "Sub")}\n'
        + f'Description: {context.user_data.get("description", "")}',
        reply_markup=reply_markup,
    )


def main() -> None:
    """Start the bot."""

    # print(is_amount("100") is True)
    # print(is_amount("-100") is True)
    # print(is_amount("  100  ") is True)
    # print(is_amount("-100c") is False)
    # print(is_amount("-") is False)

    # Create the Application and pass it your bot's token.
    TOKEN = os.environ["TG_CAPIFY"]
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("track", track_command))
    application.add_handler(CommandHandler("keyboard", keyboard_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
    )

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
