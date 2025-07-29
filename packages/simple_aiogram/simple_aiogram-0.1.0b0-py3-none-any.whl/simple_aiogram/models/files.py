from pathlib import Path
from typing import Optional, Union

from aiogram.types import BufferedInputFile
from pydantic import BaseModel
import aiofiles


class FileForm(BaseModel):
    """
    Universal pydantic model for handling file paths for different media types.

    Attributes:
        file: Optional path to a file (document).
        photo: Optional path to a photo.
        video: Optional path to a video file.
        animation: Optional path to an animation file.
        audio: Optional path to an audio file.
    """

    file: Optional[str] = None
    photo: Optional[str] = None
    video: Optional[str] = None
    animation: Optional[str] = None
    audio: Optional[str] = None

    @staticmethod
    async def format_file(path_file: Optional[str]) -> Union[BufferedInputFile, str, None]:
        """
        Reads a file asynchronously and returns it as BufferedInputFile for aiogram,
        or the original string path if the file is not found.

        Args:
            path_file: The file system path to the file.

        Returns:
            BufferedInputFile: if the file exists and was read successfully.
            str: original path if the file does not exist (possibly already file_id).
            None: if path_file is None.
        """
        if path_file is None:
            return None
        try:
            async with aiofiles.open(path_file, mode="rb") as file:
                filename = Path(path_file).name
                return BufferedInputFile(file=await file.read(), filename=filename)
        except FileNotFoundError:
            # If file is not found, return the original path (maybe it's a Telegram file_id)
            return path_file
