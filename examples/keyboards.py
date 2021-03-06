# pylint: disable=missing-function-docstring, missing-module-docstring
from telegram import Update
from telegram.ext import CallbackContext
from dotenv import load_dotenv

from telegram_utils.basic import init_updater
from telegram_utils.keyboards import RecursiveKeyboard, InlineRecursiveKeyboard


CAT_URL = "https://cataas.com/cat"


def send_cat(update: Update, context: CallbackContext):
    context.bot.send_photo(update.effective_message.chat_id, CAT_URL)


keyboard_conf_dict = {
    'cat is somewhere here': {
        'deeper...': '<b> Oops, not here </b>'
    },
    'or here...': {
        'deeper...': {
            'cat!': send_cat
        }
    }
}

def main():
    load_dotenv()
    updater = init_updater()
    dispatcher = updater.dispatcher
    classes = (RecursiveKeyboard, InlineRecursiveKeyboard)
    commands = (
        ('start', 'finish'),
        ('start_inline', 'finish_inline')
    )
    for cls, command_lst in zip(classes, commands):
        keyboard = cls(
            conf_dct=keyboard_conf_dict,
            start_command=command_lst[0],
            finish_command=command_lst[1]
        )
        keyboard.add_to(dispatcher)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
