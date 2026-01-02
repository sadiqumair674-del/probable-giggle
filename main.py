import os
import json
from io import BytesIO
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
import yt_dlp
import qrcode
import psycopg2

# ------------------ ENVIRONMENT ------------------
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID"))
DATABASE_URL = os.environ.get("DATABASE_URL")

# ------------------ DATABASE CONNECTION ------------------
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# ------------------ CLIENT INIT ------------------
app = Client("AQUA_MUSIC_BOT", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
vc = PyTgCalls(app)

# ------------------ UTILITY FUNCTIONS ------------------
def is_owner(user_id):
    cursor.execute("SELECT * FROM owners WHERE user_id=%s", (user_id,))
    return cursor.fetchone() is not None

def add_owner(user_id, username):
    cursor.execute(
        "INSERT INTO owners (user_id, username) VALUES (%s, %s) ON CONFLICT (user_id) DO NOTHING",
        (user_id, username)
    )
    conn.commit()

# ------------------ /START ------------------
@app.on_message(filters.command("start") & filters.private)
async def start(_, message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("SUPPORT", url="https://t.me/AQUAxMUSIC")],
        [InlineKeyboardButton("UPDATES", url="https://t.me/AQUAxMUSIC_UPDATES")],
        [InlineKeyboardButton("FOUNDER / OWNER", callback_data="owner_info")],
        [InlineKeyboardButton("DM OWNER", url="https://t.me/ENDLES_ERA")]
    ])
    await message.reply_text(
        "❖ ˹ 𝐀𝐐𝐔𝐀 ꭙ 𝐌ᴜsɪᴄ ˼ is online!\n"
        "❖ 24x7 run | Best sound quality | No ads\n"
        "❖ Click on the help button to get info about modules and commands",
        reply_markup=buttons
    )

@app.on_callback_query(filters.regex("owner_info"))
async def owner_info(_, query):
    await query.answer()
    await query.message.edit_text(
        "❖ Name: THEGAMERADEPT\n"
        "❖ Username: @ENDLES_ERA\n"
        "❖ Telegram ID: 6245574035"
    )

# ------------------ /QR ------------------
@app.on_message(filters.command("qr"))
async def qr_gen(_, message):
    if len(message.command) < 2:
        await message.reply_text("Usage: /qr <text or URL>")
        return
    text = " ".join(message.command[1:])
    await message.reply_text("Pʀᴏsᴇsɪɴɢ.. 🪄")
    img = qrcode.make(text)
    bio = BytesIO()
    bio.name = "qr.png"
    img.save(bio, "PNG")
    bio.seek(0)
    await message.reply_photo(photo=bio, caption="Here is your QR code!")

# ------------------ /ID ------------------
@app.on_message(filters.command("id"))
async def show_id(_, message):
    chat = message.chat.id
    user = message.from_user.id
    await message.reply_text(
        f"❖ ᴍᴇssᴀɢᴇ ɪᴅ: {message.id}\n"
        f"❖ ʏᴏᴜʀ ɪᴅ: {user}\n"
        f"❖ ᴄʜᴀᴛ ɪᴅ: {chat}"
    )

# ------------------ MUSIC COMMANDS ------------------
async def download_audio(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'extractaudio': True,
        'audioformat': "mp3",
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        url = info['url']
        title = info.get('title', "Unknown Title")
    return url, title

@app.on_message(filters.command("play") & filters.group)
async def play(_, message):
    if len(message.command) < 2:
        await message.reply_text("Usage: /play <song name or YouTube URL>")
        return
    query = " ".join(message.command[1:])
    await message.reply_text(f"❖ ˹ 𝐀𝐐𝐔𝐀 ꭙ 𝐌ᴜsɪᴄ ˼ is streaming ⏤͟͞●\n❍ Searching...")
    try:
        url, title = await download_audio(query)
        chat_id = message.chat.id
        vc.join_group_call(chat_id, AudioPiped(url))
        # Add to songs table
        cursor.execute(
            "INSERT INTO songs (chat_id, song_title, url, requested_by) VALUES (%s, %s, %s, %s)",
            (chat_id, title, url, message.from_user.id)
        )
        conn.commit()
        await message.reply_text(
            f"❍ ᴛɪᴛʟє ➥ {title}\n"
            f"❍ ʙʏ ➥ {message.from_user.first_name}\n"
            "❖ ϻᴧᴅє ʙʏ ➛ THEGAMERADEPT"
        )
    except Exception as e:
        await message.reply_text(f"Error: {e}")

@app.on_message(filters.command("stop") & filters.group)
async def stop(_, message):
    try:
        vc.leave_group_call(message.chat.id)
        await message.reply_text("Stopped and left VC.")
    except Exception:
        await message.reply_text("No active VC to stop.")

@app.on_message(filters.command("pause") & filters.group)
async def pause(_, message):
    try:
        vc.pause_stream(message.chat.id)
        await message.reply_text("Paused current song.")
    except Exception:
        await message.reply_text("No active VC to pause.")

@app.on_message(filters.command("resume") & filters.group)
async def resume(_, message):
    try:
        vc.resume_stream(message.chat.id)
        await message.reply_text("Resumed current song.")
    except Exception:
        await message.reply_text("No active VC to resume.")

# ------------------ OWNER COMMANDS ------------------
@app.on_message(filters.command("addev") & filters.user(OWNER_ID))
async def addev(_, message):
    if len(message.command) < 3:
        await message.reply_text("Usage: /addev <user_id> <username>")
        return
    user_id = int(message.command[1])
    username = message.command[2]
    add_owner(user_id, username)
    await message.reply_text(f"Added {username} as owner.")

# ------------------ ADMIN PLACEHOLDER ------------------
@app.on_message(filters.command(["kick","ban","unban","mute","unmute","pin","unpin"]) & filters.group)
async def admin_cmd(_, message):
    await message.reply_text(f"Admin command '{message.command[0]}' received. (Implement admin checks)")

# ------------------ RUN ------------------
vc.start()
print("🌊 Aqua Music Bot is online!")
app.run()
