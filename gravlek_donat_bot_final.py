"""
╔══════════════════════════════════════╗
║     GRAVLEK_DONAT - Telegram Bot     ║
║     MLBB Almaz Sotish Boti           ║
╚══════════════════════════════════════╝

O'rnatish:
  pip install pyTelegramBotAPI

Ishga tushirish:
  python gravlek_donat_bot.py
"""

import telebot
from telebot import types
import json
from datetime import datetime

# ══════════════════════════════════════
#   SOZLAMALAR — O'ZINGIZ O'ZGARTIRING
# ══════════════════════════════════════

BOT_TOKEN = "8902732980:AAEH_LP74iEp7ji9qTC6CLkNyUlKTlxmkck"
ADMIN_ID   = 6040509902

# 💎 ALMAZ PAKETLARI — NARXNI O'ZINGIZ BELGILANG
PACKAGES = [
    # 🎁 BONUS PAKETLAR (1 martalik)
    {"id": 1,  "diamonds": 100,  "price": 11_000,  "label": "50+50 💎 BONUS"},
    {"id": 2,  "diamonds": 300,  "price": 32_000,  "label": "150+150 💎 BONUS"},
    {"id": 3,  "diamonds": 500,  "price": 50_000,  "label": "250+250 💎 BONUS"},
    {"id": 4,  "diamonds": 1000, "price": 105_000, "label": "500+500 💎 BONUS"},
    # 💎 OLMOS PAKETLARI
    {"id": 5,  "diamonds": 55,   "price": 11_000,  "label": "55 💎"},
    {"id": 6,  "diamonds": 86,   "price": 17_000,  "label": "86 💎"},
    {"id": 7,  "diamonds": 172,  "price": 32_000,  "label": "172 💎"},
    {"id": 8,  "diamonds": 257,  "price": 47_000,  "label": "257 💎"},
    {"id": 9,  "diamonds": 275,  "price": 49_000,  "label": "275 💎"},
    {"id": 10, "diamonds": 344,  "price": 64_000,  "label": "344 💎"},
    {"id": 11, "diamonds": 565,  "price": 105_000, "label": "565 💎"},
    {"id": 12, "diamonds": 706,  "price": 123_000, "label": "706 💎"},
    {"id": 13, "diamonds": 1412, "price": 245_000, "label": "1412 💎"},
    {"id": 14, "diamonds": 2195, "price": 370_000, "label": "2195 💎"},
    {"id": 15, "diamonds": 3688, "price": 620_000, "label": "3688 💎"},
    {"id": 16, "diamonds": 4390, "price": 730_000, "label": "4390 💎"},
    {"id": 17, "diamonds": 5532, "price": 930_000, "label": "5532 💎"},
    # 🎟 PROPUSKLAR
    {"id": 18, "diamonds": 0, "price": 20_000, "label": "🎟 Haftalik Propusk"},
    {"id": 19, "diamonds": 0, "price": 12_000, "label": "🎟 Haftalik Elitniy Propusk"},
    {"id": 20, "diamonds": 0, "price": 55_000, "label": "🎟 Oylik Elitniy Propusk"},
]

# 💳 TO'LOV KARTA RAQAMI
CARD_NUMBER = "5614 6822 1981 7402"   # O'zingizning karta raqamingiz
CARD_NAME   = "Gravlek Donat"

# ══════════════════════════════════════
#   BOT ISHGA TUSHISHI
# ══════════════════════════════════════

bot = telebot.TeleBot(BOT_TOKEN)

# Foydalanuvchi holatlari (xotira)
user_states = {}   # { user_id: { "step": ..., "pkg": ..., "player_id": ..., "server": ... } }
order_counter = [1000]  # Buyurtma raqami


def get_state(uid):
    if uid not in user_states:
        user_states[uid] = {}
    return user_states[uid]


def fmt_price(p):
    return f"{p:,}".replace(",", " ") + " so'm"


# ══════════════════════════════════════
#   /START — BOSHLASH
# ══════════════════════════════════════

@bot.message_handler(commands=["start"])
def start(msg):
    uid = msg.from_user.id
    user_states[uid] = {}

    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("💎 Almaz Sotib Olish", callback_data="buy"),
        types.InlineKeyboardButton("📋 Buyurtmalarim",     callback_data="orders"),
        types.InlineKeyboardButton("📞 Bog'lanish",        callback_data="contact"),
    )
    bot.send_message(uid,
        "🎮 *Gravlek Donat Botga Xush Kelibsiz!*\n\n"
        "✅ Tez yetkazib berish\n"
        "✅ Arzon narxlar\n"
        "✅ 100% xavfsiz\n\n"
        "Quyidan xizmatni tanlang 👇",
        parse_mode="Markdown",
        reply_markup=kb
    )


# ══════════════════════════════════════
#   PAKET TANLASH
# ══════════════════════════════════════

@bot.callback_query_handler(func=lambda c: c.data == "buy")
def show_packages(call):
    uid = call.from_user.id
    user_states[uid] = {"step": "choose_pkg"}

    kb = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for pkg in PACKAGES:
        buttons.append(
            types.InlineKeyboardButton(
                f"{pkg['label']} — {fmt_price(pkg['price'])}",
                callback_data=f"pkg_{pkg['id']}"
            )
        )
    kb.add(*buttons)
    kb.add(types.InlineKeyboardButton("🔙 Orqaga", callback_data="back_start"))

    bot.edit_message_text(
        "💎 *Paket Tanlang:*\n\n"
        "_Sizga mos paketni bosing_ 👇",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=kb
    )


# ══════════════════════════════════════
#   PAKET TANLANDI → ID SO'RASH
# ══════════════════════════════════════

@bot.callback_query_handler(func=lambda c: c.data.startswith("pkg_"))
def pkg_selected(call):
    uid = call.from_user.id
    pkg_id = int(call.data.split("_")[1])
    pkg = next(p for p in PACKAGES if p["id"] == pkg_id)

    state = get_state(uid)
    state["step"] = "enter_id"
    state["pkg"] = pkg

    bot.edit_message_text(
        f"✅ Tanlandi: *{pkg['label']}* — {fmt_price(pkg['price'])}\n\n"
        f"🎮 *Player ID* va *Server* raqamini kiriting:\n\n"
        f"📍 Qayerdan topish:\n"
        f"MLBB → Profil rasmi ustiga bosing → ID nusxalang\n\n"
        f"Formatda yozing:\n"
        f"`ID SERVER` _(masalan: 123456789 2202)_",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown"
    )


# ══════════════════════════════════════
#   ID QABUL QILISH
# ══════════════════════════════════════

@bot.message_handler(func=lambda m: get_state(m.from_user.id).get("step") == "enter_id")
def get_player_id(msg):
    uid = msg.from_user.id
    state = get_state(uid)
    parts = msg.text.strip().split()

    if len(parts) < 2:
        bot.send_message(uid,
            "❌ Noto'g'ri format!\n\n"
            "Iltimos quyidagi formatda yozing:\n"
            "`ID SERVER` _(masalan: 123456789 2202)_",
            parse_mode="Markdown"
        )
        return

    state["player_id"] = parts[0]
    state["server"]    = parts[1]
    state["step"]      = "confirm"

    pkg = state["pkg"]
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("✅ To'lovga o'tish", callback_data="pay"),
        types.InlineKeyboardButton("❌ Bekor qilish",   callback_data="cancel"),
    )

    bot.send_message(uid,
        f"📋 *Buyurtma Ma'lumotlari:*\n\n"
        f"💎 Paket:     *{pkg['label']}*\n"
        f"💰 Narx:      *{fmt_price(pkg['price'])}*\n"
        f"🆔 Player ID: `{state['player_id']}`\n"
        f"🌐 Server:    `{state['server']}`\n\n"
        f"Ma'lumotlar to'g'rimi?",
        parse_mode="Markdown",
        reply_markup=kb
    )


# ══════════════════════════════════════
#   TO'LOV BOSQICHI
# ══════════════════════════════════════

@bot.callback_query_handler(func=lambda c: c.data == "pay")
def payment_info(call):
    uid = call.from_user.id
    state = get_state(uid)
    pkg = state["pkg"]
    state["step"] = "waiting_payment"

    # Buyurtma raqami
    order_counter[0] += 1
    order_id = f"GRV-{order_counter[0]}"
    state["order_id"] = order_id

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("✅ To'lov qildim!", callback_data="paid"))
    kb.add(types.InlineKeyboardButton("❌ Bekor qilish",  callback_data="cancel"))

    bot.edit_message_text(
        f"💳 *To'lov Ma'lumotlari:*\n\n"
        f"💰 Summa:  *{fmt_price(pkg['price'])}*\n"
        f"🏦 Karta:  `{CARD_NUMBER}`\n"
        f"👤 Egasi:  {CARD_NAME}\n\n"
        f"📌 *Muhim:* To'lov izohiga buyurtma raqamini yozing:\n"
        f"`{order_id}`\n\n"
        f"To'lov qilgandan so'ng ✅ tugmasini bosing 👇",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=kb
    )


# ══════════════════════════════════════
#   TO'LOV QILINDI → ADMINGA XABAR
# ══════════════════════════════════════

@bot.callback_query_handler(func=lambda c: c.data == "paid")
def payment_done(call):
    uid = call.from_user.id
    state = get_state(uid)
    pkg   = state["pkg"]
    state["step"] = "pending"

    user = call.from_user
    username = f"@{user.username}" if user.username else f"ID: {uid}"
    now = datetime.now().strftime("%d.%m.%Y %H:%M")

    # ── Adminga xabar ──
    admin_kb = types.InlineKeyboardMarkup(row_width=2)
    admin_kb.add(
        types.InlineKeyboardButton("✅ Tasdiqlash",   callback_data=f"admin_ok_{uid}"),
        types.InlineKeyboardButton("❌ Rad etish",    callback_data=f"admin_no_{uid}"),
    )

    bot.send_message(ADMIN_ID,
        f"🔔 *YANGI BUYURTMA!*\n\n"
        f"🧾 Buyurtma:  `{state['order_id']}`\n"
        f"⏰ Vaqt:      {now}\n\n"
        f"👤 Mijoz:     {user.first_name} {username}\n"
        f"💎 Paket:     {pkg['label']}\n"
        f"💰 Summa:     {fmt_price(pkg['price'])}\n"
        f"🆔 Player ID: `{state['player_id']}`\n"
        f"🌐 Server:    `{state['server']}`\n\n"
        f"⚡ fastdonate.su dan yuborishni unutmang!",
        parse_mode="Markdown",
        reply_markup=admin_kb
    )

    # ── Mijozga xabar ──
    bot.edit_message_text(
        f"⏳ *Buyurtmangiz Qabul Qilindi!*\n\n"
        f"🧾 Raqam: `{state['order_id']}`\n\n"
        f"Almaz yetkazib berilgandan so'ng xabar olasiz.\n"
        f"Odatda *5-30 daqiqa* ichida yetkaziladi ⚡",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown"
    )


# ══════════════════════════════════════
#   ADMIN: TASDIQLASH ✅
# ══════════════════════════════════════

@bot.callback_query_handler(func=lambda c: c.data.startswith("admin_ok_"))
def admin_confirm(call):
    customer_id = int(call.data.split("_")[2])
    state = get_state(customer_id)
    pkg = state.get("pkg", {})

    # Mijozga yuborish
    bot.send_message(customer_id,
        f"✅ *Almaz Yetkazib Berildi!*\n\n"
        f"💎 {pkg.get('label','?')} hisobingizga tushdi!\n"
        f"🧾 Buyurtma: `{state.get('order_id','?')}`\n\n"
        f"Xarid uchun rahmat! 🙏\n"
        f"Do'stlaringizga ham ulashing 😊",
        parse_mode="Markdown"
    )

    # Admin xabarini yangilash
    bot.edit_message_text(
        call.message.text + "\n\n✅ *TASDIQLANDI*",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown"
    )
    user_states.pop(customer_id, None)


# ══════════════════════════════════════
#   ADMIN: RAD ETISH ❌
# ══════════════════════════════════════

@bot.callback_query_handler(func=lambda c: c.data.startswith("admin_no_"))
def admin_reject(call):
    customer_id = int(call.data.split("_")[2])
    state = get_state(customer_id)

    bot.send_message(customer_id,
        f"❌ *Buyurtma Rad Etildi*\n\n"
        f"🧾 Raqam: `{state.get('order_id','?')}`\n\n"
        f"Muammo bo'lsa admin bilan bog'laning:\n"
        f"👤 @Gravlekk_donat_bot",
        parse_mode="Markdown"
    )

    bot.edit_message_text(
        call.message.text + "\n\n❌ *RAD ETILDI*",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown"
    )
    user_states.pop(customer_id, None)


# ══════════════════════════════════════
#   BEKOR QILISH
# ══════════════════════════════════════

@bot.callback_query_handler(func=lambda c: c.data == "cancel")
def cancel(call):
    uid = call.from_user.id
    user_states.pop(uid, None)
    bot.edit_message_text(
        "❌ Bekor qilindi.\n\n/start — qayta boshlash",
        call.message.chat.id,
        call.message.message_id
    )


# ══════════════════════════════════════
#   BOG'LANISH
# ══════════════════════════════════════

@bot.callback_query_handler(func=lambda c: c.data == "contact")
def contact(call):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🔙 Orqaga", callback_data="back_start"))
    bot.edit_message_text(
        "📞 *Bog'lanish:*\n\n"
        "👤 Admin: @Gravlek_admin\n"
        "⏰ Ish vaqti: 09:00 — 23:00",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=kb
    )


@bot.callback_query_handler(func=lambda c: c.data == "back_start")
def back_start(call):
    user_states.pop(call.from_user.id, None)
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("💎 Almaz Sotib Olish", callback_data="buy"),
        types.InlineKeyboardButton("📋 Buyurtmalarim",     callback_data="orders"),
        types.InlineKeyboardButton("📞 Bog'lanish",        callback_data="contact"),
    )
    bot.edit_message_text(
        "🎮 *Gravlek Donat Botga Xush Kelibsiz!*\n\n"
        "✅ Tez yetkazib berish\n"
        "✅ Arzon narxlar\n"
        "✅ 100% xavfsiz\n\n"
        "Quyidan xizmatni tanlang 👇",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=kb
    )


@bot.callback_query_handler(func=lambda c: c.data == "orders")
def orders(call):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🔙 Orqaga", callback_data="back_start"))
    bot.edit_message_text(
        "📋 *Buyurtmalarim:*\n\n"
        "Hozircha buyurtmalar yo'q.\n"
        "Yangi buyurtma berish uchun orqaga qayting 👇",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=kb
    )


# ══════════════════════════════════════
#   ISHGA TUSHIRISH
# ══════════════════════════════════════

if __name__ == "__main__":
    print("🚀 Gravlek Donat Bot ishga tushdi...")
    print(f"📦 {len(PACKAGES)} ta paket yuklandi")
    print("⏳ Xabarlar kutilmoqda...\n")
    bot.infinity_polling()
