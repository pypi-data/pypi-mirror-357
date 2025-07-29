"""
keyboard_builder.py

Universal keyboard builder for aiogram bots, based on Pydantic models.
Easily add, format, and manage Telegram inline/reply keyboards.

Author: belyankiss
License: MIT
"""

from typing import Optional, Union, Tuple, Any, Dict

from aiogram.types import (
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    ForceReply,
    InlineKeyboardButton,
    KeyboardButton
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from pydantic import BaseModel, Field

TYPE_KEYBOARDS = (InlineKeyboardButton, KeyboardButton)
TYPE_ONCE_KEYBOARDS = (ReplyKeyboardRemove, ForceReply)
BUILDERS = {
    InlineKeyboardButton: InlineKeyboardBuilder,
    KeyboardButton: ReplyKeyboardBuilder
}

class DefaultKeyboardBuilder(BaseModel):
    """
    Universal keyboard builder for aiogram Telegram bots.

    Features:
        - Supports both Inline and Reply keyboards.
        - Dict-based storage for flexible button management.
        - Format any button text/callback_data with runtime variables.
        - Safe, non-mutating formatting.
        - Easily integrates as a base or mixin class.

    Example:
        class MyKb(DefaultKeyboardBuilder):
            btn1: InlineKeyboardButton = InlineKeyboardButton(text='Hello {username}', callback_data='cb1')
            btn2: InlineKeyboardButton = InlineKeyboardButton(text='World', callback_data='cb2')

        kb = MyKb()
        kb.format_buttons(username='oleg')
        markup = kb.reply_markup  # ready to send
    """

    buttons: Dict[Union[str, int], Union[InlineKeyboardButton, KeyboardButton]] = Field(default_factory=dict)
    """
    All keyboard buttons.
    Key: usually button text or unique id.
    Value: aiogram button object (InlineKeyboardButton or KeyboardButton).
    """

    reply_markup: Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply]] = None
    """Resulting aiogram markup object for message models."""

    sizes: Tuple[int, ...] = (1,)
    """Keyboard layout: how many buttons per row."""

    repeat: bool = False
    """Whether to repeat row sizes cyclically."""

    _kwargs: Any = None
    """Internal storage for formatting kwargs."""

    _clear: bool = False
    """Flag for full keyboard replacement in add_buttons/format_buttons."""

    _adder: bool = False
    """Internal flag to distinguish between normal and add_buttons initialization."""

    _formatter: bool = False
    """Internal flag to distinguish between normal and format_buttons initialization."""

    def model_post_init(self, context: Any, /) -> None:
        """
        Pydantic post-init hook.
        Automatically builds the keyboard after model creation or after changes.
        """
        if not self._adder and not self._formatter:
            self._get_buttons()
        self.reply_markup = self._build_keyboard()

    def add_buttons(
        self,
        *buttons: Union[InlineKeyboardButton, KeyboardButton],
        replace_keyboard: bool = False
    ) -> "DefaultKeyboardBuilder":
        """
        Add one or more buttons to the keyboard.

        Args:
            *buttons: Any number of aiogram button objects.
            replace_keyboard: If True, the keyboard is cleared and replaced with these buttons only.

        Returns:
            Self (for method chaining).
        """
        self._adder = True
        self._get_buttons()
        if replace_keyboard:
            self._clear = replace_keyboard
            self.buttons.clear()
        for button in buttons:
            self.buttons[button.text] = button
        if self._kwargs:
            self.format_buttons(**self._kwargs)
        self.model_post_init(None)
        self._adder = False
        return self

    def format_buttons(self, **kwargs) -> "DefaultKeyboardBuilder":
        """
        Format all button fields using provided kwargs (for template substitution).

        Args:
            **kwargs: Variables for string formatting (e.g., username='Oleg').

        Returns:
            Self (for method chaining).
        """
        self._formatter = True
        self._kwargs = kwargs
        new_buttons = {}
        if not self._clear:
            self._get_buttons()
        for key, button in self.buttons.items():
            new_buttons[key] = self._sub_format(button)
        self.buttons = new_buttons
        self.model_post_init(None)
        self._formatter = False
        return self

    def _sub_format(self, button: Union[InlineKeyboardButton, KeyboardButton]) -> Union[InlineKeyboardButton, KeyboardButton]:
        """
        Create a formatted copy of a button with values substituted from self._kwargs.

        Args:
            button: The original button object.

        Returns:
            A new button object with formatted fields.
        """
        new_model = {}
        old_model = button.model_dump()
        for key, value in old_model.items():
            try:
                new_model[key] = value.format_map(self._kwargs)
            except (KeyError, AttributeError):
                new_model[key] = value
        return type(button)(**new_model)

    def _build_keyboard(
            self,
            *inline_buttons: Union[InlineKeyboardButton],
            sizes: Tuple[int] = (1,),
            repeat: bool = False,
            **kwargs
    ) -> Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]]:
        """
        Build the final aiogram keyboard markup from all current buttons.

        Args:
            *inline_buttons: Inline buttons to use (for dynamic inline keyboards).
            sizes: Row sizes for layout.
            repeat: Whether to repeat sizes cyclically.
            **kwargs: Passed to as_markup (e.g. resize_keyboard=True).

        Returns:
            The aiogram keyboard markup object, or None if no buttons.
        """
        if inline_buttons:
            b = InlineKeyboardBuilder()
            b.add(*inline_buttons)
            return b.adjust(*sizes, repeat=repeat).as_markup(**kwargs)
        builder = None
        buttons = None
        if self.buttons:
            buttons = list(self.buttons.values())
            builder = BUILDERS.get(type(buttons[0]), None)
        if builder:
            builder = builder()
            builder.add(*buttons)
            return builder.adjust(*self.sizes, repeat=self.repeat).as_markup(resize_keyboard=True)
        return None

    def _get_buttons(self) -> None:
        """
        Collect all default (class-declared) buttons into the .buttons dictionary.
        """
        for key, value in self.__class__.model_fields.items():
            if isinstance(value.default, TYPE_ONCE_KEYBOARDS):
                self.reply_markup = value.default
                break
            elif isinstance(value.default, TYPE_KEYBOARDS):
                self.buttons[key] = value.default
