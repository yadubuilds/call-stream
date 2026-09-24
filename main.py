import asyncio
from pathlib import Path

from telethon import events
from pytgcalls import PyTgCalls

from telegram_client import client
from config import VIDEO_PATH
from call_manager import CallManager


calls = None
call_manager = None


@client.on(
    events.NewMessage(
        pattern=r"^/start_stream(?:\s+(.+))?$"
    )
)
async def start_stream(event):

    if call_manager is None:

        await event.reply(
            "Streamer is not ready."
        )

        return

    user_id_text = (
        event.pattern_match.group(1)
    )

    if not user_id_text:

        await event.reply(
            "Usage:\n\n"
            "/start_stream <telegram_user_id>\n\n"
            "Example:\n"
            "/start_stream 123456789"
        )

        return

    try:

        user_id = int(
            user_id_text.strip()
        )

    except ValueError:

        await event.reply(
            "Telegram user ID must be a number."
        )

        return

    await event.reply(
        "Starting Telegram video call...\n"
        f"Target: {user_id}"
    )

    success, result = (
        await call_manager.start(
            user_id
        )
    )

    await event.reply(result)


@client.on(
    events.NewMessage(
        pattern=r"^/stop_stream$"
    )
)
async def stop_stream(event):

    if call_manager is None:

        await event.reply(
            "Streamer is not ready."
        )

        return

    success, result = (
        await call_manager.stop()
    )

    await event.reply(result)


@client.on(
    events.NewMessage(
        pattern=r"^/stream_status$"
    )
)
async def stream_status(event):

    if call_manager is None:

        await event.reply(
            "Streamer is not ready."
        )

        return

    result = (
        await call_manager.status()
    )

    await event.reply(result)


async def main():

    global calls
    global call_manager

    video = Path(VIDEO_PATH)

    # --------------------------------
    # Validate video
    # --------------------------------

    if not video.exists():

        raise FileNotFoundError(
            "Video file does not exist:\n"
            f"{video.resolve()}"
        )

    if not video.is_file():

        raise ValueError(
            "Video path is not a file:\n"
            f"{video.resolve()}"
        )

    # --------------------------------
    # Application banner
    # --------------------------------

    print()
    print("==============================")
    print(" Telegram Video Streamer")
    print("==============================")
    print()

    print(
        f"Video: {video.resolve()}"
    )

    print()

    # --------------------------------
    # Telegram
    # --------------------------------

    print(
        "Starting Telegram client..."
    )

    await client.start()

    me = await client.get_me()

    print(
        "Logged in as:"
    )

    print(
        f"  Name: {me.first_name}"
    )

    print(
        f"  ID:   {me.id}"
    )

    print()

    # --------------------------------
    # PyTgCalls
    # --------------------------------

    print(
        "Creating PyTgCalls..."
    )

    # IMPORTANT:
    #
    # PyTgCalls must be created inside
    # the same asyncio event loop used by
    # the Telegram client.
    #
    # Therefore it is created here,
    # inside main().
    #

    calls = PyTgCalls(client)

    # IMPORTANT:
    #
    # CallManager now requires the
    # Telethon client so it can resolve
    # Telegram user entities before
    # starting the call.
    #

    call_manager = CallManager(
        calls=calls,
        client=client,
        video_path=VIDEO_PATH,
    )

    print()

    # --------------------------------
    # Start PyTgCalls
    # --------------------------------

    print(
        "Starting PyTgCalls..."
    )

    await calls.start()

    print()
    print("==============================")
    print(" Streamer is ready")
    print("==============================")
    print()

    print("Commands:")
    print()

    print(
        "/start_stream <telegram_user_id>"
    )

    print(
        "/stop_stream"
    )

    print(
        "/stream_status"
    )

    print()

    # --------------------------------
    # Keep application running
    # --------------------------------

    try:

        await client.run_until_disconnected()

    finally:

        print()

        # --------------------------------
        # Stop PyTgCalls
        # --------------------------------

        print(
            "Stopping PyTgCalls..."
        )

        if calls is not None:

            try:

                await calls.stop()

            except Exception as exc:

                print(
                    "PyTgCalls stop error:",
                    repr(exc),
                )

        # --------------------------------
        # Disconnect Telegram
        # --------------------------------

        print(
            "Stopping Telegram client..."
        )

        try:

            await client.disconnect()

        except Exception as exc:

            print(
                "Telegram disconnect error:",
                repr(exc),
            )


# --------------------------------
# Application entry point
# --------------------------------

if __name__ == "__main__":

    asyncio.run(main())