import asyncio
from pathlib import Path

from config import VIDEO_PATH


class StreamManager:

    def __init__(self):
        self.running = False
        self.target_user_id: int | None = None
        self.video_task: asyncio.Task | None = None

    async def start(self, user_id: int):

        if self.running:
            return {
                "success": False,
                "message": "A stream is already running."
            }

        video = Path(VIDEO_PATH)

        if not video.exists():
            return {
                "success": False,
                "message": f"Video not found: {video}"
            }

        self.target_user_id = user_id
        self.running = True

        self.video_task = asyncio.create_task(
            self._run_video()
        )

        return {
            "success": True,
            "message": f"Stream started for {user_id}"
        }

    async def stop(self):

        if not self.running:
            return {
                "success": False,
                "message": "No active stream."
            }

        self.running = False

        if self.video_task:
            self.video_task.cancel()

            try:
                await self.video_task
            except asyncio.CancelledError:
                pass

            self.video_task = None

        self.target_user_id = None

        # TODO:
        # Tell Telegram VoIP layer to terminate the call.

        return {
            "success": True,
            "message": "Stream stopped."
        }

    async def _run_video(self):

        try:
            # TODO:
            #
            # 1. Establish Telegram 1-to-1 video call
            # 2. Start Telegram VoIP media transport
            # 3. Decode video.mp4
            # 4. Send decoded frames as video packets
            # 5. Detect EOF
            # 6. Automatically terminate the call
            #
            # This cannot be implemented by Telethon alone.

            while self.running:
                await asyncio.sleep(1)

                # Placeholder until the Telegram
                # VoIP media implementation is connected.

        except asyncio.CancelledError:
            raise

        finally:
            self.running = False