# import telebot
# from telebot import types
# from google import genai
# from deep_translator import GoogleTranslator
# from youtubesearchpython import VideosSearch
# import wikipedia
# import yt_dlp
# import json
# import os
# import random
# from dotenv import load_dotenv

# load_dotenv()

# TOKEN = os.getenv("BOT_TOKEN")
# bot = telebot.TeleBot(TOKEN, parse_mode=None)
# GEMINI_API_KEY =os.getenv("KEY") 

# # AI va Botni sozlash
# client = genai.Client(api_key=GEMINI_API_KEY)
# bot = telebot.TeleBot(TOKEN)
# wikipedia.set_lang("uz")
# DATA_FILE = "lugat.json"

# def load_data():
#     """Bo'sh fayl bo'lsa yoki xato bo'lsa, {} qaytaradi"""
#     if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
#         try:
#             with open(DATA_FILE, "r", encoding="utf-8") as f:
#                 return json.load(f)
#         except json.JSONDecodeError:
#             return {}
#     return {}

# def save_data(data):
#     with open(DATA_FILE, "w", encoding="utf-8") as f:
#         json.dump(data, f, indent=4, ensure_all_ascii=False)

# def send_large_message(chat_id, text):
#     if len(text) <= 4096:
#         bot.send_message(chat_id, text)
#     else:
#         for i in range(0, len(text), 4000):
#             bot.send_message(chat_id, text[i:i+4000])

# def main_menu():
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
#     markup.add(
#         types.KeyboardButton("🤖 AI bilan suhbat"),
#         types.KeyboardButton("💻 Kod yozish"),
#         types.KeyboardButton("➕ Lug'atga so'z qo'shish"),
#         types.KeyboardButton("🧠 So'z takrorlash"),
#         types.KeyboardButton("📥 YouTube Yuklash"),
#         types.KeyboardButton("🌍 Tarjima"),
#         types.KeyboardButton("🔍 Vikipediya")
#     )
#     return markup

# def back_markup():
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     markup.add(types.KeyboardButton("⬅️ Asosiy menyuga qaytish"))
#     return markup

# @bot.message_handler(commands=['start'])
# def start(message):
#     bot.send_message(message.chat.id, "Bot qayta ishga tushdi!", reply_markup=main_menu())

# @bot.message_handler(content_types=['text'])
# def handle_menu(message):
#     if message.text == "⬅️ Asosiy menyuga qaytish":
#         bot.send_message(message.chat.id, "Asosiy menyudasiz:", reply_markup=main_menu())

#     elif message.text == "🤖 AI bilan suhbat":
#         msg = bot.send_message(message.chat.id, "Savolingizni bering:", reply_markup=back_markup())
#         bot.register_next_step_handler(msg, process_ai_chat)

#     elif message.text == "💻 Kod yozish":
#         msg = bot.send_message(message.chat.id, "Kod vazifasini yozing:", reply_markup=back_markup())
#         bot.register_next_step_handler(msg, process_ai_code)

#     elif message.text == "➕ Lug'atga so'z qo'shish":
#         msg = bot.send_message(message.chat.id, "So'z va tarjimani yozing (Masalan: Book - Kitob):", reply_markup=back_markup())
#         bot.register_next_step_handler(msg, add_word)

#     elif message.text == "🧠 So'z takrorlash":
#         start_quiz(message)

#     elif message.text == "📥 YouTube Yuklash":
#         msg = bot.send_message(message.chat.id, "Video linkini yuboring:", reply_markup=back_markup())
#         bot.register_next_step_handler(msg, process_youtube_dl)

#     elif message.text == "🌍 Tarjima":
#         msg = bot.send_message(message.chat.id, "Matn yuboring:", reply_markup=back_markup())
#         bot.register_next_step_handler(msg, process_translation)

#     elif message.text == "🔍 Vikipediya":
#         msg = bot.send_message(message.chat.id, "Mavzu yozing:", reply_markup=back_markup())
#         bot.register_next_step_handler(msg, process_wiki)

# def process_ai_chat(message):
#     if message.text == "⬅️ Asosiy menyuga qaytish": return start(message)
#     bot.send_chat_action(message.chat.id, 'typing')
#     try:
#         response = client.models.generate_content(model='gemini-1.5-flash', contents=message.text)
#         send_large_message(message.chat.id, response.text)
#     except:
#         bot.reply_to(message, "⚠️ AI ulanishda xato. Biroz kutib urinib ko'ring.")
#     bot.register_next_step_handler(message, process_ai_chat)

# def process_ai_code(message):
#     if message.text == "⬅️ Asosiy menyuga qaytish": return start(message)
#     try:
#         response = client.models.generate_content(model='gemini-1.5-flash', contents=f"Kod yoz: {message.text}")
#         send_large_message(message.chat.id, response.text)
#     except:
#         bot.reply_to(message, "❌ Xatolik.")
#     bot.register_next_step_handler(message, process_ai_code)

# def add_word(message):
#     if message.text == "⬅️ Asosiy menyuga qaytish": return start(message)
#     data = load_data()
#     uid = str(message.chat.id)
#     if uid not in data: data[uid] = []
#     data[uid].append(message.text)
#     save_data(data)
#     bot.send_message(message.chat.id, "✅ Lug'atga qo'shildi!")
#     bot.register_next_step_handler(message, add_word)

# def start_quiz(message):
#     data = load_data()
#     uid = str(message.chat.id)
#     if uid in data and len(data[uid]) > 0:
#         word = random.choice(data[uid])
#         bot.send_message(message.chat.id, f"🤔 Buning tarjimasi nima?\n\n👉 **{word.split('-')[0].strip()}**", reply_markup=back_markup())
#     else:
#         bot.send_message(message.chat.id, "📭 Lug'atingiz bo'sh. Avval so'z qo'shing.")

# def process_youtube_dl(message):
#     if message.text == "⬅️ Asosiy menyuga qaytish": return start(message)
#     bot.send_message(message.chat.id, "⏳ Yuklanmoqda...")
#     try:
#         filename = f"v_{message.chat.id}.mp4"
#         with yt_dlp.YoutubeDL({'outtmpl': filename, 'format': 'best[filesize<45M]'}) as ydl:
#             ydl.download([message.text])
#         with open(filename, 'rb') as v: bot.send_video(message.chat.id, v)
#         os.remove(filename)
#     except: bot.send_message(message.chat.id, "❌ Yuklab bo'lmadi.")
#     bot.register_next_step_handler(message, process_youtube_dl)

# def process_translation(message):
#     if message.text == "⬅️ Asosiy menyuga qaytish": return start(message)
#     tr = GoogleTranslator(source='auto', target='uz').translate(message.text)
#     bot.reply_to(message, f"🇺🇿: {tr}")
#     bot.register_next_step_handler(message, process_translation)

# def process_wiki(message):
#     if message.text == "⬅️ Asosiy menyuga qaytish": return start(message)
#     try:
#         res = wikipedia.summary(message.text, sentences=2)
#         bot.send_message(message.chat.id, f"📖: {res}")
#     except: bot.send_message(message.chat.id, "❌ Topilmadi.")
#     bot.register_next_step_handler(message, process_wiki)

# print("--- Bot barcha xatoliklardan tozalandi! ---")
# bot.infinity_polling()



























# # import telebot
# # import os
# # from dotenv import load_dotenv
# # from transliterate import to_cyrillic, to_latin

# # load_dotenv()

# # TOKEN = os.getenv("BOT_TOKEN")
# # bot = telebot.TeleBot(TOKEN, parse_mode=None)

# # @bot.message_handler(commands=['start', 'help'])
# # def send_welcome(message):
# # 	bot.reply_to(message,)
	
# # @bot.message_handler(func=lambda message: True)
# # def echo_all(message):
# # 	#print(message)
# # 	text = message.text
# # 	if text.isascii():
# # 		bot.reply_to(message, to_cyrillic(text))
# # 	else:
# # 		bot.reply_to(message, to_latin(text))
	
# # bot.infinity_polling()

# # s = input()
# # if s.isascii():
# #     print(to_cyrillic(s))
# # else:
# #     print(to_latin(s))

import os
import json
import random
import telebot
from telebot import types
from deep_translator import GoogleTranslator
import wikipedia
import yt_dlp
from dotenv import load_dotenv

# .env faylini yuklash
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

# Botni sozlash
bot = telebot.TeleBot(TOKEN)
wikipedia.set_lang("uz")

DATA_FILE = "lugat.json"
CHANNELS_FILE = "kanallar.json"

# --- Ma'lumotlarni yuklash va saqlash funksiyalari ---
def load_json_data(file_path):
    """JSON fayldan ma'lumot yuklash"""
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_json_data(file_path, data):
    """Ma'lumotlarni JSON faylga saqlash"""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def send_large_message(chat_id, text):
    """Uzun xabarlarni bo'lib yuborish"""
    if len(text) <= 4096:
        bot.send_message(chat_id, text)
    else:
        for i in range(0, len(text), 4000):
            bot.send_message(chat_id, text[i:i+4000])

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

@bot.message_handler(commands=['start'])
def start(message):
    # Foydalanuvchining ismini olish (agar ismi bo'lmasa 'Foydalanuvchi' deb chiqaradi)
    user_name = message.from_user.first_name if message.from_user.first_name else "Foydalanuvchi"
    
    # Istasangiz, @username ni chiqarish uchun pastdagi qatordan foydalanishingiz ham mumkin:
    # user_name = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

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
        bot.send_message(message.chat.id, "📢 Kanallar bo'limi. Quyidagilardan birini tanlang:", reply_markup=channels_menu())
        
    elif message.text == "➕ Yangi kanal qo'shish":
        msg = bot.send_message(message.chat.id, "Kanal nomini yoki havolasini (linkini) yuboring:", reply_markup=back_markup())
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


# 1. Kanallar bilan ishlash
def add_channel(message):
    if message.text == "⬅️ Asosiy menyuga qaytish": return start(message)
    channels_data = load_json_data(CHANNELS_FILE)
    uid = str(message.chat.id)
    
    if uid not in channels_data:
        channels_data[uid] = []
        
    channels_data[uid].append(message.text)
    save_json_data(CHANNELS_FILE, channels_data)
    
    bot.send_message(message.chat.id, "✅ Kanal muvaffaqiyatli saqlandi!", reply_markup=channels_menu())

def show_channels(message):
    channels_data = load_json_data(CHANNELS_FILE)
    uid = str(message.chat.id)
    
    if uid in channels_data and len(channels_data[uid]) > 0:
        text = "📋 **Siz saqlagan kanallar ro'yxati:**\n\n"
        for index, channel in enumerate(channels_data[uid], 1):
            text += f"{index}. {channel}\n"
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=channels_menu())
    else:
        bot.send_message(message.chat.id, "🤷‍♂️ Sizda hali saqlangan kanallar yo'q.", reply_markup=channels_menu())

# 2. Lug'at bilan ishlash
def add_word(message):
    if message.text == "⬅️ Asosiy menyuga qaytish": return start(message)
    data = load_json_data(DATA_FILE)
    uid = str(message.chat.id)
    
    if uid not in data:
        data[uid] = []
        
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
        bot.send_message(message.chat.id, "🤷‍♂️ Lug'atingiz bo'sh. Avval so'z qo'shing.")

# 3. YouTube yuklagich
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
        bot.send_message(message.chat.id, "❌ Yuklab bo'lmadi. Havola xato yoki video hajmi juda katta.")
        
    bot.register_next_step_handler(message, process_youtube_dl)

# 4. Tarjimon va Vikipediya
def process_translation(message):
    if message.text == "⬅️ Asosiy menyuga qaytish": return start(message)
    try:
        tr = GoogleTranslator(source='auto', target='uz').translate(message.text)
        bot.reply_to(message, f"🇺🇿 {tr}")
    except Exception:
        bot.reply_to(message, "❌ Tarjimada xatolik.")
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
    print("--- Bot muvaffaqiyatli ishga tushdi! ---")
    bot.infinity_polling()