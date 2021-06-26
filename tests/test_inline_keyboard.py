# pylint: disable=missing-function-docstring, missing-module-docstring
import os

from telegram import Update
from telegram.ext import CallbackContext

from telegram_utils.basic import get_updater
from telegram_utils.keyboard import InlineRecursiveKeyboard

DATA_DIR = os.path.join(os.path.split(__file__)[0], 'data')
TOKEN_FILE = os.path.join(DATA_DIR, 'token.txt')
with open(os.path.join(DATA_DIR, 'cat_url.txt')) as f:
    CAT_URL = f.read().strip()
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
    updater = get_updater(TOKEN_FILE)
    dispatcher = updater.dispatcher
    keyboard = InlineRecursiveKeyboard(
        conf_dct=keyboard_conf_dict,
        start_command='start_cat'
    )
    keyboard.add_to(dispatcher)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
