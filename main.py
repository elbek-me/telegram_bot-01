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



























import telebot
import os
from dotenv import load_dotenv
from transliterate import to_cyrillic, to_latin

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN, parse_mode=None)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message,)
	
@bot.message_handler(func=lambda message: True)
def echo_all(message):
	#print(message)
	text = message.text
	if text.isascii():
		bot.reply_to(message, to_cyrillic(text))
	else:
		bot.reply_to(message, to_latin(text))
	
bot.infinity_polling()

s = input()
if s.isascii():
    print(to_cyrillic(s))
else:
    print(to_latin(s))