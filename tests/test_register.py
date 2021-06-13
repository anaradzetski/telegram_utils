from telegram.ext import CommandHandler, Filters
from telegram.ext.messagehandler import MessageHandler
from telegram_utils.registrator import HandlerRegistrator
from telegram_utils.basic import get_updater

REGISTRATOR = HandlerRegistrator()

@REGISTRATOR.register(CommandHandler, 'check')
def check(update, context):
    context.bot.send_message(
        text='Bot is running.',
        chat_id=update.message.chat.id
    )


@REGISTRATOR.register(MessageHandler, filters=~Filters.command & Filters.text)
def echo(update, context):
    context.bot.send_message(
        text=f'ECHO: {update.message.text}',
        chat_id=update.message.chat.id
    )


if __name__ == '__main__':
    updater = get_updater('token.txt')
    dispatcher = updater.dispatcher
    REGISTRATOR.add(dispatcher)
    updater.start_polling()
    updater.idle()
