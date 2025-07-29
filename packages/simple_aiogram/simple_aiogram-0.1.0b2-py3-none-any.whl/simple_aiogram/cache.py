from functools import wraps
from aiogram.types import Message
from .models.text import TextForms

FILE_CACHE = {}

def use_cache(file_path: str, file_id: str = None) -> str | None:
    """
    Get file_id from cache by file_path, or set file_id if provided.
    """
    if file_id:
        FILE_CACHE[file_path] = file_id
    return FILE_CACHE.get(file_path)

def _get_field(self: TextForms) -> str | None:
    """
    Return a unique field key in format '<type>:<path>', e.g. 'photo:path/to/img.jpg'
    """
    if self.photo:
        return f"photo:{self.photo}"
    elif self.file:
        return f"document:{self.file}"
    elif self.video:
        return f"video:{self.video}"
    elif self.animation:
        return f"animation:{self.animation}"
    elif self.audio:
        return f"audio:{self.audio}"
    return None

def _save_in_cache(file_name: str, self: TextForms, result: Message):
    """
    Save sent file's file_id to cache, using file_name as key.
    """
    file_id = None
    if self.photo and getattr(result, "photo", None):
        file_id = result.photo[0].file_id
    elif self.file and getattr(result, "document", None):
        file_id = result.document.file_id
    elif self.video and getattr(result, "video", None):
        file_id = result.video.file_id
    elif self.animation and (getattr(result, "animation", None) or getattr(result, "video", None)):
        if result.animation:
            file_id = result.animation.file_id
        else:
            file_id = result.video.file_id
    elif self.audio and getattr(result, "audio", None):
        file_id = result.audio.file_id
    if file_id:
        use_cache(file_name, file_id)

def cache(func):
    """
    Async decorator for caching file_id/photo_id from Telegram for uploads.
    """
    @wraps(func)
    async def wrapper(self: TextForms, *args, **kwargs):
        file_name = _get_field(self)
        if not file_name:
            raise AttributeError(f"{func.__name__} missing required file or photo attribute")
        file_id = use_cache(file_name)
        key, value = file_name.split(":", 1)
        if file_id:
            kwargs[key] = file_id
        else:
            kwargs[key] = await self.format_file(value)
        result = await func(self, *args, **kwargs)
        _save_in_cache(file_name, self, result)
        return result
    return wrapper
