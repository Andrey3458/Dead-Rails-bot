
import telebot
from telebot import types
import json
import os

TOKEN = "8034284579:AAFzlNrZcsFVzl_8nlzAmeNgZNK15ADt0Co"
bot = telebot.TeleBot(TOKEN)

DATA_FILE = "users.json"
users = {}

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        users = json.load(f)

def save_users():
    with open(DATA_FILE, "w") as f:
        json.dump(users, f)

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    if user_id not in users:
        users[user_id] = {"bonds": 0, "invited": []}
        save_users()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎁 Получить подарок", "🛒 Магазин классов")
    markup.add("📁 Профиль", "📨 Пригласить друга")
    bot.send_message(message.chat.id, "Добро пожаловать! Выбери действие:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🎁 Получить подарок")
def daily(message):
    user_id = str(message.from_user.id)
    if user_id not in users:
        users[user_id] = {"bonds": 0, "invited": []}
    users[user_id]["bonds"] += 100
    save_users()
    bot.send_message(message.chat.id, "🎁 Вы получили 100 облигаций!")

@bot.message_handler(func=lambda m: m.text == "📁 Профиль")
def profile(message):
    user_id = str(message.from_user.id)
    bonds = users.get(user_id, {}).get("bonds", 0)
    invited = users.get(user_id, {}).get("invited", [])
    bot.send_message(message.chat.id, f"📁 Профиль:
Облигации: {bonds}
Приглашено друзей: {len(invited)}")

@bot.message_handler(func=lambda m: m.text == "📨 Пригласить друга")
def invite(message):
    user_id = str(message.from_user.id)
    link = f"https://t.me/Klassrails_bot?start={user_id}"
    bot.send_message(message.chat.id, f"📨 Пригласи друзей по ссылке:
{link}")

@bot.message_handler(func=lambda m: m.text == "🛒 Магазин классов")
def shop(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("👔 Президент — 2500", callback_data="buy_president"))
    markup.add(types.InlineKeyboardButton("🎯 Охотник — 3000", callback_data="buy_hunter"))
    markup.add(types.InlineKeyboardButton("💣 Подрывник — 3000", callback_data="buy_bomber"))
    bot.send_message(message.chat.id, "Выберите класс для покупки:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def handle_buy(call):
    user_id = str(call.from_user.id)
    item = call.data.replace("buy_", "")
    prices = {"president": 2500, "hunter": 3000, "bomber": 3000}
    names = {"president": "👔 Президент", "hunter": "🎯 Охотник", "bomber": "💣 Подрывник"}

    if user_id not in users:
        users[user_id] = {"bonds": 0, "invited": []}

    if users[user_id]["bonds"] >= prices[item]:
        users[user_id]["bonds"] -= prices[item]
        save_users()
        bot.answer_callback_query(call.id, f"{names[item]} куплен!")
        bot.send_message(user_id, f"{names[item]} будет выдан через 48 часов.")
    else:
        bot.answer_callback_query(call.id, "Недостаточно облигаций!")

bot.polling()
