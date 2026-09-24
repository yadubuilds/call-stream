
import os

from dotenv import load_dotenv


load_dotenv()


def required(
    name: str,
) -> str:

    value = os.getenv(name)

    if not value:

        raise RuntimeError(
            f"Missing environment variable: {name}"
        )

    return value


API_ID = int(
    required("TELEGRAM_API_ID")
)

API_HASH = required(
    "TELEGRAM_API_HASH"
)

SESSION_NAME = os.getenv(
    "SESSION_NAME",
    "sessions/streamer",
)

VIDEO_PATH = os.getenv(
    "VIDEO_PATH",
    "video/video.MOV",
)

