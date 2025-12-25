from utils import get_size, is_subscribed, is_req_subscribed, group_setting_buttons, get_poster, temp, get_settings, save_group_settings, get_cap, imdb, is_check_admin, extract_request_content, log_error, clean_filename, generate_season_variations, clean_search_text
import tracemalloc
from fuzzywuzzy import process
from tgebotz.util.file_properties import get_name, get_hash
from urllib.parse import quote_plus
import logging
from database.ia_filterdb import Media, Media2, get_file_details, get_search_results, get_bad_files
from database.config_db import mdb
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid, ChatAdminRequired, UserNotParticipant
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto, WebAppInfo
from info import *
from Script import script
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from database.refer import referdb
from database.users_chats_db import db
import asyncio
import re
import math
import random
import pytz
from datetime import datetime, timedelta
lock = asyncio.Lock()

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

tracemalloc.start()


TIMEZONE = "Asia/Kolkata"
BUTTON = {}
BUTTONS = {}
FRESH = {}
BUTTONS0 = {}
BUTTONS1 = {}
BUTTONS2 = {}
SPELL_CHECK = {}


@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    if EMOJI_MODE:
        try:
            await message.react(emoji=random.choice(REACTIONS), big=True)
        except Exception:
            await message.react(emoji="⚡️", big=True)
    await mdb.update_top_messages(message.from_user.id, message.text)
    if message.chat.id != SUPPORT_CHAT_ID:
        settings = await get_settings(message.chat.id)
        try:
            if settings['auto_ffilter']:
                if re.search(r'https?://\S+|www\.\S+|t\.me/\S+', message.text):
                    if await is_check_admin(client, message.chat.id, message.from_user.id):
                        return
                    return await message.delete()
                await auto_filter(client, message)
        except KeyError:
            pass
    else:
        search = message.text
        _, _, total_results = await get_search_results(chat_id=message.chat.id, query=search.lower(), offset=0, filter=True)
        if total_results == 0:
            return
        await message.reply_text(
            f"<b>Hey🙋</code> {message.from_user.mention},\n\n"
            f"<code>Your Request is already Available ✅</code>\n\n"
            f"<code>📂 File Found :</code> {str(total_results)}\n"
            f"<code>🔍 Search :</code> <code>{search}</code>\n\n"
            f"<code>‼️ ᴛʜɪs ɪs ᴀ <u>Support Group</u> So that you can't get files from here...</code>\n\n"
            f"<code>📝 Search Here : 👇</code>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔍 JOIN AND SEARCH HERE 🔎", url=GRP_LNK)]])
        )


@Client.on_message(filters.private & filters.text & filters.incoming & ~filters.regex(r"^/"))
async def pm_text(bot, message):
    bot_id = bot.me.id
    content = message.text
    user = message.from_user.first_name
    user_id = message.from_user.id
    if EMOJI_MODE:
        try:
            await message.react(emoji=random.choice(REACTIONS), big=True)
        except Exception:
            await message.react(emoji="⚡️", big=True)
    if content.startswith(("#")):
        return
    try:
        await mdb.update_top_messages(user_id, content)
        pm_search = await db.pm_search_status(bot_id)
        if pm_search:
            await auto_filter(bot, message)
        else:
            await message.reply_text(
                text=(
                    f"<code>🙋 Hey</code> {user} 😍 ,\n\n"
                    "You can search for movies only in our Movie Group. You are not allowed to search for movies on the Direct Bot. Please join our movie group by clicking the Request Here button below and search for your favorite movie there 👇."
                    "<blockquote>"
                    "आप केवल हमारे Movie Group पर ही Movie Search कर सकते हैं।"
                    "आपको Direct Bot पर Movie Search करने की अनुमति नहीं है। कृपया नीचे दिए गए 'Request Here' वाले Button पर क्लिक करके हमारे Movie Group को Join करें और वहां अपनी मनपसंद Movie Search करें।"
                    "</blockquote></b>"
                ), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📝 REQUEST HERE", url=GRP_LNK)]]))
            await bot.send_message(chat_id=LOG_CHANNEL,
                                   text=(
                                       f"<b>#𝐏𝐌_𝐌𝐒𝐆 </b>\n\n"
                                       f"<code>👤 Name : </code> {user}\n"
                                       f"<code>🆔 Id : </code> {user_id}\n"
                                       f"<code>💬 Message : {content}</code>"
                                   )
                                   )
    except Exception:
        pass


@Client.on_callback_query(filters.regex(r"^reffff"))
async def refercall(bot, query):
    btn = [[
        InlineKeyboardButton(
            'invite link', url=f'https://telegram.me/share/url?url=https://t.me/{bot.me.username}?start=reff_{query.from_user.id}&text=Hello%21%20Experience%20a%20bot%20that%20offers%20a%20vast%20library%20of%20unlimited%20movies%20and%20series.%20%F0%9F%98%83'),
        InlineKeyboardButton(
            f'⏳ {referdb.get_refer_points(query.from_user.id)}', callback_data='ref_point'),
        InlineKeyboardButton('Back', callback_data='premium_info')
    ]]
    reply_markup = InlineKeyboardMarkup(btn)
    try:
        await bot.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto("https://graph.org/file/1a2e64aee3d4d10edd930.jpg")
        )
    except Exception as e:    
        pass
    await query.message.edit_text(
        text=f'Hay Your refer link:\n\nhttps://t.me/{bot.me.username}?start=reff_{query.from_user.id}\n\nShare this link with your friends, Each time they join,  you will get 10 refferal points and after 100 points you will get 1 month premium subscription.',
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )
    await query.answer()


@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    if BUTTONS.get(key) != None:
        search = BUTTONS.get(key)
    else:
        search = FRESH.get(key)
    if not search:
        await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True)
        return
    files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    temp.GETALL[key] = files
    temp.SHORT[query.from_user.id] = query.message.chat.id
    settings = await get_settings(query.message.chat.id)
    if settings.get('button'):
        btn = [
            [
                InlineKeyboardButton(text=f"🔗 {get_size(file.file_size)} ≽ " + clean_filename(
                    file.file_name), callback_data=f'file#{file.file_id}'),
            ]
            for file in files
        ]
        btn.insert(0,
                   [
                       InlineKeyboardButton(
                           f'Quality', callback_data=f"qualities#{key}"),
                       InlineKeyboardButton(
                           "Language", callback_data=f"languages#{key}"),
                       InlineKeyboardButton(
                           "Season",  callback_data=f"seasons#{key}")
                   ]
                   )
        btn.insert(0,
                   [
                       InlineKeyboardButton(
                           "🎫 Remove Ads 🎫", url=f"https://t.me/{temp.U_NAME}?start=premium"),
                       InlineKeyboardButton(
                           "Send All", callback_data=f"sendfiles#{key}")

                   ]
                   )

    else:
        btn = []
        btn.insert(0,
                   [
                       InlineKeyboardButton(
                           f'Quality', callback_data=f"qualities#{key}"),
                       InlineKeyboardButton(
                           "Language", callback_data=f"languages#{key}"),
                       InlineKeyboardButton(
                           "Season",  callback_data=f"seasons#{key}")
                   ]
                   )
        btn.insert(0, [
            InlineKeyboardButton(
                "🎫 Remove Ads 🎫 ", url=f"https://t.me/{temp.U_NAME}?start=premium"),
            InlineKeyboardButton("Send All", callback_data=f"sendfiles#{key}")
        ])
    try:
        if settings['max_btn']:
            if 0 < offset <= 10:
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - 10
            if n_offset == 0:
                btn.append([InlineKeyboardButton("Page", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(
                    f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages")])
            elif off_set is None:
                btn.append([InlineKeyboardButton("Page", callback_data="pages"), InlineKeyboardButton(
                    f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"), InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")])
            else:
                btn.append(
                    [
                        InlineKeyboardButton(
                            "⏮️ Back", callback_data=f"next_{req}_{key}_{off_set}"),
                        InlineKeyboardButton(
                            f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
                        InlineKeyboardButton(
                            "Next ⏭️", callback_data=f"next_{req}_{key}_{n_offset}")
                    ],
                )
        else:
            if 0 < offset <= int(MAX_B_TN):
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - int(MAX_B_TN)
            if n_offset == 0:
                btn.append([InlineKeyboardButton("⏮️ Back", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(
                    f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages")])
            elif off_set is None:
                btn.append([InlineKeyboardButton("Page", callback_data="pages"), InlineKeyboardButton(
                    f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"), InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")])
            else:
                btn.append(
                    [
                        InlineKeyboardButton(
                            "⏮️ Back", callback_data=f"next_{req}_{key}_{off_set}"),
                        InlineKeyboardButton(
                            f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"),
                        InlineKeyboardButton(
                            "Next ⏭️", callback_data=f"next_{req}_{key}_{n_offset}")
                    ],
                )
    except KeyError:
        await save_group_settings(query.message.chat.id, 'max_btn', True)
        if 0 < offset <= 10:
            off_set = 0
        elif offset == 0:
            off_set = None
        else:
            off_set = offset - 10
        if n_offset == 0:
            btn.append(
                [InlineKeyboardButton("⏮️ Back", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(
                    f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages")]
            )
        elif off_set is None:
            btn.append([InlineKeyboardButton("Page", callback_data="pages"), InlineKeyboardButton(
                f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"), InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")])
        else:
            btn.append(
                [
                    InlineKeyboardButton(
                        "⏮️ Back", callback_data=f"next_{req}_{key}_{off_set}"),
                    InlineKeyboardButton(
                        f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
                    InlineKeyboardButton(
                        "Next ⏭️", callback_data=f"next_{req}_{key}_{n_offset}")
                ],
            )
    if not settings["button"]:
        cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - \
            timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(
                curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        tge_title = clean_search_text(search)
        cap = await get_cap(settings, remaining_seconds, files, query, total, tge_title, offset+1)
        try:
            await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
        except MessageNotModified:
            pass
    await query.answer()


@Client.on_callback_query(filters.regex(r"^spol"))
async def advantage_spoll_choker(bot, query):
    _, id, user = query.data.split('#')
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    movies = await get_poster(id, id=True)
    movie = movies.get('title')
    movie = re.sub(r"[:-]", " ", movie)
    movie = re.sub(r"\s+", " ", movie).strip()
    await query.answer(script.TOP_ALRT_MSG)
    files, offset, total_results = await get_search_results(query.message.chat.id, movie, offset=0, filter=True)
    if files:
        k = (movie, files, offset, total_results)
        await auto_filter(bot, query, k)
    else:
        reqstr1 = query.from_user.id if query.from_user else 0
        reqstr = await bot.get_users(reqstr1)
        if NO_RESULTS_MSG:
            try:
                await bot.send_message(chat_id=BIN_CHANNEL, text=script.NORSLTS.format(reqstr.id, reqstr.mention, movie))
            except Exception as e:
                print(f"Error In Spol - {e}   Make Sure Bot Admin BIN CHANNEL")
        btn = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔰CLICK HERE & REQUEST TO ADMIN🔰", url=OWNER_LNK)]])
        k = await query.message.edit(script.MVE_NT_FND, reply_markup=btn)
        await asyncio.sleep(10)
        await k.delete()

# Qualities
@Client.on_callback_query(filters.regex(r"^qualities#"))
async def qualities_cb_handler(client: Client, query: CallbackQuery):
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"<code>⚠️ Hello </code> {query.from_user.first_name},\n"
                f"<code>ᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇǫᴜᴇꜱᴛ,\nʀᴇǫᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...</code>",
                show_alert=True,
            )
    except:
        pass

    _, key = query.data.split("#")
    search = FRESH.get(key)
    search = search.replace(' ', '_')

    btn = []
    for i in range(0, len(QUALITIES), 2):
        q1 = QUALITIES[i]
        row = [InlineKeyboardButton(
            text=q1, callback_data=f"fq#{q1.lower()}#{key}")]
        if i + 1 < len(QUALITIES):
            q2 = QUALITIES[i + 1]
            row.append(InlineKeyboardButton(
                text=q2, callback_data=f"fq#{q2.lower()}#{key}"))
        btn.append(row)

    btn.insert(0, [
        InlineKeyboardButton(text="⇊ SELECT QUALITY ⇊", callback_data="ident")
    ])
    btn.append([
        InlineKeyboardButton(text="↭ BACK TO FILES ↭",
                             callback_data=f"fq#homepage#{key}")
    ])

    await query.edit_message_reply_markup(InlineKeyboardMarkup(btn))


@Client.on_callback_query(filters.regex(r"^fq#"))
async def filter_qualities_cb_handler(client: Client, query: CallbackQuery):
    _, qual, key = query.data.split("#")
    curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    search = FRESH.get(key)
    search = search.replace("_", " ")
    baal = qual in search
    if baal:
        search = search.replace(qual, "")
    else:
        search = search
    req = query.from_user.id
    chat_id = query.message.chat.id
    message = query.message
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(f"<code>⚠️ ʜᴇʟʟᴏ|</code> {query.from_user.first_name},\n <code >ᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇǫᴜᴇꜱᴛ,\nʀᴇǫᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...</code>", show_alert=True,)
    except:
        pass
    if qual != "homepage":
        search = f"{search} {qual}"
    BUTTONS[key] = search
    files, offset, total_results = await get_search_results(chat_id, search, offset=0, filter=True)
    if not files:
        await query.answer("🚫 NO FILES WERE FOUND 🚫", show_alert=1)
        return
    temp.GETALL[key] = files
    settings = await get_settings(message.chat.id)
    if settings.get('button'):
        btn = [
            [
                InlineKeyboardButton(text=f"🔗 {get_size(file.file_size)} ≽ " + clean_filename(
                    file.file_name), callback_data=f'file#{file.file_id}'),
            ]
            for file in files
        ]
        btn.insert(0,
                   [
                       InlineKeyboardButton(
                           f'Quality', callback_data=f"qualities#{key}"),
                       InlineKeyboardButton(
                           "Language", callback_data=f"languages#{key}"),
                       InlineKeyboardButton(
                           "Season",  callback_data=f"seasons#{key}")
                   ]
                   )
        btn.insert(0,
                   [
                       InlineKeyboardButton(
                           "🎫 Remove Ads 🎫", url=f"https://t.me/{temp.U_NAME}?start=premium"),
                       InlineKeyboardButton(
                           "Send All", callback_data=f"sendfiles#{key}")
                   ])
    else:
        btn = []
        btn.insert(0,
                   [
                       InlineKeyboardButton(
                           f'Quality', callback_data=f"qualities#{key}"),
                       InlineKeyboardButton(
                           "Language", callback_data=f"languages#{key}"),
                       InlineKeyboardButton(
                           "Season",  callback_data=f"seasons#{key}")
                   ]
                   )
        btn.insert(0,
                   [
                       InlineKeyboardButton(
                           "🎫 Remove Ads 🎫 ", url=f"https://t.me/{temp.U_NAME}?start=premium"),
                       InlineKeyboardButton(
                           "Send All", callback_data=f"sendfiles#{key}")

                   ])
    if offset != "":
        try:
            if settings['max_btn']:
                btn.append(

                    [InlineKeyboardButton("Page", callback_data="pages"), InlineKeyboardButton(
                        text=f"1/{math.ceil(int(total_results)/10)}", callback_data="pages"), InlineKeyboardButton(text="Next ⏭️", callback_data=f"next_{req}_{key}_{offset}")]
                )
            else:
                btn.append(

                    [InlineKeyboardButton("Page", callback_data="pages"), InlineKeyboardButton(
                        text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}", callback_data="pages"), InlineKeyboardButton(text="Next ⏭️", callback_data=f"next_{req}_{key}_{offset}")]
                )
        except KeyError:
            await save_group_settings(query.message.chat.id, 'max_btn', True)
            btn.append(

                [InlineKeyboardButton("Page", callback_data="pages"), InlineKeyboardButton(
                    text=f"1/{math.ceil(int(total_results)/10)}", callback_data="pages"), InlineKeyboardButton(text="Next ⏭️", callback_data=f"next_{req}_{key}_{offset}")]
            )
    else:
        btn.append(

            [InlineKeyboardButton(
                text="↭🚫 NO MORE PAGES AVAILABLE 🚫↭", callback_data="pages")]
        )
    if not settings["button"]:
        cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - \
            timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(
                curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        tge_title = clean_search_text(search)
        cap = await get_cap(settings, remaining_seconds, files, query, total_results, tge_title, offset=1)
        try:
            await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
        except MessageNotModified:
            pass
    await query.answer()

# languages


@Client.on_callback_query(filters.regex(r"^languages#"))
async def languages_cb_handler(client: Client, query: CallbackQuery):
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"<code>⚠️ Hello</code> {query.from_user.first_name},\n"
                f"<code> This is not your movie Request,\n Request your's...</code>",
                show_alert=True,
            )
    except:
        pass

    _, key = query.data.split("#")
    search = FRESH.get(key)
    search = search.replace(' ', '_')

    items = list(LANGUAGES.items())
    btn = []

    for i in range(0, len(items), 2):
        name1, code1 = items[i]
        row = [InlineKeyboardButton(
            text=name1, callback_data=f"fl#{code1}#{key}")]
        if i + 1 < len(items):
            name2, code2 = items[i + 1]
            row.append(InlineKeyboardButton(
                text=name2, callback_data=f"fl#{code2}#{key}"))
        btn.append(row)

    btn.insert(0, [InlineKeyboardButton(
        text="⇊ SELECT LANGUAGE ⇊", callback_data="ident")])
    btn.append([InlineKeyboardButton(text="↭ BACK TO FILES ↭",
               callback_data=f"fl#homepage#{key}")])

    await query.edit_message_reply_markup(InlineKeyboardMarkup(btn))


@Client.on_callback_query(filters.regex(r"^fl#"))
async def filter_languages_cb_handler(client: Client, query: CallbackQuery):
    _, lang, key = query.data.split("#")
    curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    search = FRESH.get(key)
    search = search.replace("_", " ")
    baal = lang in search
    if baal:
        search = search.replace(lang, "")
    else:
        search = search
    req = query.from_user.id
    chat_id = query.message.chat.id
    message = query.message
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(f"<code>⚠️ Hello </code> {query.from_user.first_name},\n <code> ᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇǫᴜᴇꜱᴛ,\nʀᴇǫᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ... </code>", show_alert=True,)
    except:
        pass
    if lang != "homepage":
        search = f"{search} {lang}"
    BUTTONS[key] = search
    files, offset, total_results = await get_search_results(chat_id, search, offset=0, filter=True)
    if not files:
        await query.answer("🚫 NO FILES WERE FOUNDED 🚫", show_alert=1)
        return
    temp.GETALL[key] = files
    settings = await get_settings(message.chat.id)
    if settings.get('button'):
        btn = [
            [
                InlineKeyboardButton(text=f"🔗 {get_size(file.file_size)} ≽ " + clean_filename(
                    file.file_name), callback_data=f'file#{file.file_id}'),
            ]
            for file in files
        ]
        btn.insert(0,
                   [
                       InlineKeyboardButton(
                           f'Quality', callback_data=f"qualities#{key}"),
                       InlineKeyboardButton(
                           "Languag", callback_data=f"languages#{key}"),
                       InlineKeyboardButton(
                           "Season",  callback_data=f"seasons#{key}")
                   ]
                   )
        btn.insert(0,
                   [
                       InlineKeyboardButton(
                           "🎫 Remove Ads 🎫", url=f"https://t.me/{temp.U_NAME}?start=premium"),
                       InlineKeyboardButton(
                           "Send All", callback_data=f"sendfiles#{key}")
                   ]
                   )
    else:
        btn = []
        btn.insert(0,
                   [
                       InlineKeyboardButton(
                           f'Quality', callback_data=f"qualities#{key}"),
                       InlineKeyboardButton(
                           "Language", callback_data=f"languages#{key}"),
                       InlineKeyboardButton(
                           "Season",  callback_data=f"seasons#{key}")
                   ])
        btn.insert(0,
                   [
                       InlineKeyboardButton(
                           "🎫 Remove Ads 🎫", url=f"https://t.me/{temp.U_NAME}?start=premium"),
                       InlineKeyboardButton(
                           "Send All", callback_data=f"sendfiles#{key}")
                   ])
    if offset != "":
        try:
            if settings['max_btn']:
                btn.append(
                    [
                        InlineKeyboardButton("Page", callback_data="pages"), InlineKeyboardButton(
                            text=f"1/{math.ceil(int(total_results)/10)}", callback_data="pages"), InlineKeyboardButton(text="Next ⏭️", callback_data=f"next_{req}_{key}_{offset}")
                    ])
            else:
                btn.append(
                    [
                        InlineKeyboardButton("Page", callback_data="pages"), InlineKeyboardButton(
                            text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}", callback_data="pages"), InlineKeyboardButton(text="Next ⏭️", callback_data=f"next_{req}_{key}_{offset}")
                    ])
        except KeyError:
            await save_group_settings(query.message.chat.id, 'max_btn', True)
            btn.append(
                [
                    InlineKeyboardButton("Page", callback_data="pages"), InlineKeyboardButton(
                        text=f"1/{math.ceil(int(total_results)/10)}", callback_data="pages"), InlineKeyboardButton(text="Next ⏭️", callback_data=f"next_{req}_{key}_{offset}")
                ])
    else:
        btn.append([InlineKeyboardButton(
            text="↭🚫 NO MORE PAGES AVAILABLE 🚫 ↭", callback_data="pages")])
    if not settings["button"]:
        cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - \
            timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(
                curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        tge_title = clean_search_text(search)
        cap = await get_cap(settings, remaining_seconds, files, query, total_results, tge_title, offset=1)
        try:
            await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
        except MessageNotModified:
            pass
    await query.answer()


@Client.on_callback_query(filters.regex(r"^seasons#"))
async def seasons_cb_handler(client: Client, query: CallbackQuery):
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"<code>⚠️ Hello</code> {query.from_user.first_name},\n This is not your movie request ,\n Request your's…",
                show_alert=True,
            )
    except Exception:
        pass
    _, key = query.data.split("#")
    search = FRESH.get(key).replace(" ", "_")
    req = query.from_user.id
    offset = 0
    btn: list[list[InlineKeyboardButton]] = []
    for i in range(0, len(SEASONS) - 1, 2):
        btn.append([
            InlineKeyboardButton(
                f"Season {SEASONS[i][1:]}", callback_data=f"fs#{SEASONS[i].lower()}#{key}"),
            InlineKeyboardButton(
                f"Season {SEASONS[i+1][1:]}", callback_data=f"fs#{SEASONS[i+1].lower()}#{key}")
        ])

    btn.insert(
        0,
        [InlineKeyboardButton("⇊ SELECT SEASON ⇊", callback_data="ident")],
    )
    btn.append([InlineKeyboardButton(text="↭ BACK TO FILES ​↭",
               callback_data=f"next_{req}_{key}_{offset}")])
    await query.edit_message_reply_markup(InlineKeyboardMarkup(btn))
    await query.answer()


@Client.on_callback_query(filters.regex(r"^fs#"))
async def filter_seasons_cb_handler(client: Client, query: CallbackQuery):
    _, season_tag, key = query.data.split("#")
    search = FRESH.get(key).replace("_", " ")
    season_tag = season_tag.lower()
    if season_tag == "homepage":
        search_final = search
        query_input = search_final
    else:
        season_number = int(season_tag[1:])
        query_input = generate_season_variations(search, season_number)
        search_final = query_input[0] if query_input else search

    BUTTONS[key] = search_final
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer("<code>⚠️ Not your request </code>", show_alert=True)
    except Exception:
        pass

    chat_id = query.message.chat.id
    req = query.from_user.id
    files, n_offset, total_results = await get_search_results(chat_id, query_input, offset=0, filter=True)
    if not files:
        return await query.answer("🚫 NO FILES FOUND 🚫", show_alert=True)

    temp.GETALL[key] = files
    settings = await get_settings(chat_id)
    btn: list[list[InlineKeyboardButton]] = []
    if settings.get("button"):
        btn.extend(
            [
                [
                    InlineKeyboardButton(
                        f"🔗 {get_size(f.file_size)} ≽ " +
                        clean_filename(f.file_name),
                        callback_data=f"file#{f.file_id}",
                    )
                ]
                for f in files
            ]
        )
    btn.insert(
        0,
        [
            InlineKeyboardButton("Quality", callback_data=f"qualities#{key}"),
            InlineKeyboardButton("Language", callback_data=f"languages#{key}"),
            InlineKeyboardButton("Season", callback_data=f"seasons#{key}"),
        ],
    )
    btn.insert(
        0,
        [
            InlineKeyboardButton(
                "🎫 Remove Ads 🎫", url=f"https://t.me/{temp.U_NAME}?start=premium"),
            InlineKeyboardButton("Send All", callback_data=f"sendfiles#{key}"),
        ],
    )
    if n_offset != "":
        try:
            if settings['max_btn']:
                btn.append(
                    [InlineKeyboardButton("Page", callback_data="pages"), InlineKeyboardButton(
                        text=f"1/{math.ceil(int(total_results)/10)}", callback_data="pages"), InlineKeyboardButton(text="Next ⏭️", callback_data=f"next_{req}_{key}_{n_offset}")]
                )

            else:
                btn.append(
                    [InlineKeyboardButton("Page", callback_data="pages"), InlineKeyboardButton(
                        text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}", callback_data="pages"), InlineKeyboardButton(text="Next ⏭️", callback_data=f"next_{req}_{key}_{n_offset}")]
                )
        except KeyError:
            await save_group_settings(query.message.chat.id, 'max_btn', True)
            btn.append(
                [InlineKeyboardButton("Page", callback_data="pages"), InlineKeyboardButton(
                    text=f"1/{math.ceil(int(total_results)/10)}", callback_data="pages"), InlineKeyboardButton(text="Next ⏭️", callback_data=f"next_{req}_{key}_{n_offset}")]
            )
    else:
        n_offset = 0
        btn.append(
            [InlineKeyboardButton(
                "↭ 🚫 NO MORE PAGES AVAILABLE 🚫 ↭", callback_data="pages")]
        )
    if not settings.get("button"):
        curr_time = datetime.now(pytz.timezone("Asia/Kolkata")).time()
        time_difference = timedelta(
            hours=curr_time.hour,
            minutes=curr_time.minute,
            seconds=curr_time.second + curr_time.microsecond / 1_000_000,
        )
        remaining_seconds = f"{time_difference.total_seconds():.2f}"
        tge_title = clean_search_text(search_final)
        cap = await get_cap(settings, remaining_seconds, files, query, total_results, tge_title, offset=1)
        try:
            await query.message.edit_text(
                text=cap,
                reply_markup=InlineKeyboardMarkup(btn),
                disable_web_page_preview=True,
            )
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(InlineKeyboardMarkup(btn))
        except MessageNotModified:
            pass
    await query.answer()


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    TgeData = query.data
    try:
        link = await client.create_chat_invite_link(int(REQST_CHANNEL))
    except:
        pass
    if query.data == "close_data":
        try:
            user = query.message.reply_to_message.from_user.id
        except:
            user = query.from_user.id
        if int(user) != 0 and query.from_user.id != int(user):
            return await query.answer(script.NT_ALRT_TXT, show_alert=True)
        await query.answer("THANKS FOR CLOSE 🙈")
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass

    elif query.data == "pages":
        await query.answer("THIS IS PAGES BUTTON 😅")

    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type
        if chat_type == enums.ChatType.PRIVATE:
            await query.message.reply_to_message.delete()
            await query.message.delete()
        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer("That's not for you !!", show_alert=True)

    if query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        user = query.message.reply_to_message.from_user.id if query.message.reply_to_message else query.from_user.id
        if int(user) != 0 and query.from_user.id != int(user):
            return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start=file_{query.message.chat.id}_{file_id}")

    elif query.data.startswith("sendfiles"):
        clicked = query.from_user.id
        ident, key = query.data.split("#")
        settings = await get_settings(query.message.chat.id)
        try:
            await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=allfiles_{query.message.chat.id}_{key}")
            return
        except UserIsBlocked:
            await query.answer('UNBLOCK THE BOT MAHN !', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=sendfiles3_{key}")
        except Exception as e:
            logger.exception(e)
            await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=sendfiles4_{key}")

    elif query.data.startswith("del"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        settings = await get_settings(query.message.chat.id)
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"
        await query.answer(url=f"href='https://telegram.me/{temp.U_NAME}?start=file_{query.message.chat.id}_{file.file_id}")

    elif query.data.startswith("autofilter_delete"):
        await Media.collection.drop()
        if MULTIPLE_DB:    
            await Media2.collection.drop()
        await query.answer("Everything's Gone")
        await query.message.edit('Successfully delete all indexed files ✅')

    elif query.data.startswith("checksub"):
        try:
            ident, kk, file_id = query.data.split("#")
            btn = []
            chat = file_id.split("_")[0]
            settings = await get_settings(chat)
            fsub_channels = list(dict.fromkeys((settings.get('fsub', []) if settings else [])+ AUTH_CHANNELS)) 
            btn += await is_subscribed(client, query.from_user.id, fsub_channels)
            btn += await is_req_subscribed(client, query.from_user.id, AUTH_REQ_CHANNELS)
            if btn:
                btn.append([InlineKeyboardButton("♻️ Try again ♻️", callback_data=f"checksub#{kk}#{file_id}")])
                try:
                    await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
                except MessageNotModified:
                    pass
                await query.answer(
                    f"<code>👋 Hello </code>{query.from_user.first_name},\n\n"
                    "<code>🛑 You have not joined all required update channels.</code>\n"
                    "<code>👉 Please join each one try again.</code>\n",
                    show_alert=True
                )
                return
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={kk}_{file_id}")
            await query.message.delete()
        except Exception as e:
            await log_error(client, f"❌ Error in checksub callback:\n\n{repr(e)}")
            logger.error(f"❌ Error in checksub callback:\n\n{repr(e)}")


    elif query.data.startswith("killfilesdq"):
        ident, keyword = query.data.split("#")
        await query.message.edit_text(f"<code>Fetching Files for your query</code> {keyword} <code> on DB... Please wait...</code>")
        files, total = await get_bad_files(keyword)
        await query.message.edit_text("<code> File deletion process will start in 5 second !</code>")
        await asyncio.sleep(5)
        deleted = 0
        async with lock:
            try:
                for file in files:
                    file_ids = file.file_id
                    file_name = file.file_name
                    result = await Media.collection.delete_one({
                        '_id': file_ids,
                    })
                    if not result.deleted_count and MULTIPLE_DB:
                        result = await Media2.collection.delete_one({
                            '_id': file_ids,
                        })
                    if result.deleted_count:
                        logger.info(
                            f'<code>File found for your query</code> {keyword}! <code> Successfully Deleted </code> {file_name} <code>From Database.</code>')
                    deleted += 1
                    if deleted % 20 == 0:
                        await query.message.edit_text(f"<code> Process started for deleting files from DB. Successfully Deleted</code> {str(deleted)} Files from DB for your Query {keyword} !\n\nPlease wait...</code>")
            except Exception as e:
                print(f"Error In killfiledq -{e}")
                await query.message.edit_text(f'Error: {e}')
            else:
                await query.message.edit_text(f"<code> Process completed for file deletation !\n\n Successfully Deleted </code> {str(deleted)} <code>Files from DB for your query Files</code> {keyword}.</b>")

    elif query.data.startswith("opnsetgrp"):
        ident, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        st = await client.get_chat_member(grp_id, userid)
        if (
                st.status != enums.ChatMemberStatus.ADMINISTRATOR
                and st.status != enums.ChatMemberStatus.OWNER
                and str(userid) not in ADMINS
        ):
            await query.answer("<code>You don't have rights to do do this !</code>", show_alert=True)
            return
        title = query.message.chat.title
        settings = await get_settings(grp_id)
        if settings is not None:
            btn = await group_setting_buttons(int(grp_id))
            reply_markup = InlineKeyboardMarkup(btn)
            await query.message.edit_text(
                text=f"<code>Change your settings for </code> {title} <code>As you wish ⚙</code>",
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML
            )
            await query.message.edit_reply_markup(reply_markup)

    elif query.data.startswith("opnsetpm"):
        ident, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        st = await client.get_chat_member(grp_id, userid)
        if (
                st.status != enums.ChatMemberStatus.ADMINISTRATOR
                and st.status != enums.ChatMemberStatus.OWNER
                and str(userid) not in ADMINS
        ):
            await query.answer("<code> You don't have sufficient rights to do this !</code>", show_alert=True)
            return
        title = query.message.chat.title
        settings = await get_settings(grp_id)
        btn2 = [[
            InlineKeyboardButton(
                "CHECK MY DM 🗳️", url=f"telegram.me/{temp.U_NAME}")
        ]]
        reply_markup = InlineKeyboardMarkup(btn2)
        await query.message.edit_text(f"<code> Your settings menu for </code> {title} <code> Has been sent to you by DM.</code>")
        await query.message.edit_reply_markup(reply_markup)
        if settings is not None:
            btn = await group_setting_buttons(int(grp_id))
            reply_markup = InlineKeyboardMarkup(btn)
            await client.send_message(
                chat_id=userid,
                text=f"<code>Change your settings for</code>{title} <code>As you wish ⚙</code>",
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML,
                reply_to_message_id=query.message.id
            )

    elif query.data.startswith("show_option"):
        ident, from_user = query.data.split("#")
        btn = [[
            InlineKeyboardButton("⚠️ UNAVAILABLE ⚠️",
                                 callback_data=f"unavailable#{from_user}"),
            InlineKeyboardButton(
                "🟢 UPLOADED 🟢", callback_data=f"uploaded#{from_user}")
        ], [
            InlineKeyboardButton("♻️ ALREADY AVAILABLE ♻️",
                                 callback_data=f"already_available#{from_user}")
        ], [
            InlineKeyboardButton("📌  Not Released 📌",
                                 callback_data=f"Not_Released#{from_user}"),
            InlineKeyboardButton("♨️Type Correct Spelling♨️",
                                 callback_data=f"Type_Correct_Spelling#{from_user}")
        ], [
            InlineKeyboardButton("🚫 Not Available In Hindi 🚫",
                                 callback_data=f"Not_Available_In_The_Hindi#{from_user}")
        ]]
        btn2 = [[
            InlineKeyboardButton("VIEW STATUS", url=f"{query.message.link}")
        ]]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            await query.message.edit_reply_markup(reply_markup)
            await query.answer(" Here are the options!")
        else:
            await query.answer("<code> You don't have sufficiant rights to do this !</code>", show_alert=True)

    elif query.data.startswith("unavailable"):
        ident, from_user = query.data.split("#")
        btn = [
            [InlineKeyboardButton("⚠️ UNAVAILABLE ⚠️",
                                  callback_data=f"unalert#{from_user}")]
        ]
        btn2 = [
            [InlineKeyboardButton('JOIN CHANNEL ', url=link.invite_link),
             InlineKeyboardButton("VIEW STATUS", url=f"{query.message.link}")]
        ]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("<code>Set to Unavailable!<code>")
            content = extract_request_content(query.message.text)
            try:
                await client.send_message(
                    chat_id=int(from_user),
                    text=f"<code>Hey </code> {user.mention},\n\n<u>{content}</u> <code>Has been marked Ad Unavailable...💔</code>\n\n#Unavailable ⚠️",
                    reply_markup=InlineKeyboardMarkup(btn2)
                )
            except UserIsBlocked:
                await client.send_message(
                    chat_id=int(SUPPORT_CHAT_ID),
                    text=f"<code>Hey </code> {user.mention},\n\n<u>{content}</u> <code> Has been marked Ad Unavailable...</code>💔\n\n#Uɴᴀᴠᴀɪʟᴀʙʟᴇ ⚠️\n\n<small>Bʟᴏᴄᴋᴇᴅ? Uɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ʀᴇᴄᴇɪᴠᴇ ᴍᴇꜱꜱᴀɢᴇꜱ Unblock the bot received messages.</small></b>",
                    reply_markup=InlineKeyboardMarkup(btn2)
                )

    elif query.data.startswith("Not_Released"):
        ident, from_user = query.data.split("#")
        btn = [[InlineKeyboardButton(
            "📌 Not Released 📌", callback_data=f"nralert#{from_user}")]]
        btn2 = [[
            InlineKeyboardButton('JOIN CHANNEL ', url=link.invite_link),
            InlineKeyboardButton("VIEW STATUS", url=f"{query.message.link}")
        ]]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Set to not released!")
            content = extract_request_content(query.message.text)
            try:
                await client.send_message(
                    chat_id=int(from_user),
                    text=(
                        f"<code>Hey</code> {user.mention}\n\n"
                        f"<code>{content}</code>, <code>Your request has not been released yet </code>\n\n"
                        f"#ComingSoon...😍✌️</b>"
                    ),
                    reply_markup=InlineKeyboardMarkup(btn2)
                )
            except UserIsBlocked:
                await client.send_message(
                    chat_id=int(SUPPORT_CHAT_ID),
                    text=(
                        f"<u>Hey {user.mention}</u>\n\n"
                        f"<b><code>{content}</code>, <code>Your request has not been released yet </code>\n\n"
                        f"#CominSoon...😍✌️\n\n"
                        f"<small>Bʟᴏᴄᴋᴇᴅ? Unblock the bot to received messages.</small></b>"
                    ),
                    reply_markup=InlineKeyboardMarkup(btn2)
                )
        else:
            await query.answer(" <code>You don't have sufficiant rights to do this!</code>", show_alert=True)

    elif query.data.startswith("Type_Correct_Spelling"):
        ident, from_user = query.data.split("#")
        btn = [[
            InlineKeyboardButton("♨️ Type Correct Spelling ♨️",
                                 callback_data=f"wsalert#{from_user}")
        ]]
        btn2 = [[
            InlineKeyboardButton('ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ', url=link.invite_link),
            InlineKeyboardButton("ᴠɪᴇᴡ ꜱᴛᴀᴛᴜꜱ", url=f"{query.message.link}")
        ]]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("<code>Set to correct spelling!</code>")
            content = extract_request_content(query.message.text)
            try:
                await client.send_message(
                    chat_id=int(from_user),
                    text=(
                        f"<code>Hey </code> {user.mention}\n\n"
                        f" <code> We declined your request </code> {content}, <code>Because your spelling was wrong </code>😢\n\n"
                        f"#Wrong_Spelling 😑</b>"
                    ),
                    reply_markup=InlineKeyboardMarkup(btn2)
                )
            except UserIsBlocked:
                await client.send_message(
                    chat_id=int(SUPPORT_CHAT_ID),
                    text=(
                        f"<u>Hey {user.mention}</u>\n\n"
                        f"<b><code>{content}</code>, <code>Because your spelling was wrong </code>😢\n\n"
                        f"#Wʀᴏɴɢ_Sᴘᴇʟʟɪɴɢ 😑\n\n"
                        f"<small>Bʟᴏᴄᴋᴇᴅ?  Unblock the bot to received mesages.</small></b>"
                    ),
                    reply_markup=InlineKeyboardMarkup(btn2)
                )
        else:
            await query.answer(" <code>You don't have sufficient rights to do this !</code>", show_alert=True)

    elif query.data.startswith("Not_Available_In_The_Hindi"):
        ident, from_user = query.data.split("#")
        btn = [[
            InlineKeyboardButton(
                "🚫 Not Available In The Hindi 🚫", callback_data=f"hnalert#{from_user}")
        ]]
        btn2 = [[
            InlineKeyboardButton('JOIN CHANNEL ', url=link.invite_link),
            InlineKeyboardButton("VIEW STATUS", url=f"{query.message.link}")
        ]]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Sᴇᴛ ᴛᴏ Nᴏᴛ Aᴠᴀɪʟᴀʙʟᴇ Iɴ Hɪɴᴅɪ !")
            content = extract_request_content(query.message.text)
            try:
                await client.send_message(
                    chat_id=int(from_user),
                    text=(
                        f"<code>Hey </code> {user.mention}\n\n"
                        f" <code>Yᴏᴜʀ Rᴇǫᴜᴇsᴛ </code> - <code>{content}</code> - <code>is not available in Hindi right now . So our moderators can't upload it </code>\n\n"
                        f"#Hindi_Not_Available ❌</b>"
                    ),
                    reply_markup=InlineKeyboardMarkup(btn2)
                )
            except UserIsBlocked:
                await client.send_message(
                    chat_id=int(SUPPORT_CHAT_ID),
                    text=(
                        f"<u>Hey {user.mention}</u>\n\n"
                        f"<b><code>{content}</code> - <code>is not available in Hindi right now . So our moderators can't upload it </code>\n\n"
                        f"#Hindi_Not_Available ❌\n\n"
                        f"<small>Bʟᴏᴄᴋᴇᴅ? Unblock the bot to receive messages.</small></b>"
                    ),
                    reply_markup=InlineKeyboardMarkup(btn2)
                )
        else:
            await query.answer("<code> You don't have sufficiant rights to do this !</code>", show_alert=True)

    elif query.data.startswith("uploaded"):
        ident, from_user = query.data.split("#")
        btn = [[
            InlineKeyboardButton(
                "🟢 UPLOADED 🟢", callback_data=f"upalert#{from_user}")
        ]]
        btn2 = [[
            InlineKeyboardButton('JOIN CHANNEL ', url=link.invite_link),
            InlineKeyboardButton("VIEW STATUS", url=f"{query.message.link}")
        ], [
            InlineKeyboardButton("🔍 SEARCH HERE 🔎", url=GRP_LNK)
        ]]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Sᴇᴛ ᴛᴏ Uᴘʟᴏᴀᴅᴇᴅ !")
            content = extract_request_content(query.message.text)
            try:
                await client.send_message(
                    chat_id=int(from_user),
                    text=(
                        f"<b>Hᴇʏ {user.mention},\n\n"
                        f"<u>{content}</u> Yᴏᴜʀ ʀᴇǫᴜᴇꜱᴛ ʜᴀꜱ ʙᴇᴇɴ ᴜᴘʟᴏᴀᴅᴇᴅ ʙʏ ᴏᴜʀ ᴍᴏᴅᴇʀᴀᴛᴏʀs.\n"
                        f"Kɪɴᴅʟʏ sᴇᴀʀᴄʜ ɪɴ ᴏᴜʀ Gʀᴏᴜᴘ.</b>\n\n"
                        f"#Uᴘʟᴏᴀᴅᴇᴅ✅"
                    ),
                    reply_markup=InlineKeyboardMarkup(btn2)
                )
            except UserIsBlocked:
                await client.send_message(
                    chat_id=int(SUPPORT_CHAT_ID),
                    text=(
                        f"<u>{content}</u>\n\n"
                        f"<b>Hᴇʏ {user.mention}, Yᴏᴜʀ ʀᴇǫᴜᴇꜱᴛ ʜᴀꜱ ʙᴇᴇɴ ᴜᴘʟᴏᴀᴅᴇᴅ ʙʏ ᴏᴜʀ ᴍᴏᴅᴇʀᴀᴛᴏʀs."
                        f"Kɪɴᴅʟʏ sᴇᴀʀᴄʜ ɪɴ ᴏᴜʀ Gʀᴏᴜᴘ.</b>\n\n"
                        f"#Uᴘʟᴏᴀᴅᴇᴅ✅\n\n"
                        f"<small>Bʟᴏᴄᴋᴇᴅ? Uɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ʀᴇᴄᴇɪᴠᴇ ᴍᴇꜱꜱᴀɢᴇꜱ.</small>"
                    ),
                    reply_markup=InlineKeyboardMarkup(btn2)
                )
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

    elif query.data.startswith("already_available"):
        ident, from_user = query.data.split("#")
        btn = [[
            InlineKeyboardButton("♻️ ALREADY AVAILABLE ♻️",
                                 callback_data=f"alalert#{from_user}")
        ]]
        btn2 = [[
            InlineKeyboardButton('JOIN CHANNEL', url=link.invite_link),
            InlineKeyboardButton("VIEW STATUS", url=f"{query.message.link}")
        ], [
            InlineKeyboardButton("🔍 SEARCH HERE 🔎", url=GRP_LNK)
        ]]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Sᴇᴛ ᴛᴏ Aʟʀᴇᴀᴅʏ Aᴠᴀɪʟᴀʙʟᴇ !")
            content = extract_request_content(query.message.text)
            try:
                await client.send_message(
                    chat_id=int(from_user),
                    text=(
                        f"<b>Hᴇʏ {user.mention},\n\n"
                        f"<u>{content}</u> Yᴏᴜʀ ʀᴇǫᴜᴇꜱᴛ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴀᴠᴀɪʟᴀʙʟᴇ ɪɴ ᴏᴜʀ ʙᴏᴛ'ꜱ ᴅᴀᴛᴀʙᴀꜱᴇ.\n"
                        f"Kɪɴᴅʟʏ sᴇᴀʀᴄʜ ɪɴ ᴏᴜʀ Gʀᴏᴜᴘ.</b>\n\n"
                        f"#Aᴠᴀɪʟᴀʙʟᴇ 💗"
                    ),
                    reply_markup=InlineKeyboardMarkup(btn2)
                )
            except UserIsBlocked:
                await client.send_message(
                    chat_id=int(SUPPORT_CHAT_ID),
                    text=(
                        f"<b>Hᴇʏ {user.mention},\n\n"
                        f"<u>{content}</u> Yᴏᴜʀ ʀᴇǫᴜᴇꜱᴛ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴀᴠᴀɪʟᴀʙʟᴇ ɪɴ ᴏᴜʀ ʙᴏᴛ'ꜱ ᴅᴀᴛᴀʙᴀꜱᴇ.\n"
                        f"Kɪɴᴅʟʏ sᴇᴀʀᴄʜ ɪɴ ᴏᴜʀ Gʀᴏᴜᴘ.</b>\n\n"
                        f"#Aᴠᴀɪʟᴀʙʟᴇ 💗\n"
                        f"<small>Bʟᴏᴄᴋᴇᴅ? Uɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ʀᴇᴄᴇɪᴠᴇ ᴍᴇꜱꜱᴀɢᴇꜱ.</small></i>"
                    ),
                    reply_markup=InlineKeyboardMarkup(btn2)
                )
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

    elif query.data.startswith("alalert"):
        ident, from_user = query.data.split("#")
        if int(query.from_user.id) == int(from_user):
            user = await client.get_users(from_user)
            await query.answer(
                f"Hᴇʏ {user.first_name}, Yᴏᴜʀ ʀᴇǫᴜᴇꜱᴛ ɪꜱ Aʟʀᴇᴀᴅʏ Aᴠᴀɪʟᴀʙʟᴇ ✅",
                show_alert=True
            )
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴇɴᴛ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜɪs ❌", show_alert=True)

    elif query.data.startswith("upalert"):
        ident, from_user = query.data.split("#")
        if int(query.from_user.id) == int(from_user):
            user = await client.get_users(from_user)
            await query.answer(
                f"Hᴇʏ {user.first_name}, Yᴏᴜʀ ʀᴇǫᴜᴇꜱᴛ ɪꜱ Uᴘʟᴏᴀᴅᴇᴅ 🔼",
                show_alert=True
            )
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴇɴᴛ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜɪs ❌", show_alert=True)

    elif query.data.startswith("unalert"):
        ident, from_user = query.data.split("#")
        if int(query.from_user.id) == int(from_user):
            user = await client.get_users(from_user)
            await query.answer(
                f"Hᴇʏ {user.first_name}, Yᴏᴜʀ ʀᴇǫᴜᴇꜱᴛ ɪꜱ Uɴᴀᴠᴀɪʟᴀʙʟᴇ ⚠️",
                show_alert=True
            )
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴇɴᴛ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜɪs ❌", show_alert=True)

    elif query.data.startswith("hnalert"):
        ident, from_user = query.data.split("#")  # Hindi Not Available
        if int(query.from_user.id) == int(from_user):
            user = await client.get_users(from_user)
            await query.answer(
                f"Hᴇʏ {user.first_name}, Tʜɪꜱ ɪꜱ Nᴏᴛ Aᴠᴀɪʟᴀʙʟᴇ ɪɴ Hɪɴᴅɪ ❌",
                show_alert=True
            )
        else:
            await query.answer("Nᴏᴛ ᴀʟʟᴏᴡᴇᴅ — ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴛʜᴇ ʀᴇǫᴜᴇꜱᴛᴇʀ ❌", show_alert=True)

    elif query.data.startswith("nralert"):
        ident, from_user = query.data.split("#")  # Not Released
        if int(query.from_user.id) == int(from_user):
            user = await client.get_users(from_user)
            await query.answer(
                f"Hᴇʏ {user.first_name}, Tʜᴇ Mᴏᴠɪᴇ/ꜱʜᴏᴡ ɪꜱ Nᴏᴛ Rᴇʟᴇᴀꜱᴇᴅ Yᴇᴛ 🆕",
                show_alert=True
            )
        else:
            await query.answer("Yᴏᴜ ᴄᴀɴ'ᴛ ᴅᴏ ᴛʜɪꜱ ᴀꜱ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴛʜᴇ ᴏʀɪɢɪɴᴀʟ ʀᴇǫᴜᴇꜱᴛᴇʀ ❌", show_alert=True)

    elif query.data.startswith("wsalert"):
        ident, from_user = query.data.split("#")  # Wrong Spelling
        if int(query.from_user.id) == int(from_user):
            user = await client.get_users(from_user)
            await query.answer(
                f"Hᴇʏ {user.first_name}, Yᴏᴜʀ Rᴇǫᴜᴇꜱᴛ ᴡᴀꜱ ʀᴇᴊᴇᴄᴛᴇᴅ ᴅᴜᴇ ᴛᴏ ᴡʀᴏɴɢ sᴘᴇʟʟɪɴɢ ❗",
                show_alert=True
            )
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ sᴇᴇ ᴛʜɪꜱ ❌", show_alert=True)

    elif TgeData.startswith("generate_stream_link"):
        _, file_id = TgeData.split(":")
        try:
            user_id = query.from_user.id
            username = query.from_user.mention
            log_msg = await client.send_cached_media(chat_id=BIN_CHANNEL, file_id=file_id,)
            fileName = {quote_plus(get_name(log_msg))}
            tge_stream = f"{URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
            tge_download = f"{URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
            xo = await query.message.reply_text(f'💘')
            await asyncio.sleep(1)
            await xo.delete()
            await log_msg.reply_text(
                text=f"•• ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ ꜰᴏʀ ɪᴅ #{user_id} \n•• ᴜꜱᴇʀɴᴀᴍᴇ : {username} \n\n•• ᖴᎥᒪᗴ Nᗩᗰᗴ : {fileName}",
                quote=True,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚀 Fast Download 🚀", url=tge_download),  # we download Link
                                                    InlineKeyboardButton('🖥️ Watch online 🖥️', url=tge_stream)]])  # web stream Link
            )
            tgecinezone = await query.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("🚀 Download ", url=tge_download),
                        InlineKeyboardButton('🖥️ Watch ', url=tge_stream)
                    ],
                    [
                        InlineKeyboardButton('📌 ᴊᴏɪɴ ᴜᴘᴅᴀᴛᴇꜱ ᴄʜᴀɴɴᴇʟ 📌', url=UPDATE_CHNL_LNK)
                    ]
                ])
            )
            await asyncio.sleep(DELETE_TIME)
            await tgecinezone.delete()
            return
        except Exception as e:
            print(e)
            await query.answer(f"⚠️ SOMETHING WENT WRONG STREAM LINK  \n\n{e}", show_alert=True)
            return
        
        
    elif query.data == "prestream":
        await query.answer(text=script.PRE_STREAM_ALERT, show_alert=True)
        tgecinezone = await client.send_photo(
            chat_id=query.message.chat.id,
            photo="https://i.ibb.co/whf8xF7j/photo-2025-07-26-10-42-46-7531339305176793100.jpg", 
            caption=script.PRE_STREAM,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Buy Premium 🚀", callback_data="premium_info")]
            ])
        )
        await asyncio.sleep(DELETE_TIME)
        await tgecinezone.delete()


    elif query.data == "pagesn1":
        await query.answer(text=script.PAGE_TXT, show_alert=True)

    elif query.data == "sinfo":
        await query.answer(text=script.SINFO, show_alert=True)

    elif query.data == "start":
        buttons = [[
                    InlineKeyboardButton('🔰 ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ 🔰', url=f'http://telegram.me/{temp.U_NAME}?startgroup=true')
                ],[
                    InlineKeyboardButton(' ʜᴇʟᴘ 📢', callback_data='help'),
                    InlineKeyboardButton(' ᴀʙᴏᴜᴛ 📖', callback_data='about')
                ],[
                    InlineKeyboardButton('ᴛᴏᴘ sᴇᴀʀᴄʜɪɴɢ ⭐', callback_data="topsearch"),
                     InlineKeyboardButton('ᴜᴘɢʀᴀᴅᴇ 🎟', callback_data="premium_info"),
                ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        current_time = datetime.now(pytz.timezone(TIMEZONE))
        curr_time = current_time.hour        
        if curr_time < 12:
            gtxt = "<code>GOOD MORNING 🌞</code>" 
        elif curr_time < 17:
            gtxt = "<code>GOOD AFTERNOON 🌓</code>" 
        elif curr_time < 21:
            gtxt = "<code>GOOD EVENING 🌘</code>"
        else:
            gtxt = "<code>GOOD NIGHT 🌑</code>"
        try:
            await client.edit_message_media(
                query.message.chat.id, 
                query.message.id, 
                InputMediaPhoto(random.choice(PICS))
            )
        except Exception as e:    
            pass
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention, gtxt, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        await query.answer(MSG_ALRT)

    elif query.data == "donation":
        buttons = [[
                InlineKeyboardButton('🌲 Sᴇɴᴅ Dᴏɴᴀᴛᴇ Sᴄʀᴇᴇɴsʜᴏᴛ Hᴇʀᴇ', url=OWNER_LNK)
            ],[
                InlineKeyboardButton('⇍ BACK ⇏', callback_data='about')
            ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(text="● ◌ ◌")
        await query.message.edit_text(text="● ● ◌")
        await query.message.edit_text(text="● ● ●")
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto('https://graph.org/file/99eebf5dbe8a134f548e0.jpg')
        )
        await query.message.edit_text(
            text=script.TGEBOTZ_DONATION.format(query.from_user.mention, QR_CODE, OWNER_UPI_ID),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "help":
        buttons = [[
            InlineKeyboardButton('⇋ BACK TO HOME ⇋', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.HELP_TXT, 
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "about":
        buttons = [[
            InlineKeyboardButton('‼️ DISCLAIMER ‼️', callback_data='disclaimer'),
            InlineKeyboardButton ('🪔SOURCE ', callback_data='source'),
        ],[
            InlineKeyboardButton('DONATION 💰', callback_data='donation'), 
        ],[
            InlineKeyboardButton('⇋ BACK TO HOME⇋', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ABOUT_TXT.format(temp.U_NAME, temp.B_NAME, OWNER_LNK),
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "give_trial":
        try:
            user_id = query.from_user.id
            has_free_trial = await db.check_trial_status(user_id)
            if has_free_trial:
                await query.answer(
                    "🚸 ʏᴏᴜ'ᴠᴇ ᴀʟʀᴇᴀᴅʏ ᴄʟᴀɪᴍᴇᴅ ʏᴏᴜʀ ꜰʀᴇᴇ ᴛʀɪᴀʟ ᴏɴᴄᴇ !\n\n📌 ᴄʜᴇᴄᴋᴏᴜᴛ ᴏᴜʀ ᴘʟᴀɴꜱ ʙʏ : /plan",
                    show_alert=True
                )
                return
            else:            
                await db.give_free_trial(user_id)
                await query.answer("✅ Trial activated!", show_alert=True)

                msg = await client.send_photo(
                    chat_id=query.message.chat.id,
                    photo="https://i.ibb.co/0jC8MSDZ/photo-2025-07-26-10-42-36-7531339283701956616.jpg", 
                    caption=(
                        "<b>🥳 ᴄᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴꜱ\n\n"
                        "🎉 ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ꜰʀᴇᴇ ᴛʀᴀɪʟ ꜰᴏʀ <u>5 ᴍɪɴᴜᴛᴇs</u> ꜰʀᴏᴍ ɴᴏᴡ !\n\n"
                        "ɴᴇᴇᴅ ᴘʀᴇᴍɪᴜᴍ 👉🏻 /plan</b>"
                    ),
                    parse_mode=enums.ParseMode.HTML,
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🚀 Buy Premium 🚀", callback_data="premium_info")
                    ]])
                )
                await asyncio.sleep(DELETE_TIME)
                return await msg.delete()
        except Exception as e:
            logging.exception("Error in give_trial callback")



    elif query.data == "source":
        buttons = [[
            InlineKeyboardButton('TGEBOTZ 📜', url='https://github.com'),
            InlineKeyboardButton('⇋ BACK ⇋', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.SOURCE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "ref_point":
        await query.answer(f'You Have: {referdb.get_refer_points(query.from_user.id)} Refferal points.', show_alert=True)
    
    elif query.data == "disclaimer":
            btn = [[
                    InlineKeyboardButton("⇋ BACK ⇋", callback_data="about")
                  ]]
            reply_markup = InlineKeyboardMarkup(btn)
            await query.message.edit_text(
                text=(script.DISCLAIMER_TXT),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML 
            )

    elif query.data == "premium_info":
        try:
            btn = [[
                InlineKeyboardButton('•BUY PREMIUM •', callback_data='buy_info'),
            ],[
                InlineKeyboardButton('•REFER FRIENDS ', callback_data='reffff'),
                InlineKeyboardButton('FREE TRIAL •', callback_data='give_trial')
            ],[            
                InlineKeyboardButton('⇋ BACK TO HOME ⇋', callback_data='start')
            ]]
            reply_markup = InlineKeyboardMarkup(btn)                        
            await client.edit_message_media(
                chat_id=query.message.chat.id,
                message_id=query.message.id,
                media=InputMediaPhoto(media=SUBSCRIPTION, caption=script.BPREMIUM_TXT, parse_mode=enums.ParseMode.HTML),
                reply_markup=reply_markup
            )
        except Exception as e:
            logging.exception("Exception in 'premium_info' callback")


    elif query.data == "buy_info":
        try:
            btn = [[ 
                InlineKeyboardButton('ꜱᴛᴀʀ', callback_data='star_info'),
                InlineKeyboardButton('ᴜᴘɪ', callback_data='upi_info')
            ],[
                InlineKeyboardButton('⇋ ʙᴀᴄᴋ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ ⇋', callback_data='premium_info')
            ]]
            reply_markup = InlineKeyboardMarkup(btn)
            await client.edit_message_media(
                chat_id=query.message.chat.id,
                message_id=query.message.id,
                media=InputMediaPhoto(media=SUBSCRIPTION, caption=script.PREMIUM_TEXT, parse_mode=enums.ParseMode.HTML),
                reply_markup=reply_markup
            )
        except Exception as e:
            logging.exception("Exception in 'buy_info' callback")

    elif query.data == "upi_info":
        try:
            btn = [[ 
                InlineKeyboardButton('• ꜱᴇɴᴅ  ᴘᴀʏᴍᴇɴᴛ ꜱᴄʀᴇᴇɴꜱʜᴏᴛ •', url=OWNER_LNK),
            ],[
                InlineKeyboardButton('⇋ ʙᴀᴄᴋ ⇋', callback_data='buy_info')
            ]]
            reply_markup = InlineKeyboardMarkup(btn)
            await client.edit_message_media(
                chat_id=query.message.chat.id,
                message_id=query.message.id,
                media=InputMediaPhoto(media=SUBSCRIPTION, caption=script.PREMIUM_UPI_TEXT.format(OWNER_UPI_ID), parse_mode=enums.ParseMode.HTML),
                reply_markup=reply_markup
            )
        except Exception as e:
            logging.exception("Exception in 'upi_info' callback")

    elif query.data == "star_info":
        try:
            btn = [
                InlineKeyboardButton(f"{stars}⭐", callback_data=f"buy_{stars}")
                for stars, days in STAR_PREMIUM_PLANS.items()
            ]
            buttons = [btn[i:i + 2] for i in range(0, len(btn), 2)]
            buttons.append([InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data="buy_info")])
            reply_markup = InlineKeyboardMarkup(buttons)
            await client.edit_message_media(
                chat_id=query.message.chat.id,
                message_id=query.message.id,
                media=InputMediaPhoto(media=SUBSCRIPTION, caption=script.PREMIUM_STAR_TEXT, parse_mode=enums.ParseMode.HTML),
                reply_markup=reply_markup
            )
        except Exception as e:
            logging.exception("Exception in 'star' callback")


    elif query.data.startswith("grp_pm"):
        _, grp_id = query.data.split("#")
        user_id = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), user_id):
            return await query.answer(script.NT_ADMIN_ALRT_TXT, show_alert=True)

        btn = await group_setting_buttons(int(grp_id))
        tge = await client.get_chat(int(grp_id))
        await query.message.edit(text=f"ᴄʜᴀɴɢᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘ ꜱᴇᴛᴛɪɴɢꜱ ✅\nɢʀᴏᴜᴘ ɴᴀᴍᴇ - '{tge.title}'</b>⚙", reply_markup=InlineKeyboardMarkup(btn))

    elif query.data.startswith("removegrp"):
        user_id = query.from_user.id
        data = query.data
        grp_id = int(data.split("#")[1])
        if not await is_check_admin(client, grp_id, query.from_user.id):
            return await query.answer(script.NT_ADMIN_ALRT_TXT, show_alert=True)
        await db.remove_group_connection(grp_id, user_id)
        await query.answer("Group removed from your connections.", show_alert=True)
        connected_groups = await db.get_connected_grps(user_id)
        if not connected_groups:
            await query.edit_message_text("Nᴏ Cᴏɴɴᴇᴄᴛᴇᴅ Gʀᴏᴜᴘs Fᴏᴜɴᴅ .")
            return
        group_list = []
        for group in connected_groups:
            try:
                Chat = await client.get_chat(group)
                group_list.append([
                    InlineKeyboardButton(
                        text=Chat.title, callback_data=f"grp_pm#{Chat.id}")
                ])
            except Exception as e:
                print(f"Error In PM Settings Button - {e}")
                pass
        await query.edit_message_text(
            "⚠️ ꜱᴇʟᴇᴄᴛ ᴛʜᴇ ɢʀᴏᴜᴘ ᴡʜᴏꜱᴇ ꜱᴇᴛᴛɪɴɢꜱ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴄʜᴀɴɢᴇ.\n\n"
            "ɪꜰ ʏᴏᴜʀ ɢʀᴏᴜᴘ ɪꜱ ɴᴏᴛ ꜱʜᴏᴡɪɴɢ ʜᴇʀᴇ,\n"
            "ᴜꜱᴇ /reload ɪɴ ᴛʜᴀᴛ ɢʀᴏᴜᴘ ᴀɴᴅ ɪᴛ ᴡɪʟʟ ᴀᴘᴘᴇᴀʀ ʜᴇʀᴇ.",
            reply_markup=InlineKeyboardMarkup(group_list)
        )

    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            await query.answer(script.NT_ADMIN_ALRT_TXT, show_alert=True)
            return
        if status == "True":
            await save_group_settings(int(grp_id), set_type, False)
            await query.answer("ᴏꜰꜰ ✗")
        else:
            await save_group_settings(int(grp_id), set_type, True)
            await query.answer("ᴏɴ ✓")
        settings = await get_settings(int(grp_id))
        if settings is not None:
            btn = await group_setting_buttons(int(grp_id))
            reply_markup = InlineKeyboardMarkup(btn)
            await query.message.edit_reply_markup(reply_markup)
    await query.answer(MSG_ALRT)


async def auto_filter(client, msg, spoll=False):
    curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    if not spoll:
        message = msg
        if message.text.startswith("/"):
            return
        if re.findall(r"((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if len(message.text) < 100:
            search = message.text
            search = search.lower()
            m = await message.reply_text(f'**🔎 Searching** `{search}`', reply_to_message_id=message.id)
            find = search.split(" ")
            search = ""
            removes = ["in", "upload", "series", "full",
                       "horror", "thriller", "mystery", "print", "file"]
            for x in find:
                if x in removes:
                    continue
                else:
                    search = search + x + " "
            search = re.sub(r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|bro|bruh|broh|helo|that|find|dubbed|link|venum|iruka|pannunga|pannungga|anuppunga|anupunga|anuppungga|anupungga|film|undo|kitti|kitty|tharu|kittumo|kittum|movie|any(one)|with\ssubtitle(s)?)", "", search, flags=re.IGNORECASE)
            search = re.sub(r"\s+", " ", search).strip()
            search = search.replace("-", " ")
            search = search.replace(":", "")
            files, offset, total_results = await get_search_results(message.chat.id, search, offset=0, filter=True)
            settings = await get_settings(message.chat.id)
            if not files:
                if settings["spell_check"]:
                    ai_sts = await m.edit('🤖 Please Wait, Ai is checking yoir spelling...')
                    is_misspelled = await ai_spell_check(chat_id=message.chat.id, wrong_name=search)
                    if is_misspelled:
                        await ai_sts.edit(f'✅Ai Suggested: <code>{is_misspelled}</code>\n🔍 Searching for it...')
                        message.text = is_misspelled
                        await ai_sts.delete()
                        return await auto_filter(client, message)
                    await ai_sts.delete()
                    return await advantage_spell_chok(client, message)
                else:
                    await m.delete()
                    return await advantage_spell_chok(client, message)
        else:
            return
    else:
        message = msg.message.reply_to_message
        search, files, offset, total_results = spoll
        m = await message.reply_text(f'**🔎 Searching** `{search}`', reply_to_message_id=message.id)
        settings = await get_settings(message.chat.id)
        await msg.message.delete()
    key = f"{message.chat.id}-{message.id}"
    FRESH[key] = search
    temp.GETALL[key] = files
    temp.SHORT[message.from_user.id] = message.chat.id
    if settings.get('button'):
        btn = [
            [
                InlineKeyboardButton(text=f"🔗 {get_size(file.file_size)} ≽ " + clean_filename(
                    file.file_name), callback_data=f'file#{file.file_id}'),
            ]
            for file in files
        ]
        btn.insert(0,
                   [
                       InlineKeyboardButton(
                           f'Quality', callback_data=f"qualities#{key}"),
                       InlineKeyboardButton(
                           "Language", callback_data=f"languages#{key}"),
                       InlineKeyboardButton(
                           "Season",  callback_data=f"seasons#{key}")
                   ]
                   )
        btn.insert(0,
                   [
                       InlineKeyboardButton(
                           " Remove Ads 🎫", url=f"https://t.me/{temp.U_NAME}?start=premium"),
                       InlineKeyboardButton(
                           "Send All", callback_data=f"sendfiles#{key}")

                   ])
    else:
        btn = []
        btn.insert(0,
                   [
                       InlineKeyboardButton(
                           f'Quality', callback_data=f"qualities#{key}"),
                       InlineKeyboardButton(
                           "Language", callback_data=f"languages#{key}"),
                       InlineKeyboardButton(
                           "Season",  callback_data=f"seasons#{key}")
                   ]
                   )
        btn.insert(0,
                   [
                       InlineKeyboardButton(
                           "🎫 Remove Ads 🎫", url=f"https://t.me/{temp.U_NAME}?start=premium"),
                       InlineKeyboardButton(
                           "Send All", callback_data=f"sendfiles#{key}")
                   ])

    if offset != "":
        req = message.from_user.id if message.from_user else 0
        try:
            if settings['max_btn']:
                btn.append(
                    [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(
                        text=f"1/{math.ceil(int(total_results)/10)}", callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{offset}")]
                )
            else:
                btn.append(
                    [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(
                        text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}", callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{offset}")]
                )
        except KeyError:
            await save_group_settings(message.chat.id, 'max_btn', True)
            btn.append(
                [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(
                    text=f"1/{math.ceil(int(total_results)/10)}", callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{offset}")]
            )
    else:
        btn.append([InlineKeyboardButton(
            text="↭ ɴᴏ ᴍᴏʀᴇ ᴘᴀɢᴇꜱ ᴀᴠᴀɪʟᴀʙʟᴇ ↭", callback_data="pages")])

    imdb = await get_poster(search, file=(files[0]).file_name) if settings["imdb"] else None

    cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - \
        timedelta(hours=curr_time.hour, minutes=curr_time.minute,
                  seconds=(curr_time.second+(curr_time.microsecond/1000000)))
    remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
    TEMPLATE = script.IMDB_TEMPLATE_TXT
    settings = await get_settings(message.chat.id)
    if settings['template']:
        TEMPLATE = settings['template']

    if imdb:
        cap = TEMPLATE.format(
            query=search,
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box_office=imdb['box_office'],
            localized_title=imdb['localized_title'],
            kind=imdb['kind'],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url'],
            **locals()
        )
        temp.IMDB_CAP[message.from_user.id] = cap
        if not settings.get('button'):
            cap += "\n\n<b>🧾 <u>Your Requested Files Are Here</u> 👇</b>"
            for idx, file in enumerate(files, start=1):
                cap += f"<b>\n{idx}.📁 - <a href='https://telegram.me/{temp.U_NAME}?start=file_{message.chat.id}_{file.file_id}'>[{get_size(file.file_size)}] {clean_filename(file.file_name)}\n</a></b>"
    else:
        if settings.get('button'):
            cap = (
    f"🔍 <b>Search:</b> <code>{search}</code>\n"
    f"📂 <b>Total Files:</b> <code>{total_results}</code>\n"
    f"⏱ <b>Processed In:</b> <code>{remaining_seconds} Sec</code>\n\n"
    f"👤 Requested by: {message.from_user.mention}\n"
    f"⚡ Powered by: {message.chat.title or temp.B_LINK or 'TgeBotz'}\n\n"
    f"🗃️ <u>Available files:</u> 👇\n\n"
            )
        else:
            cap = (
    f"🔍 <b>Search:</b> <code>{search}</code>\n"
    f"📂 <b>Total Files:</b> <code>{total_results}</code>\n"
    f"⏱ <b>Processed In:</b> <code>{remaining_seconds} Sec</code>\n\n"
    f"👤 Requested by: {message.from_user.mention}\n"
    f"⚡ Powered by: {message.chat.title or temp.B_LINK or 'TgeBotz'}\n\n"
    f"🗃️ <u>Available files:</u> 👇\n\n"
)

            for idx, file in enumerate(files, start=1):
                cap += f"<b>\n{idx}.📁 -  <a href='https://telegram.me/{temp.U_NAME}?start=file_{message.chat.id}_{file.file_id}'>[{get_size(file.file_size)}] {clean_filename(file.file_name)}\n</a></b>"
    if imdb and imdb.get('poster'):
        try:
            hehe = await message.reply_photo(photo=imdb.get('poster'), caption=cap, reply_markup=InlineKeyboardMarkup(btn), parse_mode=enums.ParseMode.HTML)
            await m.delete()
            try:
                if settings['auto_delete']:
                    await asyncio.sleep(DELETE_TIME)
                    await hehe.delete()
                    await message.delete()
            except KeyError:
                await save_group_settings(message.chat.id, 'auto_delete', True)
                await asyncio.sleep(DELETE_TIME)
                await hehe.delete()
                await message.delete()
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")
            hmm = await message.reply_photo(photo=poster, caption=cap, reply_markup=InlineKeyboardMarkup(btn), parse_mode=enums.ParseMode.HTML)
            await m.delete()
            try:
                if settings['auto_delete']:
                    await asyncio.sleep(DELETE_TIME)
                    await hmm.delete()
                    await message.delete()
            except KeyError:
                await save_group_settings(message.chat.id, 'auto_delete', True)
                await asyncio.sleep(DELETE_TIME)
                await hmm.delete()
                await message.delete()
        except Exception as e:
            logger.exception(e)
            dxb = await message.reply_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), parse_mode=enums.ParseMode.HTML)
            try:
                if settings['auto_delete']:
                    await asyncio.sleep(DELETE_TIME)
                    await dxb.delete()
                    await message.delete()
            except KeyError:
                await save_group_settings(message.chat.id, 'auto_delete', True)
                await asyncio.sleep(DELETE_TIME)
                await dxb.delete()
                await message.delete()
    else:
        dxb = await message.reply_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)
        await m.delete()
        try:
            if settings['auto_delete']:
                await asyncio.sleep(DELETE_TIME)
                await dxb.delete()
                await message.delete()
        except KeyError:
            await save_group_settings(message.chat.id, 'auto_delete', True)
            await asyncio.sleep(DELETE_TIME)
            await dxb.delete()
            await message.delete()


async def ai_spell_check(chat_id, wrong_name):
    async def search_movie(wrong_name):
        search_results = imdb.search_movie(wrong_name)
        movie_list = [movie['title'] for movie in search_results]
        return movie_list
    movie_list = await search_movie(wrong_name)
    if not movie_list:
        return
    for _ in range(5):
        closest_match = process.extractOne(wrong_name, movie_list)
        if not closest_match or closest_match[1] <= 80:
            return
        movie = closest_match[0]
        files, _, _ = await get_search_results(chat_id=chat_id, query=movie)
        if files:
            return movie
        movie_list.remove(movie)


async def advantage_spell_chok(client, message):
    mv_id = message.id
    search = message.text
    chat_id = message.chat.id
    settings = await get_settings(chat_id)
    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "", message.text, flags=re.IGNORECASE)
    query = query.strip() + " movie"
    try:
        movies = await get_poster(search, bulk=True)
    except:
        k = await message.reply(script.I_CUDNT.format(message.from_user.mention))
        await asyncio.sleep(60)
        await k.delete()
        try:
            await message.delete()
        except:
            pass
        return
    if not movies:
        google = search.replace(" ", "+")
        button = [[InlineKeyboardButton(
            "🔍 CHECK SPELLING ON GOOGLE 🔍", url=f"https://www.google.com/search?q={google}")]]
        k = await message.reply_text(text=script.I_CUDNT.format(search), reply_markup=InlineKeyboardMarkup(button))
        await asyncio.sleep(60)
        await k.delete()
        try:
            await message.delete()
        except:
            pass
        return
    user = message.from_user.id if message.from_user else 0
    buttons = [
        [InlineKeyboardButton(text=movie.get('title'), callback_data=f"spol#{movie.movieID}#{user}")
         ] for movie in movies]

    buttons.append([InlineKeyboardButton(
        text="🚫 CLOSE 🚫", callback_data='close_data')])
    d = await message.reply_text(text=script.CUDNT_FND.format(message.from_user.mention), reply_markup=InlineKeyboardMarkup(buttons), reply_to_message_id=message.id)
    await asyncio.sleep(60)
    await d.delete()
    try:
        await message.delete()
    except:
        pass
