"""
simple_aiogram/core/bot.py

Minimalistic but powerful wrapper for aiogram3, for quick project bootstrap.
Author: belyankiss
License: MIT
"""

import asyncio
import sys
import logging

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties

__all__ = ["BotModel"]

class BotModel:
    """
    Main bootstrap class for aiogram-based bots.

    Features:
        - Safe webhook deletion before polling (for glitch-free bot startup).
        - Built-in logging setup to stdout.
        - Convenient router registration methods.
        - Exposes dispatcher and bot via property.

    Example:
        from simple_aiogram.core.bot import BotModel

        bot = BotModel(token="YOUR_BOT_TOKEN")
        bot.include_router(my_router)
        bot.run()

    Args:
        token (str): Telegram bot token.
        parse_mode (str): Default parse mode for all messages ("HTML", "Markdown", etc.).
        delete_webhook (bool): Delete Telegram webhook before polling.
        is_logging (bool): Enable stdout logging.
        level (int|str): Logging level.
    """

    def __init__(
        self,
        token: str,
        parse_mode: str = "HTML",
        delete_webhook: bool = True,
        is_logging: bool = True,
        level: int | str = logging.INFO
    ):
        self._bot: Bot = Bot(token=token, default=DefaultBotProperties(parse_mode=parse_mode))
        self._dp = Dispatcher()
        self._delete_webhook_ = delete_webhook
        self._is_logging = is_logging
        self._level = level

    async def _delete_webhook(self):
        """
        Delete webhook and drop all pending updates (recommended before polling).
        """
        await self._bot.delete_webhook(drop_pending_updates=True)

    async def _run(self):
        """
        Start polling. If configured, first delete webhook.
        """
        if self._delete_webhook_:
            await self._delete_webhook()
        await self._dp.start_polling(self._bot)

    def _get_logging(self):
        """
        Initialize stdout logging if enabled.
        """
        if self._is_logging:
            logging.basicConfig(level=self._level, stream=sys.stdout)

    @property
    def dispatcher(self) -> Dispatcher:
        """
        Returns the aiogram Dispatcher instance (for advanced customization).
        """
        return self._dp

    @property
    def bot(self) -> Bot:
        """
        Returns the aiogram Bot instance (for direct usage if needed).
        """
        return self._bot

    def include_router(self, router: Router):
        """
        Register a router (aiogram 3.x).
        """
        self._dp.include_router(router)

    def include_routers(self, *routers: Router):
        """
        Register multiple routers at once.
        """
        for r in routers:
            self.include_router(r)

    def run(self):
        """
        Start polling and block. Logging will be configured if enabled.
        """
        self._get_logging()
        try:
            asyncio.run(self._run())
        except KeyboardInterrupt:
            logging.info("Bot stopped!")
            sys.exit(0)
