"""Recursive keyboards"""
import abc
from collections import deque
from typing import Callable, Union, TypeVar, Dict, List

from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove
)
from telegram.ext import (
    CallbackContext,
    Dispatcher,
    CallbackQueryHandler,
    MessageHandler,
    CommandHandler
)
from telegram.ext.filters import Filters
from telegram.ext.handler import Handler
from telegram_utils.basic import make_message_sender, reshape_sequence

Button = TypeVar('Button', str, KeyboardButton, InlineKeyboardButton)
KeyboardMarkup = TypeVar('KeyboardMarkup', ReplyKeyboardMarkup, InlineKeyboardMarkup)
RecursiveKeyboardConfig = Dict[str, Union[str, Callable, 'RecursiveKeyboardConfig']]


class RecursiveKeyboardABC(abc.ABC):
    """Base class for all recursive keyboards"""
    _shape_key = '__shape__'
    _root_pref = 'root'
    _back_value = 'back'

    def __init__(
        self,
        conf_dct: RecursiveKeyboardConfig,
        start_command: str,
        finish_command: str,
        name: str = 'Keyboard',
        delimiter: str = '::'
    ):
        self._start_command = start_command
        self._finish_command = finish_command
        self._name = name
        self._delimiter = delimiter

        self._root_pref = 'root'
        self._callback_by_pref = {}
        self._state_by_chat = {}
        self._lists = set()

        dfs_stack = deque()
        dfs_stack.append((self._root_pref, conf_dct))
        while len(dfs_stack) != 0:
            pref, node = dfs_stack.pop()
            if isinstance(node, dict):
                self._register_dict(pref, node)
                for key, new_node in node.items():
                    dfs_stack.append((pref + self._delimiter + key, new_node))
            elif isinstance(node, str):
                self._register_text(pref, node)
            elif callable(node):
                self._register_callback(pref, node)
            else:
                raise ValueError('Invalid node type')

    @staticmethod
    @abc.abstractmethod
    def _create_button(name: str) -> Button:
        pass

    @staticmethod
    @abc.abstractmethod
    def _create_keyboard_markup(button_lst: List[Button]) -> KeyboardMarkup:
        pass

    def _register_dict(self, pref: str, dct: Dict):
        shape = 3
        raw_buttons = []
        for name in dct.keys():
            if name == '__shape__':
                shape = dct[name]
                continue
            raw_buttons.append(self._create_button(name))
        buttons = reshape_sequence(raw_buttons, shape)
        if pref != self._root_pref:
            buttons.append([self._create_button(self._back_value)])
        self._callback_by_pref[pref] =  make_message_sender(
            {
                'text': pref,
                'reply_markup': self._create_keyboard_markup(buttons)
            }
        )

    def _register_text(self, pref: str, text: str):
        self._callback_by_pref[pref] = make_message_sender(
            {
                'text': text,
                'parse_mode': 'HTML'
            }
        )
        self._lists.add(pref)

    def _register_callback(self, pref: str, callback: Callable):
        self._callback_by_pref[pref] = callback
        self._lists.add(pref)

    def _create_start_callback(self):
        def start(update: Update, context: CallbackContext):
            context.bot.send_message(
                text='Starting...',
                chat_id=update.effective_chat.id
            )
            self._state_by_chat[update.effective_chat.id] = self._root_pref
            self._callback_by_pref['root'](update, context)
        return start

    def _button_callback(self, button, update: Update, context: CallbackContext):
        chat_id = update.effective_chat.id
        state = self._state_by_chat[chat_id]
        if button == 'back':
            to_execute = state[:state.rfind(self._delimiter)]
            new_state = to_execute
        else:
            to_execute = state + self._delimiter + button
            # in case of state being maximal prefix
            if to_execute in self._lists:
                new_state = state
            else:
                new_state = to_execute
        self._callback_by_pref[to_execute](update, context)
        self._state_by_chat[chat_id] = new_state

    @abc.abstractmethod
    def _create_button_handler(self) -> Handler:
        pass

    def _create_finish_callback(self) -> Handler:
        def finish(update: Update, context: CallbackContext):
            chat_id = update.effective_chat.id
            if chat_id in self._state_by_chat:
                text = f'Finishing {self._name}...'
            else:
                text = f'{self._name} did not started.'
            context.bot.send_message(
                text=text,
                chat_id=chat_id
            )
            self._callback_by_pref.pop(chat_id, None)
        return finish

    def add_to(self, dispatcher: Dispatcher) -> None:
        """Adds keyboard to the dispatcher"""
        dispatcher.add_handler(
            CommandHandler(
                self._start_command,
                self._create_start_callback()
            )
        )

        dispatcher.add_handler(self._create_button_handler())

        dispatcher.add_handler(
            CommandHandler(
                self._finish_command,
                self._create_finish_callback()
            )
        )


class RecursiveKeyboard(RecursiveKeyboardABC):
    """"Recursive keyboard"""
    @staticmethod
    def _create_button(name: str) -> KeyboardButton:
        return KeyboardButton(name)

    @staticmethod
    def _create_keyboard_markup(button_lst: List[KeyboardButton]) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(button_lst)

    def _create_button_handler(self) -> MessageHandler:
        def on_button(update: Update, context: CallbackContext):
            return self._button_callback(
                update.message.text,
                update,
                context
            )
        return MessageHandler(Filters.text & ~Filters.command, on_button)

    def _create_finish_callback(self) -> Handler:
        raw_finish = super()._create_finish_callback()
        def finish(update: Update, context: CallbackContext):
            context.bot.send_message(
                text='Removing markup...',
                reply_markup=ReplyKeyboardRemove(),
                chat_id=update.effective_chat.id
            )
            raw_finish(update, context)
        return finish


class InlineRecursiveKeyboard(RecursiveKeyboardABC):
    """Recursive keyboard with inline markup"""
    @staticmethod
    def _create_button(name: str) -> InlineKeyboardButton:
        return InlineKeyboardButton(name, callback_data=name)

    @staticmethod
    def _create_keyboard_markup(button_lst: List[Button]) -> KeyboardMarkup:
        return InlineKeyboardMarkup(button_lst)

    def _create_button_handler(self) -> CallbackQueryHandler:
        def on_button(update: Update, context: CallbackContext):
            return self._button_callback(
                update.callback_query.data,
                update,
                context
            )
        return CallbackQueryHandler(on_button)
