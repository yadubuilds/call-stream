import asyncio
import subprocess
from pathlib import Path
from typing import Optional

from telethon import TelegramClient
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from pytgcalls.types.raw import VideoParameters


# --------------------------------------------
# Phone-size stream settings
# --------------------------------------------

PHONE_WIDTH = 1080
PHONE_HEIGHT = 1920
PHONE_FPS = 30


def _ensure_portrait_video(source_path: Path) -> Path:

    portrait_path = source_path.with_name(
        f"{source_path.stem}_portrait{source_path.suffix}",
    )

    if portrait_path.exists():
        return portrait_path

    print(
        "[STREAM] Source is not portrait yet, "
        "converting once with ffmpeg..."
    )

    vf = (
        f"scale={PHONE_WIDTH}:{PHONE_HEIGHT}:"
        "force_original_aspect_ratio=decrease,"
        f"pad={PHONE_WIDTH}:{PHONE_HEIGHT}:"
        "(ow-iw)/2:(oh-ih)/2:color=black"
    )

    result = subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(source_path),
            "-vf",
            vf,
            "-r",
            str(PHONE_FPS),
            "-c:a",
            "copy",
            str(portrait_path),
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:

        print(
            "[STREAM] ffmpeg conversion failed:"
        )

        print(
            result.stderr[-1500:]
        )

        raise RuntimeError(
            "Failed to convert video to portrait. "
            "Is ffmpeg installed and on PATH?"
        )

    print(
        f"[STREAM] Portrait video ready: "
        f"{portrait_path}"
    )

    return portrait_path


class CallManager:

    def __init__(
        self,
        calls: PyTgCalls,
        client: TelegramClient,
        video_path: str,
    ):

        self.calls = calls
        self.client = client
        self.video_path = Path(video_path)

        self.running = False
        self.target_user_id: Optional[int] = None

        self._lock = asyncio.Lock()

    # ========================================================
    # START
    # ========================================================

    async def start(
        self,
        user_id: int,
    ) -> tuple[bool, str]:

        async with self._lock:

            # --------------------------------------------
            # Check existing call
            # --------------------------------------------

            if self.running:

                return (
                    False,
                    "A video call is already active.\n"
                    f"Target: {self.target_user_id}",
                )

            # --------------------------------------------
            # Check video
            # --------------------------------------------

            if not self.video_path.exists():

                return (
                    False,
                    "Video file not found:\n"
                    f"{self.video_path.resolve()}",
                )

            if not self.video_path.is_file():

                return (
                    False,
                    "Video path is not a file:\n"
                    f"{self.video_path.resolve()}",
                )

            print()

            print(
                "=============================="
            )

            print(
                "[STREAM] Starting P2P call"
            )

            print(
                "=============================="
            )

            print(
                f"[STREAM] Target: {user_id}"
            )

            print(
                f"[STREAM] Video: "
                f"{self.video_path.resolve()}"
            )

            try:

                # ==================================================
                # Resolve Telegram user
                # ==================================================

                print()

                print(
                    f"[STREAM] Resolving Telegram user "
                    f"{user_id}..."
                )

                try:

                    entity = await self.client.get_entity(
                        user_id
                    )

                except ValueError:

                    print(
                        "[STREAM] User is not in the "
                        "current entity cache."
                    )

                    print(
                        "[STREAM] Loading Telegram dialogs..."
                    )

                    await self.client.get_dialogs(
                        limit=None
                    )

                    entity = await self.client.get_entity(
                        user_id
                    )

                # --------------------------------------------------
                # Verify entity
                # --------------------------------------------------

                print()

                print(
                    "[STREAM] Telegram user resolved."
                )

                print(
                    f"[STREAM] Entity ID: "
                    f"{entity.id}"
                )

                first_name = (
                    getattr(
                        entity,
                        "first_name",
                        None,
                    )
                    or ""
                )

                last_name = (
                    getattr(
                        entity,
                        "last_name",
                        None,
                    )
                    or ""
                )

                username = (
                    getattr(
                        entity,
                        "username",
                        None,
                    )
                )

                name = (
                    f"{first_name} "
                    f"{last_name}"
                ).strip()

                if name:

                    print(
                        f"[STREAM] Name: {name}"
                    )

                if username:

                    print(
                        f"[STREAM] Username: "
                        f"@{username}"
                    )

                # ==================================================
                # Create portrait video
                # ==================================================

                portrait_video_path = (
                    _ensure_portrait_video(
                        self.video_path
                    )
                )

                # ==================================================
                # Create MediaStream
                # ==================================================

                stream = MediaStream(

                    media_path=portrait_video_path,

                    video_parameters=VideoParameters(
                        width=PHONE_WIDTH,
                        height=PHONE_HEIGHT,
                        frame_rate=PHONE_FPS,
                    ),
                )

                print()

                print(
                    "[STREAM] Video profile:"
                )

                print(
                    f"  Resolution: "
                    f"{PHONE_WIDTH}x{PHONE_HEIGHT}"
                )

                print(
                    f"  FPS: "
                    f"{PHONE_FPS}"
                )

                print(
                    "  Aspect ratio: "
                    "9:16 (phone)"
                )

                # ==================================================
                # Start call
                # ==================================================

                print()

                print(
                    f"[STREAM] Calling "
                    f"{entity.id}..."
                )

                # IMPORTANT:
                #
                # Telethon returns a User object.
                #
                # PyTgCalls play() expects:
                #
                #     int
                #     or
                #     str
                #
                # Therefore pass entity.id.
                #

                target_chat_id = entity.id

                await self.calls.play(
                    target_chat_id,
                    stream,
                )

                # ==================================================
                # Call connected
                # ==================================================

                self.running = True

                self.target_user_id = entity.id

                print()

                print(
                    "[STREAM] Call connected."
                )

                print(
                    "[STREAM] Video streaming."
                )

                return (
                    True,
                    "Video call connected.\n"
                    f"Target: {entity.id}\n"
                    f"Video: {self.video_path.name}\n"
                    f"Stream: "
                    f"{PHONE_WIDTH}x"
                    f"{PHONE_HEIGHT} @ "
                    f"{PHONE_FPS} FPS",
                )

            # ======================================================
            # Error handling
            # ======================================================

            except Exception as exc:

                self.running = False

                self.target_user_id = None

                print()

                print(
                    "[STREAM] Call failed."
                )

                print(
                    "[STREAM] Error type:",
                    type(exc).__name__,
                )

                print(
                    "[STREAM] Error:",
                    repr(exc),
                )

                return (
                    False,
                    "Failed to establish video call.\n"
                    f"Error: {type(exc).__name__}\n"
                    f"Details: {exc}",
                )

    # ========================================================
    # STOP
    # ========================================================

    async def stop(
        self,
    ) -> tuple[bool, str]:

        async with self._lock:

            if not self.running:

                return (
                    False,
                    "No active video call.",
                )

            target = self.target_user_id

            print()

            print(
                f"[STREAM] Stopping call "
                f"to {target}"
            )

            try:

                if target is not None:

                    await self.calls.leave_call(
                        target
                    )

                print(
                    "[STREAM] Call disconnected."
                )

            except Exception as exc:

                print(
                    "[STREAM] Leave error:",
                    repr(exc),
                )

            finally:

                self.running = False

                self.target_user_id = None

            return (
                True,
                "Video call stopped.",
            )

    # ========================================================
    # STATUS
    # ========================================================

    async def status(
        self,
    ) -> str:

        if not self.running:

            return (
                "No active video call."
            )

        return (
            "Video call is active.\n"
            f"Target: {self.target_user_id}\n"
            f"Video: {self.video_path.name}\n"
            f"Stream: "
            f"{PHONE_WIDTH}x"
            f"{PHONE_HEIGHT} @ "
            f"{PHONE_FPS} FPS"
        )