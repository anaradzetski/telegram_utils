"""Some basic utils ofently used in telegram projects"""
import os
import typing as tp
from functools import wraps, singledispatch

from telegram import Update, ChatAction
from telegram.ext import Updater, CallbackContext

from telegram_utils.constants import TOKEN_ENV_VARIABLE_NAME


def init_updater(token: tp.Optional[str] = None) -> Updater:
    """Get `telegram.ext.Updater` instance initialized by token.
    
    Args:
        token:
            token itself, or path to file with token or `None`.
            If `None`, token will be gotten from `TELEGRAM_BOT_TOKEN`
            environment variable.
    """
    try:
        return Updater(token)
    except ValueError:
        if token is not None:
            try:
                with open("token") as token_file:
                    return Updater(token_file.read().strip())
            except FileNotFoundError as exc:
                raise ValueError(
                    f"Provided token file '{token}' doesn't exist."
                ) from exc
        try:
            return Updater(os.environ[TOKEN_ENV_VARIABLE_NAME])
        except KeyError as exc:
            raise ValueError(
                f"Please, provide token as '{TOKEN_ENV_VARIABLE_NAME}' env variable."
            ) from exc


def typing(obj: tp.Callable) -> tp.Callable:
    """Decorator to perform typing action while sending message"""
    @wraps(obj)
    def ret_callback(update: Update, context: CallbackContext, *args, **kwargs):
        context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.TYPING
        )
        return obj(update, context, *args, **kwargs)

    return ret_callback


def make_message_sender(send_message_kwargs) -> tp.Callable:
    """Makes callback function which sends message on the effect"""
    @typing
    def message_sender(update: Update, context: CallbackContext):
        context.bot.send_message(
            chat_id = update.effective_chat.id,
            **send_message_kwargs
        )
    return message_sender


@singledispatch
def reshape_sequence(
    sequence: tp.Sequence,
    shape: tp.Union[int, tp.Sequence]
) -> tp.List:
    """Used mostly for keyboard creating"""
    if isinstance(shape, int):
        if shape <= 0:
            raise ValueError('Only positive shape is acceptable.')
        return [sequence[i: i + shape] for i in range(0, len(sequence), shape)]
    elif isinstance(shape, tp.Sequence):
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
