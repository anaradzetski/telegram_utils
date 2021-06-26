# pylint: disable=missing-function-docstring, missing-module-docstring
import os

from telegram.ext import CommandHandler, Filters
from telegram.ext.messagehandler import MessageHandler
from telegram_utils.registrator import HandlerRegistrator
from telegram_utils.basic import get_updater, typing

TOKEN_FILE = os.path.join(os.path.split(__file__)[0], 'data/token.txt')
REGISTRATOR = HandlerRegistrator()

@REGISTRATOR.register(CommandHandler, 'check')
@typing
def check(update, context):
    context.bot.send_message(
        text='Bot is running.',
        chat_id=update.message.chat.id
    )


@REGISTRATOR.register(MessageHandler, filters=~Filters.command & Filters.text)
@typing
def echo(update, context):
    context.bot.send_message(
        text=f'ECHO: {update.message.text}',
        chat_id=update.message.chat.id
    )


if __name__ == '__main__':
    updater = get_updater(TOKEN_FILE)
    dispatcher = updater.dispatcher
    REGISTRATOR.add_to(dispatcher)
    updater.start_polling()
    updater.idle()
