from collections import deque
from typing import Callable, Iterable, Union, TypeVar, Dict

from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    CallbackContext,
    Dispatcher,
    CallbackQueryHandler,
    CommandHandler
)
from telegram_utils.basic import make_message_sender

Button = TypeVar('Button', str, KeyboardButton, InlineKeyboardButton)
KeyboardMarkup = TypeVar('KeyboardMarkup', ReplyKeyboardMarkup, InlineKeyboardMarkup)
RecursiveKeyboardConfig = Dict[str, Union[str, Callable, 'RecursiveKeyboardConfig']]

def build_keyboard(
    buttons: Iterable[str],
    inline: bool = False,
    row_size = 3,
) -> KeyboardMarkup:
    """Buids keyboard from button list

    Args:
        buttons: iterable with buttons.
        inline: inline mode flag.
    Returns:
        keyboard markup.
    """
    buttons_lst = list(buttons)
    keyboard = [
        [button for button in buttons_lst[i: i + row_size]]
        for i in range(0, len(buttons_lst), row_size)
    ]
    keyboard_cls = InlineKeyboardMarkup if inline else ReplyKeyboardMarkup
    return keyboard_cls(keyboard)


class InlineRecursiveKeyboard:
    def __init__(
        self,
        conf_dct: RecursiveKeyboardConfig,
        start_command: str,
        ):
        self._start_command = start_command
        self._callback_by_pref = {}
        self._root_pref = self._full_pref('root')
        # initialize callback_by_pref
        dfs_stack = deque()
        dfs_stack.append(('root', conf_dct))
        while len(dfs_stack) != 0:
            pref, node = dfs_stack.pop()
            if isinstance(node, dict):
                callback_func = make_message_sender(
                    {
                        'text': pref,
                        'markup': self._pref_markup(pref, node)
                    }
                )
                for key, val in node.items():
                    dfs_stack.append((f'{pref}:{key}', val))
            elif isinstance(node, str):
                callback_func = make_message_sender(
                    {
                        'text': node,
                        'markup': self._pref_markup(pref, {})
                    }
                )
            else:
                callback_func = node
            self._callback_by_pref[self._full_pref] = callback_func

    def _full_pref(self, pref: str):
        return f'{pref}_{id(self)}'

    def _back_button(self, pref):
        prev_pref = pref[:pref.rfind(':')]
        return InlineKeyboardButton('back', callback_data=self._full_pref(prev_pref))

    def _pref_markup(self, pref, dct) -> InlineKeyboardMarkup:
        buttons = [
                InlineKeyboardButton(
                    key,
                    callback_data=self._full_pref(f'{pref}:{key}')
                ) for key in dct.keys()
            ]
        # add back button if not rott
        if self._full_pref(pref) != self._root_pref:
            buttons.append(self._back_button(pref))
        return build_keyboard(buttons, inline=True)

    def _make_start_handler(self):
        return CommandHandler(
            command=self._start_command,
            callback=self._callback_by_pref[self._root_pref]
        )

    def _make_prefs_handler(self):
        prefs = set(self._callback_by_pref.keys())
        def prefs_handler(update: Update, context: CallbackContext):
            return self._callback_by_pref[update.callback_query](
                update, context
            )
        return CallbackQueryHandler(
            prefs_handler,
            pattern=lambda cq: cq in prefs
        )

    def add(self, dispatcher: Dispatcher):
        """Add to keyboard handlers to dispatcher"""
        dispatcher.add_handler(self._make_start_handler())
        dispatcher.add_handler(self._make_prefs_handler())
