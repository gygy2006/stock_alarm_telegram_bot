import requests
import logging
import threading
import time
import os

from bs4 import BeautifulSoup
from telegram import InlineQueryResultArticle, InputTextMessageContent, Bot
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    InlineQueryHandler,
)

from scrapper import StockInformation

news_box = []
sent_message_box = []
TOKEN = os.environ.get("TOKEN")
ID = os.environ.get("ID")
TELEGRAM_URL = os.environ.get("TELEGRAM_URL")
BOT = Bot(token=TOKEN)
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher
updater.start_polling()  # start polling
# updater.stop() # stop start

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# update : user information requested to Telegram Bot
# context : my bot(?)


def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="command information\n/news"
    )


start_handler = CommandHandler("start", start)  # run on /start call
dispatcher.add_handler(start_handler)


def send_news(update, context):
    fill_news_box()
    for news in news_box:
        link = send_news_validate(update, context, news)
        if link:
            context.bot.send_message(chat_id=update.effective_chat.id, text=link)


def get_news():
    news = StockInformation(news_box)
    return news


def fill_news_box():
    news = get_news()
    news.get_news()


def send_news_validate(update, context, news):
    link = news[0]
    title = news[1]
    if link not in sent_message_box:
        sent_message_box.append(link)
        return link
    else:
        False


news_handler = CommandHandler("news", send_news)
dispatcher.add_handler(news_handler)


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)


def caps(update, context):
    # https://python-telegram-bot.readthedocs.io/en/latest/telegram.ext.callbackcontext.html // usage of context
    # context.args : return the "text" /caps "text" as a list containing the text.
    text_caps = " ".join(context.args).upper()
    print(text_caps)
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)


caps_handler = CommandHandler("caps", caps)  # run on /caps call
dispatcher.add_handler(caps_handler)


def inline_caps(update, context):
    query = update.inline_query.query
    print(query)
    if not query:
        return
    results = list()
    results.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title="Caps",
            input_message_content=InputTextMessageContent(query.upper()),
        )
    )
    context.bot.answer_inline_query(update.inline_query.id, results)


inline_caps_handler = InlineQueryHandler(inline_caps)
dispatcher.add_handler(inline_caps_handler)


def unknown(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry, I didn't understand that command.",
    )


unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)


def send_message():
    BOT.sendMessage(chat_id=ID, text="hihihi")
    threading.Timer(2.5, send_message).start()


# threading.Timer(2.5, send_message)
