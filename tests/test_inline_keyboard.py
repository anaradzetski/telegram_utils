from telegram_utils.basic import get_updater
from telegram_utils.keyboard import InlineRecursiveKeyboard



if __name__ == '__main__':
    updater = get_updater('token.txt')
    dispatcher = updater.dispatcher
    kb_conf_dct = {
        'hello' : {
            'world': '!'
        },
        'n': {
            'a': {
                's': {
                    't': {
                        'y': 'a'
                    }
                }
            }
        }
    }
    kb = InlineRecursiveKeyboard(conf_dct=kb_conf_dct, start_command='hi')
    kb.add(dispatcher)
    updater.start_polling()
    updater.idle()
