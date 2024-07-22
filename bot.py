import os
import asyncio
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from youtube_search import YoutubeSearch
from pytube import YouTube

# Bot configuration
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

# Create Pyrogram client
app = Client("music-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Create PyTgCalls client
calls = PyTgCalls(app)

# FFmpeg command for converting video to raw audio
FFMPEG_CMD = "ffmpeg -i {} -f s16le -ac 1 -ar 44100 {}"


# YouTube search function
async def search_youtube(query):
    try:
        ys = YoutubeSearch(query, max_results=1)
        video_url = "https://www.youtube.com" + ys.videos[0]["url_suffix"]
        return video_url
    except Exception as e:
        print(f"Error searching for YouTube video: {e}")
        return None


# Bot commands
@app.on_message(filters.command("play"))
async def play(client, message):
    query = message.text.split(" ", 1)[1]
    video_url = await search_youtube(query)
    if video_url is None:
        await message.reply("Video not found!")
        return
    yt = YouTube(video_url)
    audio_file = yt.streams.filter(only_audio=True).first().download()
    output_file = "output.raw"
    try:
        proc = await asyncio.create_subprocess_exec(
            "ffmpeg",
            "-i",
            audio_file,
            "-f",
            "s16le",
            "-ac",
            "1",
            "-ar",
            "44100",
            output_file,
        )
        await proc.wait()
    except Exception as e:
        print(f"Error converting video to raw audio: {e}")
        await message.reply("Error converting video to raw audio!")
        return
    try:
        calls.join_group_call(message.chat.id, output_file)
    except Exception as e:
        print(f"Error joining voice chat: {e}")
        await message.reply("Error joining voice chat!")
        return
    finally:
        os.remove(audio_file)
        os.remove(output_file)


@app.on_message(filters.command("stop"))
async def stop(client, message):
    try:
        calls.leave_group_call(message.chat.id)
    except Exception as e:
        print(f"Error leaving voice chat: {e}")
        await message.reply("Error leaving voice chat!")


# Run the bot
app.run()
