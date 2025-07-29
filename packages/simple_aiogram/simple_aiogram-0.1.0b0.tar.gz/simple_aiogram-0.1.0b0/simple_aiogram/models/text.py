from typing import Optional

from .keyboard_builder import DefaultKeyboardBuilder
from .files import FileForm

class TextForms(DefaultKeyboardBuilder, FileForm):
    """
    Base model for message templates in Telegram bots.
    Combines keyboard builder and file fields, and allows
    storing message text for formatting or reuse.

    Attributes:
        text: Optional text message template (can be formatted with variables).
    """
    text: Optional[str] = None
