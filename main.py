import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from pytgcalls.exceptions import NoActiveGroupCall
import yt_dlp
import qrcode
from io import BytesIO

# ------------------ ENVIRONMENT ------------------
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH"))
BOT_TOKEN = os.environ.get("BOT_TOKEN"))
OWNER_ID = int(os.environ.get("OWNER_ID"))

# ------------------ CLIENT INIT ------------------
app = Client("AQUA_MUSIC_BOT", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
vc = PyTgCalls(app)

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
        await message.reply_text(f"❍ ᴛɪᴛʟє ➥ {title}\n❍ ʙʏ ➥ {message.from_user.first_name}\n❖ ϻᴧᴅє ʙʏ ➛ THEGAMERADEPT")
    except Exception as e:
        await message.reply_text(f"Error: {e}")

@app.on_message(filters.command("stop") & filters.group)
async def stop(_, message):
    try:
        vc.leave_group_call(message.chat.id)
        await message.reply_text("Stopped and left VC.")
    except Exception as e:
        await message.reply_text("No active VC to stop.")

@app.on_message(filters.command("pause") & filters.group)
async def pause(_, message):
    try:
        vc.pause_stream(message.chat.id)
        await message.reply_text("Paused current song.")
    except Exception as e:
        await message.reply_text("No active VC to pause.")

@app.on_message(filters.command("resume") & filters.group)
async def resume(_, message):
    try:
        vc.resume_stream(message.chat.id)
        await message.reply_text("Resumed current song.")
    except Exception as e:
        await message.reply_text("No active VC to resume.")

# ------------------ ADMIN COMMANDS (placeholder) ------------------
@app.on_message(filters.command(["kick","ban","unban","mute","unmute","pin","unpin"]) & filters.group)
async def admin_cmd(_, message):
    await message.reply_text(f"Admin command '{message.command[0]}' received. (Implement admin checks)")

# ------------------ RUN ------------------
vc.start()
print("🌊 Aqua Music Bot is online!")
app.run()
