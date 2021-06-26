"""Some basic utils ofently used in telegram projects"""
from typing import Callable, Sequence, Union, List
from functools import wraps, singledispatch

from telegram import Update, ChatAction
from telegram.ext import Updater, CallbackContext

def get_updater(path_to_token: str) -> Updater:
    """Get Updater by path to file with token"""
    with open(path_to_token) as f:
        return Updater(f.read().strip())


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
    """Makes callback function which sends message on the effect"""
    @typing
    def message_sender(update: Update, context: CallbackContext):
        context.bot.send_message(
            chat_id = update.effective_chat.id,
            **send_message_kwargs
        )
    return message_sender


@singledispatch
def reshape_sequence(sequence: Sequence, shape: Union[int, Sequence]) -> List:
    """Used mostly for keyboard creating"""
    if isinstance(shape, int):
        if shape <= 0:
            raise ValueError('Only positive shape is acceptable.')
        return [sequence[i: i + shape] for i in range(0, len(sequence), shape)]
    elif isinstance(shape, Sequence):
        ret = []
        cur_start = 0
        try:
            for row_len, idx in enumerate(shape):
                if row_len == -1:
                    if idx != len(shape) -1:
                        raise ValueError('-1 not at the end of shape array.')
                    ret.append(sequence[cur_start, -1])
                elif row_len > 0:
                    ret.append(sequence[cur_start: row_len])
                    cur_start += row_len
                else:
                    raise ValueError('Invalid row length.')
        except KeyError as ex:
            raise ValueError('Invalid shape array.') from ex
        return ret
    else:
        raise ValueError('Invalid shape parameter.')
