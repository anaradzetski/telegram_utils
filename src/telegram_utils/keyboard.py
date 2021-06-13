from typing import Iterable, Union

from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import CallbackContext

def build_keyboard(
    buttons: Iterable[str],
    inline: bool = False,
    row_size = 3,
) -> Union[ReplyKeyboardMarkup, InlineKeyboardMarkup]:
    """Buids keyboard from button list

    Args:
        buttons: iterable with button names.
        inline: inline mode flag.
    Returns:
        keyboard markup.
    """
    buttons_lst = list(buttons)
    button_cls = InlineKeyboardButton if inline else KeyboardButton
    keyboard = [
        [button_cls(name) for name in buttons_lst[i: i + row_size]]
        for i in range(0, len(buttons_lst), row_size)
    ]
    keyboard_cls = InlineKeyboardMarkup if inline else ReplyKeyboardMarkup
    return keyboard_cls(keyboard)

    