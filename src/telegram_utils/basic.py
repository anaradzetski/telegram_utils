import re
from typing import Callable
from functools import wraps

from telegram import Update, ChatAction
from telegram.ext import Updater, CallbackContext

def get_updater(path_to_token: str) -> Updater:
    """Get Updater by path to file with token"""
    with open(path_to_token) as f:
        return Updater(re.match(r'\S+', f.read()).group(0))


def typing(obj: Callable) -> Callable:
    """Decorator to perform typing action while sending message"""
    @wraps(obj)
    def ret_callback(update: Update, context: CallbackContext, *args, **kwargs):
        context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.TYPING
        )
        return obj(update, context, *args, **kwargs)

    return ret_callback


def make_message_sender(send_message_kwargs) -> Callable:
    """Makes callback context which sends message on the effect"""
    @typing
    def message_sender(update: Update, context: CallbackContext):
        context.bot.send_message(
            chat_id = update.effective_chat.id,
            **send_message_kwargs
        )
    return message_sender
