import html
import logging

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database.request_db import request_db
from info import ADMINS, GRP_LNK, LOG_CHANNEL

logger = logging.getLogger(__name__)


def _is_admin(user_id: int) -> bool:
    return user_id in [admin for admin in ADMINS if isinstance(admin, int)]


def _extract_title(query) -> str:
    message = query.message
    if message.reply_to_message and message.reply_to_message.text:
        return message.reply_to_message.text
    text = message.text or message.caption or ""
    for prefix in ("Movie not found:", "Couldn't find", "Search:"):
        if prefix.lower() in text.lower():
            text = text.split(":", 1)[-1]
    return text


@Client.on_message(filters.command("request"))
async def request_movie_command(client, message):
    title = " ".join(message.command[1:]).strip()
    if not title:
        return await message.reply_text(
            "<b>Usage:</b> <code>/request Movie Name</code>\n\n"
            "Example: <code>/request Premalu 2024</code>"
        )

    created, request = await request_db.create_request(
        user_id=message.from_user.id,
        user_name=message.from_user.first_name,
        title=title,
        chat_id=message.chat.id,
        message_id=message.id,
    )
    if not created:
        return await message.reply_text(
            f"⚠️ <b>This request is already pending.</b>\n\n🎬 <code>{html.escape(request['title'])}</code>"
        )

    await message.reply_text(
        "✅ <b>Movie request submitted!</b>\n\n"
        f"🎬 <code>{html.escape(request['title'])}</code>\n"
        "🔔 You will be notified after the admin updates it."
    )
    try:
        await client.send_message(
            LOG_CHANNEL,
            "#MOVIE_REQUEST\n\n"
            f"👤 {message.from_user.mention}\n"
            f"🆔 <code>{message.from_user.id}</code>\n"
            f"🎬 <code>{html.escape(request['title'])}</code>",
        )
    except Exception as exc:
        logger.warning("Unable to log movie request: %s", exc)


@Client.on_callback_query(filters.regex(r"^movie_request$"))
async def request_movie_callback(client, query):
    if not query.from_user:
        return await query.answer("User information unavailable.", show_alert=True)

    title = request_db.normalize_title(_extract_title(query))
    if not title:
        return await query.answer("Please use /request Movie Name", show_alert=True)

    created, request = await request_db.create_request(
        user_id=query.from_user.id,
        user_name=query.from_user.first_name,
        title=title,
        chat_id=query.message.chat.id,
        message_id=query.message.id,
    )
    if not created:
        return await query.answer("⚠️ This request is already pending.", show_alert=True)

    await query.answer("✅ Request submitted!", show_alert=True)
    await query.message.reply_text(
        "✅ <b>Movie request submitted!</b>\n\n"
        f"🎬 <code>{html.escape(request['title'])}</code>\n"
        "🔔 You will be notified when it becomes available."
    )


@Client.on_message(filters.command("requests"))
async def pending_requests_command(client, message):
    if not message.from_user or not _is_admin(message.from_user.id):
        return await message.reply_text("🚫 This command is only for bot admins.")

    pending = await request_db.list_pending(limit=10)
    count = await request_db.pending_count()
    if not pending:
        return await message.reply_text("✅ No pending movie requests.")

    await message.reply_text(f"📥 <b>Pending requests:</b> {count}\nShowing latest {len(pending)}")
    for item in pending:
        request_id = str(item["_id"])
        text = (
            f"🎬 <b>{html.escape(item['title'])}</b>\n"
            f"👤 {html.escape(item.get('user_name', 'User'))}\n"
            f"🆔 <code>{item['user_id']}</code>"
        )
        buttons = InlineKeyboardMarkup(
            [[
                InlineKeyboardButton("✅ Available", callback_data=f"reqapprove#{request_id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reqreject#{request_id}"),
            ]]
        )
        await message.reply_text(text, reply_markup=buttons)


@Client.on_callback_query(filters.regex(r"^req(approve|reject)#"))
async def request_admin_action(client, query):
    if not query.from_user or not _is_admin(query.from_user.id):
        return await query.answer("Admins only.", show_alert=True)

    action, request_id = query.data.split("#", 1)
    status = "approved" if action == "reqapprove" else "rejected"
    request = await request_db.set_status(request_id, status, query.from_user.id)
    if not request:
        return await query.answer("Request already handled or not found.", show_alert=True)

    if status == "approved":
        user_text = (
            "✅ <b>Your requested movie is now available!</b>\n\n"
            f"🎬 <code>{html.escape(request['title'])}</code>\n"
            "Search the movie again using the button below."
        )
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔍 Search Now", url=GRP_LNK)]])
        label = "✅ APPROVED"
    else:
        user_text = (
            "❌ <b>Your movie request was not approved.</b>\n\n"
            f"🎬 <code>{html.escape(request['title'])}</code>\n"
            "Please check the spelling and request again later."
        )
        markup = None
        label = "❌ REJECTED"

    try:
        await client.send_message(request["user_id"], user_text, reply_markup=markup)
    except Exception as exc:
        logger.warning("Unable to notify requester %s: %s", request["user_id"], exc)

    await query.message.edit_text(f"{query.message.text}\n\n<b>{label}</b>")
    await query.answer("Request updated.")
