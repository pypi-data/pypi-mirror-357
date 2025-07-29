from datetime import datetime, timedelta
from typing import Any, Optional, Union, Tuple

from aiogram.types import (
    Message, CallbackQuery, MessageEntity, LinkPreviewOptions, ReplyParameters,
    InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply,
    InlineKeyboardButton, InputFile, InputMediaAudio, InputMediaPhoto,
    InputMediaDocument, InputMediaAnimation, InputMediaVideo
)
from aiogram.client.default import Default

from ..cache import cache
from .text import TextForms


class MessageMethods(TextForms):
    """
    Unified interface for sending and editing Telegram messages (text, media, alerts, etc.)
    for both Message and CallbackQuery events.
    """

    event: Union[Message, CallbackQuery]
    show_alert: bool = False

    def _get_event(self) -> Message:
        """
        Internal: always return Message for sending/editing, regardless of event type.
        """
        if isinstance(self.event, CallbackQuery):
            return self.event.message
        return self.event

    async def answer(self,
                     text: str = None,
                     parse_mode: str | Default | None = Default("parse_mode"),
                     entities: list[MessageEntity] | None = None,
                     link_preview_options: LinkPreviewOptions | Default | None = Default("link_preview"),
                     disable_notification: bool | None = None,
                     protect_content: bool | Default | None = Default("protect_content"),
                     allow_paid_broadcast: bool | None = None,
                     message_effect_id: str | None = None,
                     reply_parameters: ReplyParameters | None = None,
                     reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply | None = None,
                     allow_sending_without_reply: bool | None = None,
                     disable_web_page_preview: bool | Default | None = Default("link_preview_is_disabled"),
                     reply_to_message_id: int | None = None,
                     url: str | None = None,
                     cache_time: int | None = None,
                     **kwargs: Any) -> Message:
        """
        Send a text answer or alert, depending on show_alert.
        All formatting variables in text and self.text are substituted from kwargs.

        Args:
            text: Optional text to send (otherwise self.text is used).
            ... (all other Telegram message args)
            **kwargs: Variables for formatting in text/self.text.

        Returns:
            Message: Result of sending the answer.
            :param text: Text of the message to be sent, 1-4096 characters after entities parsing
            :param parse_mode: Mode for parsing entities in the message text. See `formatting options <https://core.telegram.org/bots/api#formatting-options>`_ for more details.
            :param entities: A JSON-serialized list of special entities that appear in message text, which can be specified instead of *parse_mode*
            :param link_preview_options: Link preview generation options for the message
            :param disable_notification: Sends the message `silently <https://telegram.org/blog/channels-2-0#silent-messages>`_. Users will receive a notification with no sound.
            :param protect_content: Protects the contents of the sent message from forwarding and saving
            :param allow_paid_broadcast: Pass :code:`True` to allow up to 1000 messages per second, ignoring `broadcasting limits <https://core.telegram.org/bots/faq#how-can-i-message-all-of-my-bot-39s-subscribers-at-once>`_ for a fee of 0.1 Telegram Stars per message. The relevant Stars will be withdrawn from the bot's balance
            :param message_effect_id: Unique identifier of the message effect to be added to the message; for private chats only
            :param reply_parameters: Description of the message to reply to
            :param reply_markup: Additional interface options. A JSON-serialized object for an `inline keyboard <https://core.telegram.org/bots/features#inline-keyboards>`_, `custom reply keyboard <https://core.telegram.org/bots/features#keyboards>`_, instructions to remove a reply keyboard or to force a reply from the user
            :param allow_sending_without_reply: Pass :code:`True` if the message should be sent even if the specified replied-to message is not found
            :param disable_web_page_preview: Disables link previews for links in this message
            :param reply_to_message_id: If the message is a reply, ID of the original message
            :param url: Optional URL for redirection.
            :param cache_time: Cache duration for alert.
            :return: instance of method :class:`aiogram.models.send_message.SendMessage`

        """
        if self.show_alert:
            return await self.alert(
                text=text if text is not None else self.text.format_map(kwargs),
                show_alert=self.show_alert,
                url=url,
                cache_time=cache_time,
                **kwargs
            )
        event = self._get_event()
        return await event.answer(
            text=text if text is not None else self.text.format_map(kwargs),
            parse_mode=parse_mode,
            entities=entities,
            link_preview_options=link_preview_options,
            disable_notification=disable_notification,
            protect_content=protect_content,
            allow_paid_broadcast=allow_paid_broadcast,
            message_effect_id=message_effect_id,
            reply_parameters=reply_parameters,
            reply_markup=reply_markup if reply_markup else self.reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            disable_web_page_preview=disable_web_page_preview,
            reply_to_message_id=reply_to_message_id,
            **kwargs
        )

    async def reply(
            self,
            text: Optional[str] = None,
            parse_mode: str | Default | None = Default("parse_mode"),
            entities: list[MessageEntity] | None = None,
            link_preview_options: LinkPreviewOptions | Default | None = Default(
                "link_preview"
            ),
            disable_notification: bool | None = None,
            protect_content: bool | Default | None = Default("protect_content"),
            allow_paid_broadcast: bool | None = None,
            message_effect_id: str | None = None,
            reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply | None = None,
            allow_sending_without_reply: bool | None = None,
            disable_web_page_preview: bool | Default | None = Default(
                "link_preview_is_disabled"
            ),
            **kwargs: Any
    ) -> Message:
        """
        Reply message
        """
        event = self._get_event()
        return await event.reply(
            text=text if text else self.text.format_map(kwargs),
            parse_mode=parse_mode,
            entities=entities,
            link_preview_options=link_preview_options,
            disable_notification=disable_notification,
            protect_content=protect_content,
            allow_paid_broadcast=allow_paid_broadcast,
            message_effect_id=message_effect_id,
            reply_markup=reply_markup if reply_markup else self.reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            disable_web_page_preview=disable_web_page_preview,
            **kwargs
        )

    @cache
    async def answer_photo(self,
            photo: str | InputFile,
            caption: str | None = None,
            parse_mode: str | Default | None = Default("parse_mode"),
            caption_entities: list[MessageEntity] | None = None,
            show_caption_above_media: bool | Default | None = Default("show_caption_above_media"),
            has_spoiler: bool | None = None,
            disable_notification: bool | None = None,
            protect_content: bool | Default | None = Default("protect_content"),
            allow_paid_broadcast: bool | None = None,
            message_effect_id: str | None = None,
            reply_parameters: ReplyParameters | None = None,
            reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply | None = None,
            allow_sending_without_reply: bool | None = None,
            reply_to_message_id: int | None = None,
            **kwargs: Any) -> Message:
        """
        Send a photo message.
        """
        event = self._get_event()
        return await event.answer_photo(
            photo=photo,
            caption=caption if caption else self.text.format_map(kwargs),
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            show_caption_above_media=show_caption_above_media,
            has_spoiler=has_spoiler,
            disable_notification=disable_notification,
            protect_content=protect_content,
            allow_paid_broadcast=allow_paid_broadcast,
            message_effect_id=message_effect_id,
            reply_parameters=reply_parameters,
            reply_markup=reply_markup if reply_markup else self.reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_to_message_id=reply_to_message_id,
            **kwargs
        )

    @cache
    async def reply_photo(
            self,
            photo: str | InputFile,
            caption: str | None = None,
            parse_mode: str | Default | None = Default("parse_mode"),
            caption_entities: list[MessageEntity] | None = None,
            show_caption_above_media: bool | Default | None = Default(
                "show_caption_above_media"
            ),
            has_spoiler: bool | None = None,
            disable_notification: bool | None = None,
            protect_content: bool | Default | None = Default("protect_content"),
            allow_paid_broadcast: bool | None = None,
            message_effect_id: str | None = None,
            reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply | None = None,
            allow_sending_without_reply: bool | None = None,
            **kwargs: Any
    ) -> Message:
        """
                Send a photo message.
                """
        event = self._get_event()
        return await event.reply_photo(
            photo=photo,
            caption=caption if caption else self.text.format_map(kwargs),
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            show_caption_above_media=show_caption_above_media,
            has_spoiler=has_spoiler,
            disable_notification=disable_notification,
            protect_content=protect_content,
            allow_paid_broadcast=allow_paid_broadcast,
            message_effect_id=message_effect_id,
            reply_markup=reply_markup if reply_markup else self.reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            **kwargs
        )

    @cache
    async def answer_document(self,
            document: Union[str, InputFile, None] = None,
            thumbnail: InputFile | None = None,
            caption: str | None = None,
            parse_mode: str | Default | None = Default("parse_mode"),
            caption_entities: list[MessageEntity] | None = None,
            disable_content_type_detection: bool | None = None,
            disable_notification: bool | None = None,
            protect_content: bool | Default | None = Default("protect_content"),
            allow_paid_broadcast: bool | None = None,
            message_effect_id: str | None = None,
            reply_parameters: ReplyParameters | None = None,
            reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply | None = None,
            allow_sending_without_reply: bool | None = None,
            reply_to_message_id: int | None = None,
            **kwargs: Any) -> Message:
        """
        Send a document message.
        """
        event = self._get_event()
        return await event.answer_document(
            document=document,
            thumbnail=thumbnail,
            caption=caption if caption else self.text.format_map(kwargs),
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            disable_content_type_detection=disable_content_type_detection,
            disable_notification=disable_notification,
            protect_content=protect_content,
            allow_paid_broadcast=allow_paid_broadcast,
            message_effect_id=message_effect_id,
            reply_parameters=reply_parameters,
            reply_markup=reply_markup if reply_markup  else self.reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_to_message_id=reply_to_message_id,
            **kwargs
        )

    @cache
    async def reply_document(
            self,
            document: str | InputFile,
            thumbnail: InputFile | None = None,
            caption: str | None = None,
            parse_mode: str | Default | None = Default("parse_mode"),
            caption_entities: list[MessageEntity] | None = None,
            disable_content_type_detection: bool | None = None,
            disable_notification: bool | None = None,
            protect_content: bool | Default | None = Default("protect_content"),
            allow_paid_broadcast: bool | None = None,
            message_effect_id: str | None = None,
            reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply | None = None,
            allow_sending_without_reply: bool | None = None,
            **kwargs: Any
    ) -> Message:
        """
                Send a document message.
                """
        event = self._get_event()
        return await event.reply_document(
            document=document,
            thumbnail=thumbnail,
            caption=caption if caption else self.text.format_map(kwargs),
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            disable_content_type_detection=disable_content_type_detection,
            disable_notification=disable_notification,
            protect_content=protect_content,
            allow_paid_broadcast=allow_paid_broadcast,
            message_effect_id=message_effect_id,
            reply_markup=reply_markup if reply_markup else self.reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            **kwargs
        )

    @cache
    async def answer_animation(self,
            animation: str | InputFile,
            duration: int | None = None,
            width: int | None = None,
            height: int | None = None,
            thumbnail: InputFile | None = None,
            caption: str | None = None,
            parse_mode: str | Default | None = Default("parse_mode"),
            caption_entities: list[MessageEntity] | None = None,
            show_caption_above_media: bool | Default | None = Default("show_caption_above_media"),
            has_spoiler: bool | None = None,
            disable_notification: bool | None = None,
            protect_content: bool | Default | None = Default("protect_content"),
            allow_paid_broadcast: bool | None = None,
            message_effect_id: str | None = None,
            reply_parameters: ReplyParameters | None = None,
            reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply | None = None,
            allow_sending_without_reply: bool | None = None,
            reply_to_message_id: int | None = None,
            **kwargs: Any) -> Message:
        """
        Send an animation (GIF) message.
        """
        event = self._get_event()
        return await event.answer_animation(
            animation=animation,
            duration=duration,
            width=width,
            height=height,
            thumbnail=thumbnail,
            caption=caption if caption else self.text.format_map(kwargs),
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            show_caption_above_media=show_caption_above_media,
            has_spoiler=has_spoiler,
            disable_notification=disable_notification,
            protect_content=protect_content,
            allow_paid_broadcast=allow_paid_broadcast,
            message_effect_id=message_effect_id,
            reply_parameters=reply_parameters,
            reply_markup=reply_markup if reply_markup else self.reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_to_message_id=reply_to_message_id,
            **kwargs
        )

    @cache
    async def reply_animation(
            self,
            animation: str | InputFile,
            duration: int | None = None,
            width: int | None = None,
            height: int | None = None,
            thumbnail: InputFile | None = None,
            caption: str | None = None,
            parse_mode: str | Default | None = Default("parse_mode"),
            caption_entities: list[MessageEntity] | None = None,
            show_caption_above_media: bool | Default | None = Default(
                "show_caption_above_media"
            ),
            has_spoiler: bool | None = None,
            disable_notification: bool | None = None,
            protect_content: bool | Default | None = Default("protect_content"),
            allow_paid_broadcast: bool | None = None,
            message_effect_id: str | None = None,
            reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply | None = None,
            allow_sending_without_reply: bool | None = None,
            **kwargs: Any
    ) -> Message:
        """
                Send an animation (GIF) message.
                """
        event = self._get_event()
        return await event.reply_animation(
            animation=animation,
            duration=duration,
            width=width,
            height=height,
            thumbnail=thumbnail,
            caption=caption if caption else self.text.format_map(kwargs),
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            show_caption_above_media=show_caption_above_media,
            has_spoiler=has_spoiler,
            disable_notification=disable_notification,
            protect_content=protect_content,
            allow_paid_broadcast=allow_paid_broadcast,
            message_effect_id=message_effect_id,
            reply_markup=reply_markup if reply_markup else self.reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            **kwargs
        )

    @cache
    async def answer_video(self,
            video: str | InputFile,
            duration: int | None = None,
            width: int | None = None,
            height: int | None = None,
            thumbnail: InputFile | None = None,
            cover: str | InputFile | None = None,
            start_timestamp: datetime | timedelta | int | None = None,
            caption: str | None = None,
            parse_mode: str | Default | None = Default("parse_mode"),
            caption_entities: list[MessageEntity] | None = None,
            show_caption_above_media: bool | Default | None = Default("show_caption_above_media"),
            has_spoiler: bool | None = None,
            supports_streaming: bool | None = None,
            disable_notification: bool | None = None,
            protect_content: bool | Default | None = Default("protect_content"),
            allow_paid_broadcast: bool | None = None,
            message_effect_id: str | None = None,
            reply_parameters: ReplyParameters | None = None,
            reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply | None = None,
            allow_sending_without_reply: bool | None = None,
            reply_to_message_id: int | None = None,
            **kwargs: Any) -> Message:
        """
        Send a video message.
        """
        event = self._get_event()
        return await event.answer_video(
            video=video,
            duration=duration,
            width=width,
            height=height,
            thumbnail=thumbnail,
            cover=cover,
            start_timestamp=start_timestamp,
            caption=caption if caption else self.text.format_map(kwargs),
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            show_caption_above_media=show_caption_above_media,
            has_spoiler=has_spoiler,
            supports_streaming=supports_streaming,
            disable_notification=disable_notification,
            protect_content=protect_content,
            allow_paid_broadcast=allow_paid_broadcast,
            message_effect_id=message_effect_id,
            reply_parameters=reply_parameters,
            reply_markup=reply_markup if reply_markup else self.reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_to_message_id=reply_to_message_id,
            **kwargs
        )

    @cache
    async def reply_video(
            self,
            video: str | InputFile,
            duration: int | None = None,
            width: int | None = None,
            height: int | None = None,
            thumbnail: InputFile | None = None,
            cover: str | InputFile | None = None,
            start_timestamp: datetime | timedelta | int | None = None,
            caption: str | None = None,
            parse_mode: str | Default | None = Default("parse_mode"),
            caption_entities: list[MessageEntity] | None = None,
            show_caption_above_media: bool | Default | None = Default(
                "show_caption_above_media"
            ),
            has_spoiler: bool | None = None,
            supports_streaming: bool | None = None,
            disable_notification: bool | None = None,
            protect_content: bool | Default | None = Default("protect_content"),
            allow_paid_broadcast: bool | None = None,
            message_effect_id: str | None = None,
            reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply | None = None,
            allow_sending_without_reply: bool | None = None,
            **kwargs: Any
    ) -> Message:
        """
                Send a video message.
                """
        event = self._get_event()
        return await event.reply_video(
            video=video,
            duration=duration,
            width=width,
            height=height,
            thumbnail=thumbnail,
            cover=cover,
            start_timestamp=start_timestamp,
            caption=caption if caption else self.text.format_map(kwargs),
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            show_caption_above_media=show_caption_above_media,
            has_spoiler=has_spoiler,
            supports_streaming=supports_streaming,
            disable_notification=disable_notification,
            protect_content=protect_content,
            allow_paid_broadcast=allow_paid_broadcast,
            message_effect_id=message_effect_id,
            reply_markup=reply_markup if reply_markup else self.reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            **kwargs
        )

    @cache
    async def answer_audio(
            self,
            audio: str | InputFile,
            caption: str | None = None,
            parse_mode: str | Default | None = Default("parse_mode"),
            caption_entities: list[MessageEntity] | None = None,
            duration: int | None = None,
            performer: str | None = None,
            title: str | None = None,
            thumbnail: InputFile | None = None,
            disable_notification: bool | None = None,
            protect_content: bool | Default | None = Default("protect_content"),
            allow_paid_broadcast: bool | None = None,
            message_effect_id: str | None = None,
            reply_parameters: ReplyParameters | None = None,
            reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply | None = None,
            allow_sending_without_reply: bool | None = None,
            reply_to_message_id: int | None = None,
            **kwargs: Any
    ) -> Message:
        """
                Send an audio file as an answer.
                """
        event = self._get_event()
        return await event.answer_audio(
            audio=audio,
            caption=caption if caption else self.text.format_map(kwargs),
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            duration=duration,
            performer=performer,
            title=title,
            thumbnail=thumbnail,
            disable_notification=disable_notification,
            protect_content=protect_content,
            allow_paid_broadcast=allow_paid_broadcast,
            message_effect_id=message_effect_id,
            reply_parameters=reply_parameters,
            reply_markup=reply_markup if reply_markup else self.reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_to_message_id=reply_to_message_id,
            **kwargs
        )

    @cache
    async def reply_audio(
            self,
            audio: str | InputFile,
            caption: str | None = None,
            parse_mode: str | Default | None = Default("parse_mode"),
            caption_entities: list[MessageEntity] | None = None,
            duration: int | None = None,
            performer: str | None = None,
            title: str | None = None,
            thumbnail: InputFile | None = None,
            disable_notification: bool | None = None,
            protect_content: bool | Default | None = Default("protect_content"),
            allow_paid_broadcast: bool | None = None,
            message_effect_id: str | None = None,
            reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply | None = None,
            allow_sending_without_reply: bool | None = None,
            **kwargs: Any
    ) -> Message:
        """
                Send an audio file as an answer.
                """
        event = self._get_event()
        return await event.reply_audio(
            audio=audio,
            caption=caption if caption else self.text.format_map(kwargs),
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            duration=duration,
            performer=performer,
            title=title,
            thumbnail=thumbnail,
            disable_notification=disable_notification,
            protect_content=protect_content,
            allow_paid_broadcast=allow_paid_broadcast,
            message_effect_id=message_effect_id,
            reply_markup=reply_markup if reply_markup else self.reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            **kwargs
        )

    async def answer_dice(
            self,
            emoji: str | None = None,
            disable_notification: bool | None = None,
            protect_content: bool | Default | None = Default("protect_content"),
            allow_paid_broadcast: bool | None = None,
            message_effect_id: str | None = None,
            reply_parameters: ReplyParameters | None = None,
            reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply | None = None,
            allow_sending_without_reply: bool | None = None,
            reply_to_message_id: int | None = None,
            **kwargs: Any
    ) -> Message:
        """
                Send a dice emoji as an answer (🎲, 🎯, 🏀, etc).
        """
        event = self._get_event()
        return await event.answer_dice(
            emoji=emoji if emoji else self.text,
            disable_notification=disable_notification,
            protect_content=protect_content,
            allow_paid_broadcast=allow_paid_broadcast,
            message_effect_id=message_effect_id,
            reply_parameters=reply_parameters,
            reply_markup=reply_markup if reply_markup else self.reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_to_message_id=reply_to_message_id,
            **kwargs
        )

    async def reply_dice(
            self,
            emoji: str | None = None,
            disable_notification: bool | None = None,
            protect_content: bool | Default | None = Default("protect_content"),
            allow_paid_broadcast: bool | None = None,
            message_effect_id: str | None = None,
            reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply | None = None,
            allow_sending_without_reply: bool | None = None,
            **kwargs: Any
    ) -> Message:
        """
                Send a dice emoji as an answer (🎲, 🎯, 🏀, etc).
        """
        event = self._get_event()
        return await event.reply_dice(
            emoji=emoji if emoji else self.text,
            disable_notification=disable_notification,
            protect_content=protect_content,
            allow_paid_broadcast=allow_paid_broadcast,
            message_effect_id=message_effect_id,
            reply_markup=reply_markup if reply_markup else self.reply_markup,
            allow_sending_without_reply=allow_sending_without_reply,
            **kwargs
        )

    async def alert(self,
            text: str | None = None,
            show_alert: bool | None = None,
            url: str | None = None,
            cache_time: int | None = None,
            **kwargs: Any) -> Message:
        """
        Show an alert popup for CallbackQuery (or notification if show_alert=False).

        Args:
            text: Alert message.
            show_alert: Whether to show as popup (True) or as notification (False).
            url: Optional URL for redirection.
            cache_time: Cache duration for alert.
            **kwargs: Formatting variables.

        Returns:
            Message: Result of alert answer.
        """
        return await self.event.answer(
            text=text if text is not None else self.text.format_map(kwargs),
            show_alert=show_alert,
            url=url,
            cache_time=cache_time,
            **kwargs
        )

    async def edit_text(self,
            text: Optional[str] = None,
            inline_message_id: str | None = None,
            parse_mode: str | Default | None = Default("parse_mode"),
            entities: list[MessageEntity] | None = None,
            link_preview_options: LinkPreviewOptions | Default | None = Default("link_preview"),
            reply_markup: InlineKeyboardMarkup | None = None,
            disable_web_page_preview: bool | Default | None = Default("link_preview_is_disabled"),
            **kwargs: Any) -> Message:
        """
        Edit the text of a sent message (for CallbackQuery events only).
        """
        if isinstance(self.event, Message):
            raise AttributeError(f"edit_text must be used only with CallbackQuery events")
        event = self._get_event()
        return await event.edit_text(
            text=text if text is not None else self.text.format_map(kwargs),
            inline_message_id=inline_message_id,
            parse_mode=parse_mode,
            entities=entities,
            link_preview_options=link_preview_options,
            reply_markup=reply_markup if reply_markup else self.reply_markup,
            disable_web_page_preview=disable_web_page_preview,
            **kwargs
        )

    async def edit_caption(self,
            inline_message_id: str | None = None,
            caption: str | None = None,
            parse_mode: str | Default | None = Default("parse_mode"),
            caption_entities: list[MessageEntity] | None = None,
            show_caption_above_media: bool | Default | None = Default("show_caption_above_media"),
            reply_markup: InlineKeyboardMarkup | None = None,
            **kwargs: Any) -> Message:
        """
        Edit the caption of a sent media message.
        """
        if isinstance(self.event, Message):
            raise AttributeError(f"edit_caption must be used only with CallbackQuery events")
        event = self._get_event()
        return await event.edit_caption(
            inline_message_id=inline_message_id,
            caption=caption if caption else self.text.format_map(kwargs),
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            show_caption_above_media=show_caption_above_media,
            reply_markup=reply_markup if reply_markup else self.reply_markup,
            **kwargs
        )

    async def edit_reply_markup(self,
            *inline_buttons: InlineKeyboardButton,
            sizes: Tuple[int] = (1,),
            repeat: bool = False,
            inline_message_id: str | None = None,
            reply_markup: InlineKeyboardMarkup | None = None,
            **kwargs: Any) -> Message:
        """
        Edit only the reply_markup (keyboard) of a sent message.
        You can pass new buttons directly as *inline_buttons, or provide reply_markup.
        """
        if isinstance(self.event, Message):
            raise AttributeError(f"edit_reply_markup must be used only with CallbackQuery events")
        event = self._get_event()
        return await event.edit_reply_markup(
            inline_message_id=inline_message_id,
            reply_markup=reply_markup if reply_markup else self._build_keyboard(*inline_buttons, sizes=sizes, repeat=repeat),
            **kwargs
        )

    async def edit_media(self,
            media: InputMediaAnimation | InputMediaDocument | InputMediaAudio | InputMediaPhoto | InputMediaVideo,
            inline_message_id: str | None = None,
            reply_markup: InlineKeyboardMarkup | None = None,
            **kwargs: Any) -> Message:
        """
        Edit the media content of a sent message.
        """
        if isinstance(self.event, Message):
            raise AttributeError(f"edit_media must be used only with CallbackQuery events")
        event = self._get_event()
        return await event.edit_media(
            media=media,
            inline_message_id=inline_message_id,
            reply_markup=reply_markup if reply_markup else self.reply_markup,
            **kwargs
        )


