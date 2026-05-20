import os
import json
import random
import telebot
from telebot import types
from deep_translator import GoogleTranslator
import wikipedia
import yt_dlp

# Railway-dagi o'zgaruvchidan tokenni olish
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
wikipedia.set_lang("uz")

DATA_FILE = "lugat.json"
CHANNELS_FILE = "kanallar.json"

# --- Ma'lumotlarni yuklash va saqlash ---
def load_json_data(file_path):
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_json_data(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- Tugmalar (Keyboards) ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("📢 Sevimli kanallar"),
        types.KeyboardButton("➕ Lug'atga so'z qo'shish"),
        types.KeyboardButton("🧠 So'z takrorlash"),
        types.KeyboardButton("📺 YouTube Yuklash"),
        types.KeyboardButton("🌐 Tarjima"),
        types.KeyboardButton("🔍 Vikipediya")
    )
    return markup

def channels_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("➕ Yangi kanal qo'shish"),
        types.KeyboardButton("📋 Kanallarimni ko'rish"),
        types.KeyboardButton("⬅️ Asosiy menyuga qaytish")
    )
    return markup

def back_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("⬅️ Asosiy menyuga qaytish"))
    return markup

# --- Handlers ---
@bot.message_handler(commands=['start'])
def start(message):
    user_name = message.from_user.first_name if message.from_user.first_name else "Foydalanuvchi"
    bot.send_message(
        message.chat.id, 
        f"Xush kelibsiz, {user_name}! Sizga qanday yordam bera olaman? 👇\n\nKerakli bo'limni tanlang:", 
        reply_markup=main_menu()
    )

@bot.message_handler(content_types=['text'])
def handle_menu(message):
    if message.text == "⬅️ Asosiy menyuga qaytish":
        bot.send_message(message.chat.id, "Asosiy menyudasiz:", reply_markup=main_menu())
    elif message.text == "📢 Sevimli kanallar":
        bot.send_message(message.chat.id, "📢 Kanallar bo'limi:", reply_markup=channels_menu())
    elif message.text == "➕ Yangi kanal qo'shish":
        msg = bot.send_message(message.chat.id, "Kanal nomini yoki havolasini yuboring:", reply_markup=back_markup())
        bot.register_next_step_handler(msg, add_channel)
    elif message.text == "📋 Kanallarimni ko'rish":
        show_channels(message)
    elif message.text == "➕ Lug'atga so'z qo'shish":
        msg = bot.send_message(message.chat.id, "So'z va tarjimani kiriting (Masalan: Book - Kitob):", reply_markup=back_markup())
        bot.register_next_step_handler(msg, add_word)
    elif message.text == "🧠 So'z takrorlash":
        start_quiz(message)
    elif message.text == "📺 YouTube Yuklash":
        msg = bot.send_message(message.chat.id, "Video linkini yuboring:", reply_markup=back_markup())
        bot.register_next_step_handler(msg, process_youtube_dl)
    elif message.text == "🌐 Tarjima":
        msg = bot.send_message(message.chat.id, "Matn yuboring:", reply_markup=back_markup())
        bot.register_next_step_handler(msg, process_translation)
    elif message.text == "🔍 Vikipediya":
        msg = bot.send_message(message.chat.id, "Mavzu yozing:", reply_markup=back_markup())
        bot.register_next_step_handler(msg, process_wiki)

# --- Funksiyalar ---
def add_channel(message):
    if message.text == "⬅️ Asosiy menyuga qaytish": return start(message)
    channels_data = load_json_data(CHANNELS_FILE)
    uid = str(message.chat.id)
    if uid not in channels_data: channels_data[uid] = []
    channels_data[uid].append(message.text)
    save_json_data(CHANNELS_FILE, channels_data)
    bot.send_message(message.chat.id, "✅ Kanal saqlandi!", reply_markup=channels_menu())

def show_channels(message):
    channels_data = load_json_data(CHANNELS_FILE)
    uid = str(message.chat.id)
    if uid in channels_data and len(channels_data[uid]) > 0:
        text = "📋 **Siz saqlagan kanallar:**\n\n"
        for index, channel in enumerate(channels_data[uid], 1):
            text += f"{index}. {channel}\n"
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=channels_menu())
    else:
        bot.send_message(message.chat.id, "🤷‍♂️ Saqlangan kanallar yo'q.", reply_markup=channels_menu())

def add_word(message):
    if message.text == "⬅️ Asosiy menyuga qaytish": return start(message)
    data = load_json_data(DATA_FILE)
    uid = str(message.chat.id)
    if uid not in data: data[uid] = []
    data[uid].append(message.text)
    save_json_data(DATA_FILE, data)
    bot.send_message(message.chat.id, "✅ Lug'atga so'z qo'shildi!")
    bot.register_next_step_handler(message, add_word)

def start_quiz(message):
    data = load_json_data(DATA_FILE)
    uid = str(message.chat.id)
    if uid in data and len(data[uid]) > 0:
        word_pair = random.choice(data[uid])
        question = word_pair.split('-')[0].strip() if '-' in word_pair else word_pair
        bot.send_message(message.chat.id, f"🤔 Buning tarjimasi nima?\n\n👉 **{question}**", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "🤷‍♂️ Lug'at bo'sh.")

def process_youtube_dl(message):
    if message.text == "⬅️ Asosiy menyuga qaytish": return start(message)
    bot.send_message(message.chat.id, "⏳ Yuklanmoqda...")
    ydl_opts = {
        'outtmpl': f'v_{message.chat.id}.%(ext)s',
        'format': 'best[filesize<45M][ext=mp4]/best[filesize<45M]',
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(message.text, download=True)
            filename = ydl.prepare_filename(info)
        with open(filename, 'rb') as v:
            bot.send_video(message.chat.id, v)
        os.remove(filename)
    except Exception:
        bot.send_message(message.chat.id, "❌ Yuklab bo'lmadi.")
    bot.register_next_step_handler(message, process_youtube_dl)

def process_translation(message):
    if message.text == "⬅️ Asosiy menyuga qaytish": return start(message)
    try:
        tr = GoogleTranslator(source='auto', target='uz').translate(message.text)
        bot.reply_to(message, f"🇺🇿 {tr}")
    except Exception:
        bot.reply_to(message, "❌ Xatolik.")
    bot.register_next_step_handler(message, process_translation)

def process_wiki(message):
    if message.text == "⬅️ Asosiy menyuga qaytish": return start(message)
    try:
        res = wikipedia.summary(message.text, sentences=2)
        bot.send_message(message.chat.id, f"📖 {res}")
    except Exception:
        bot.send_message(message.chat.id, "❌ Topilmadi.")
    bot.register_next_step_handler(message, process_wiki)

if __name__ == "__main__":
    bot.infinity_polling()