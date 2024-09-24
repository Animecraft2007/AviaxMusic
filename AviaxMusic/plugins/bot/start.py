
import asyncio
import time

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch

import config
from config import BANNED_USERS, START_IMG_URL
from strings import get_string
from AviaxMusic import Telegram, YouTube, app
from AviaxMusic.misc import SUDOERS, _boot_
from AviaxMusic.plugins.sudo.sudoers import sudoers_list
from AviaxMusic.utils.database import (
    add_served_chat,
    add_served_user,
    get_assistant,
    get_lang,
    is_banned_user,
    is_on_off,
)
from AviaxMusic.utils.decorators.language import LanguageStart
from AviaxMusic.utils.formatters import get_readable_time
from AviaxMusic.utils.inline import private_panel


loop = asyncio.get_running_loop()


@app.on_message(group=-1)
async def ban_new(client, message):
    user_id = (
        message.from_user.id if message.from_user and message.from_user.id else 777000
    )
    chat_name = message.chat.title if message.chat.title else ""
    if await is_banned_user(user_id):
        try:
            alert_message = f"😳"
            BAN = await message.chat.ban_member(user_id)
            if BAN:
                await message.reply_text(alert_message)
        except:
            pass


@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_comm(client, message: Message, _):
    chat_id = message.chat.id
    await add_served_user(message.from_user.id)
    await message.react("❤️‍🔥")
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        if name[0:4] == "help":
            keyboard = InlineKeyboardMarkup(
                paginate_modules(0, HELPABLE, "help", close=True)
            )
            if config.START_IMG_URL:
                return await message.reply_photo(
                    photo=START_IMG_URL,
                    caption=_["help_1"],
                    reply_markup=keyboard,
                )
            else:
                return await message.reply_text(
                    text=_["help_1"],
                    reply_markup=keyboard,
                )
        if name[0:4] == "song":
            await message.reply_text(_["song_2"])
            return
        if name == "mkdwn_help":
            await message.reply(
                MARKDOWN,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        if name == "greetings":
            await message.reply(
                WELCOMEHELP,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        if name[0:3] == "sta":
            m = await message.reply_text("🔎 ғᴇᴛᴄʜɪɴɢ ʏᴏᴜʀ ᴘᴇʀsᴏɴᴀʟ sᴛᴀᴛs.!")
            stats = await get_userss(message.from_user.id)
            tot = len(stats)
            if not stats:
                await asyncio.sleep(1)
                return await m.edit(_["ustats_1"])

            def get_stats():
                msg = ""
                limit = 0
                results = {}
                for i in stats:
                    top_list = stats[i]["spot"]
                    results[str(i)] = top_list
                    list_arranged = dict(
                        sorted(
                            results.items(),
                            key=lambda item: item[1],
                            reverse=True,
                        )
                    )
                if not results:
                    return m.edit(_["ustats_1"])
                tota = 0
                videoid = None
                for vidid, count in list_arranged.items():
                    tota += count
                    if limit == 10:
                        continue
                    if limit == 0:
                        videoid = vidid
                    limit += 1
                    details = stats.get(vidid)
                    title = (details["title"][:35]).title()
                    if vidid == "telegram":
                        msg += f"🔗[ᴛᴇʟᴇɢʀᴀᴍ ғɪʟᴇs ᴀɴᴅ ᴀᴜᴅɪᴏs]({config.SUPPORT_GROUP}) ** played {count} ᴛɪᴍᴇs**\n\n"
                    else:
                        msg += f"🔗 [{title}](https://www.youtube.com/watch?v={vidid}) ** played {count} times**\n\n"
                msg = _["ustats_2"].format(tot, tota, limit) + msg
                return videoid, msg

            try:
                videoid, msg = await loop.run_in_executor(None, get_stats)
            except Exception as e:
                print(e)
                return
            thumbnail = await YouTube.thumbnail(videoid, True)
            await m.delete()
            await message.reply_photo(photo=thumbnail, caption=msg)
            return
        if name[0:3] == "sud":
            await sudoers_list(client=client, message=message, _=_)
            await asyncio.sleep(1)
            if await is_on_off(config.LOG):
                sender_id = message.from_user.id
                sender_mention = message.from_user.mention
                sender_name = message.from_user.first_name
                return await app.send_message(
                    config.LOG_GROUP_ID,
                    f"{message.from_user.mention} ʜᴀs ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <code>sᴜᴅᴏʟɪsᴛ </code>\n\n**ᴜsᴇʀ ɪᴅ :** {sender_id}\n**ᴜsᴇʀ ɴᴀᴍᴇ:** {sender_name}",
                )
            return
        if name[0:3] == "lyr":
            query = (str(name)).replace("lyrics_", "", 1)
            lyrical = config.lyrical
            lyrics = lyrical.get(query)
            if lyrics:
                await Telegram.send_split_text(message, lyrics)
                return
            else:
                await message.reply_text("ғᴀɪʟᴇᴅ ᴛᴏ ɢᴇᴛ ʟʏʀɪᴄs.")
                return
        if name[0:3] == "del":
            await del_plist_msg(client=client, message=message, _=_)
            await asyncio.sleep(1)
        if name[0:3] == "inf":
            m = await message.reply_text("🔎 ғᴇᴛᴄʜɪɴɢ ɪɴғᴏ!")
            query = (str(name)).replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"
            results = VideosSearch(query, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                channellink = result["channel"]["link"]
                channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]
            searched_text = f"""
🔍__**ᴠɪᴅᴇᴏ ᴛʀᴀᴄᴋ ɪɴғᴏʀᴍᴀᴛɪᴏɴ**__

❇️**ᴛɪᴛʟᴇ:** {title}

⏳**ᴅᴜʀᴀᴛɪᴏɴ:** {duration} Mins
👀**ᴠɪᴇᴡs:** `{views}`
⏰**ᴘᴜʙʟɪsʜᴇᴅ ᴛɪᴍᴇ:** {published}
🎥**ᴄʜᴀɴɴᴇʟ ɴᴀᴍᴇ:** {channel}
📎**ᴄʜᴀɴɴᴇʟ ʟɪɴᴋ:** [ᴠɪsɪᴛ ғʀᴏᴍ ʜᴇʀᴇ]({channellink})
🔗**ᴠɪᴅᴇᴏ ʟɪɴᴋ:** [ʟɪɴᴋ]({link})
"""
            key = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="🎥 ᴡᴀᴛᴄʜ ", url=f"{link}"),
                        InlineKeyboardButton(text="🔄 ᴄʟᴏsᴇ", callback_data="close"),
                    ],
                ]
            )
            await m.delete()
            await app.send_photo(
                message.chat.id,
                photo=thumbnail,
                caption=searched_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=key,
            )
            await asyncio.sleep(1)
            if await is_on_off(config.LOG):
                sender_id = message.from_user.id
                sender_name = message.from_user.first_name
                return await app.send_message(
                    config.LOG_GROUP_ID,
                    f"{message.from_user.mention} ʜᴀs ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ<code> ᴠɪᴅᴇᴏ ɪɴғᴏʀᴍᴀᴛɪᴏɴ </code>\n\n**ᴜsᴇʀ ɪᴅ:** {sender_id}\n**ᴜsᴇʀ ɴᴀᴍᴇ** {sender_name}",
                )
    else:
        out = private_panel(_)
        vip = await message.reply_text(
            f"**𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐁𝐚𝐛𝐲 ꨄ︎ {message.from_user.mention}**"
        )
        await vip.edit_text(f"**𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐁𝐚𝐛𝐲 ꨄ︎ {message.from_user.mention}  ❣️**")
        await vip.edit_text(f"**𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐁𝐚𝐛𝐲 ꨄ︎ {message.from_user.mention}  🐥**")
        await vip.edit_text(f"**𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐁𝐚𝐛𝐲 ꨄ︎ {message.from_user.mention}  ✨**")
        await vip.edit_text(f"**𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐁𝐚𝐛𝐲 ꨄ︎ {message.from_user.mention}  😻**")
        await vip.edit_text(f"**𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐁𝐚𝐛𝐲 ꨄ︎ {message.from_user.mention}  🎉**")

        await vip.delete()
        vips = await message.reply_text("**⚡s**")
        await asyncio.sleep(0.2)
        await vips.edit_text("**⚡sᴛ**")
        await asyncio.sleep(0.2)
        await vips.edit_text("**⚡sᴛᴀ**")
        await asyncio.sleep(0.2)
        await vips.edit_text("**⚡sᴛᴀʀ**")
        await asyncio.sleep(0.2)
        await vips.edit_text("**⚡sᴛᴀʀᴛ**")
        await asyncio.sleep(0.2)
        await vips.edit_text("**⚡sᴛᴀʀᴛɪɴ**")
        await asyncio.sleep(0.2)
        await vips.edit_text("**⚡sᴛᴀʀᴛɪɴɢ.**")
        await asyncio.sleep(0.2)
        await vips.edit_text("**⚡sᴛᴀʀᴛɪɴɢ..**")
        await asyncio.sleep(0.2)
        await vips.edit_text("**⚡sᴛᴀʀᴛɪɴɢ...**")
        await asyncio.sleep(0.1)
        await vips.edit_text("**⚡sᴛᴀʀᴛɪɴɢ.**")
        await asyncio.sleep(0.1)
        await vips.edit_text("**⚡sᴛᴀʀᴛɪɴɢ....**")
        await asyncio.sleep(0.1)
        await vips.edit_text("**⚡sᴛᴀʀᴛɪɴɢ.**")

        await vips.delete()

        done = await message.reply_text("💞")
        await asyncio.sleep(0.5)
        await done.delete()
        
