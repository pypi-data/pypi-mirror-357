# simple_aiogram

**Powerful, declarative message and keyboard builder for aiogram bots, powered by Pydantic models.  
Send, edit, and manage all kinds of Telegram messages and keyboards — as Python classes.**

[![PyPI](https://img.shields.io/pypi/v/simple_aiogram?style=flat-square)](https://pypi.org/project/simple_aiogram/)
[![MIT License](https://img.shields.io/github/license/belyankiss/aiogram_windows?style=flat-square)](LICENSE)

---

## ✨ Features

- **Declarative**: Describe messages, media, and keyboards as Python models.
- **Universal**: Works with text, photo, video, documents, and all Telegram keyboards.
- **Auto-keyboards**: Define buttons as class fields, get reply_markup automatically.
- **Flexible**: Format any text/callback with runtime variables (`str.format_map`).
- **Async**: All methods awaitable and designed for modern aiogram.
- **File caching**: Smart file_id cache for instant media re-use.
- **Extensible**: Use as a base class or mixin for your own message types.

---

## 🚀 Quick Start

```python
from aiogram.types import Message, InlineKeyboardButton
from aiogram.filters import CommandStart

from simple_aiogram import TelegramWindow, BotModel

from my_routers import example_router

bot = BotModel(token="YOUR_BOT_TOKEN")
dp = bot.dispatcher

bot.include_router(example_router)


class HelloWindow(TelegramWindow):
    text: str = "Hello, {username}!"
    one: InlineKeyboardButton = InlineKeyboardButton(
        text="Click me",
        callback_data="clicked_{user_id}"
    )


@dp.message(CommandStart())
async def hello_handler(msg: Message):
    window = HelloWindow(event=msg)
    window.format_buttons(user_id=msg.from_user.id)
    await window.answer(username=msg.from_user.username)


if __name__ == "__main__":
    bot.run()

```

## 🎛️ Keyboard Example
### Inline or Reply Keyboard — just declare buttons as class attributes:

```python
from aiogram import Router, F
from aiogram.types import InlineKeyboardButton, Message

from simple_aiogram import TelegramWindow

example_router = Router(name="example")

class KeyboardExample(TelegramWindow):
    text: str = "Choose:"
    btn1: InlineKeyboardButton = InlineKeyboardButton(text="Yes", callback_data="yes_{user_id}")
    btn2: InlineKeyboardButton = InlineKeyboardButton(text="No", callback_data="no_{user_id}")
    btn3: InlineKeyboardButton = InlineKeyboardButton(text="Maybe", callback_data="maybe_{user_id}")

# Send with auto-built keyboard
@example_router.message(F.text.contains("some text"))
async def hello_handler(msg: Message):
    kb = KeyboardExample(event=msg)
    kb.format_buttons(user_id=msg.from_user.id)
    await kb.answer()
```

### Or add buttons dynamically:

```python
window = HelloWindow(event=msg)
window.add_buttons(
    InlineKeyboardButton(text="Profile", callback_data="profile_{user_id}")
)
window.format_buttons(user_id=msg.from_user.id)
await window.answer(username=msg.from_user.username)
```

## 📦 Sending Media with File Caching
### Send a photo/document/audio/video and automatically cache file_id:

```python
class MediaWindow(TelegramWindow):
    text: str = "Here is your file"
    photo: str = "/path/to/image.png"

# First send uploads, next times re-uses file_id!
await MediaWindow(event=msg).answer_photo()
```

## 🛠️ Advanced Usage
- **format_buttons(kwargs): Format all buttons and callback_data with dynamic values.**

- **edit_text(), edit_reply_markup(), edit_media(): Fully supported for CallbackQuery events.**

- **@cache: Decorator for auto file_id management (for InputFile uploads).**

- **Easily extend for your own forms (see /models/text.py, /models/files.py).**

## 📚 Documentation

**Full API Reference**

**Examples**

**Pydantic models**

**aiogram docs**

## ⚡️ Why simple_aiogram?
- **Cut boilerplate and repetitive keyboard code.**

- **Add message logic as Python classes — not spaghetti handlers.**

- **Maximum type safety and flexibility.**

License

MIT License.

Author: belyankiss

Contributions and stars welcome!
