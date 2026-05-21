# import os
# import telebot
# from telebot import types
# from dotenv import load_dotenv
# from transliterate import to_cyrillic, to_latin


# load_dotenv()

# TOKEN = os.getenv("BOT_TOKEN")

# if not TOKEN:
#     raise ValueError("Xatolik: BOT_TOKEN topilmadi! .env faylingizni tekshiring.")

# bot = telebot.TeleBot(TOKEN)

# PORTFOLIO_URL = "https://wwwwpixelin.lovable.app" 

# # --- Keyboards (Tugmalar) ---

# def main_menu():
#     """Asosiy menyu tugmalari"""
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    
#     portfolio_button = types.KeyboardButton(
#         text="🌐 Portfolioni ko'rish (Mini App)", 
#         web_app=types.WebAppInfo(url=PORTFOLIO_URL)
#     )
#     transliterate_button = types.KeyboardButton(text="🔤 Transliteratsiya (Lotin/Kirill)")
    
#     markup.add(portfolio_button, transliterate_button)
#     return markup

# def back_menu():
#     """Ortga qaytish tugmasi"""
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     back_button = types.KeyboardButton(text="⬅️ Ortga qaytish")
#     markup.add(back_button)
#     return markup


# @bot.message_handler(commands=['start', 'help'])
# def start(message):
#     user_name = message.from_user.first_name if message.from_user.first_name else "Foydalanuvchi"
#     user_name = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
#     bot.send_message(
#         message.chat.id, 
#         f"Xush kelibsiz, {user_name}! Sizga qanday yordam bera olaman? 👇\n\nKerakli bo'limni tanlang:", 
#         reply_markup=main_menu()
#     )


# @bot.message_handler(func=lambda m: True)te
# def handle_text(message):
#     text = message.text
    
#     if text == "🔤 Transliteratsiya (Lotin/Kirill)":
#         info_text = (
#             "🔤 **Transliteratsiya bo'limi**\n\n"
#             "Menga matn yuboring:\n"
#             "• Agar matn **Lotin** alifbosida bo'lsa — **Kirillga** o'girib beraman.\n"
#             "• Agar matn **Kirill** alifbosida bo'lsa — **Lotinga** o'girib beraman.\n\n"
#             "Asosiy menyuga qaytish uchun pastdagi tugmani bosing."
#         )
#         bot.send_message(message.chat.id, info_text, parse_mode="Markdown", reply_markup=back_menu())
#         return

#     elif text == "⬅️ Ortga qaytish":
#         bot.send_message(message.chat.id, "Asosiy menyuga qaytdingiz:", reply_markup=main_menu())
#         return

#     else:
#         if text.isascii():
#             bot.reply_to(message, to_cyrillic(text))
#         else:
#             bot.reply_to(message, to_latin(text))


# if __name__ == "__main__":
#     print("--- Bot barcha tugmalar bilan muvaffaqiyatli ishga tushdi! ---")
#     bot.infinity_polling()









import os
import json
import random
import time
import threading
import telebot
from telebot import types
from deep_translator import GoogleTranslator
import wikipedia
from dotenv import load_dotenv
from transliterate import to_cyrillic, to_latin

# .env faylini yuklash
base_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path)

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    # Agarda .env ishlamasa, tokeningizni to'g'ridan-to'g'ri shu yerga yozishingiz ham mumkin
    TOKEN = "7510255374:AAHQvK0tH7Lh_XzYV4Z0P..." 

bot = telebot.TeleBot(TOKEN)
wikipedia.set_lang("uz")

DATA_FILE = os.path.join(base_dir, "lugat.json")
CHANNELS_FILE = os.path.join(base_dir, "kanallar.json")
MEDIA_DIR = os.path.join(base_dir, "saqlangan_medialar")

# Media saqlash papkasini tekshirish va yaratish
if not os.path.exists(MEDIA_DIR):
    os.makedirs(MEDIA_DIR)

quiz_sessions = {}

# --- JSON Ma'lumotlar bilan ishlash ---
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

# 🌍 PORTFOLIO MINI APP LINKI
PORTFOLIO_URL = "https://sizning-portfolio-saytingiz.netlify.app" 

# --- Menyular (Keyboards) ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    # Portfolio Mini App tugmasi eng tepada turadi
    portfolio_button = types.KeyboardButton(
        text="🌐 Portfolioni ko'rish (Mini App)", 
        web_app=types.WebAppInfo(url=PORTFOLIO_URL)
    )
    
    markup.row(portfolio_button) # Alohida qatorda keng turishi uchun
    markup.add(
        types.KeyboardButton("🔤 Transliteratsiya (Lotin/Kirill)"),
        types.KeyboardButton("💾 Video saqlash"),
        types.KeyboardButton("📢 Sevimli kanallar"),
        types.KeyboardButton("➕ Lug'atga so'z qo'shish"),
        types.KeyboardButton("🧠 So'z takrorlash"),
        types.KeyboardButton("📥 YouTube Yuklash"),
        types.KeyboardButton("🌐 Tarjima"),
        types.KeyboardButton("🔍 Vikipediya")
    )
    return markup

def dynamic_units_menu(chat_id, mode="add"):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    data = load_json_data(DATA_FILE)
    uid = str(chat_id)
    user_units = list(data.get(uid, {}).keys()) if isinstance(data.get(uid), dict) else []
    
    if mode == "add":
        markup.add(types.KeyboardButton("➕ Yangi Unit yaratish"))
    for unit in user_units:
        markup.add(types.KeyboardButton(unit))
    markup.add(types.KeyboardButton("⬅️ Asosiy menyuga qaytish"))
    return markup

def channels_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("➕ Yangi kanal qo'shish"),
        types.KeyboardButton("📋 Kanallarimni ko'rish"),
        types.KeyboardButton("⬅️ Asosiy menyuga qaytish")
    )
    return markup

def quiz_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(
        types.KeyboardButton("➡️ Keyingi so'z"),
        types.KeyboardButton("⬅️ Asosiy menyuga qaytish")
    )
    return markup

def back_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("⬅️ Asosiy menyuga qaytish"))
    return markup

# --- Handlers ---
@bot.message_handler(commands=['start', 'help'])
def start(message):
    chat_id = message.chat.id
    if chat_id in quiz_sessions:
        quiz_sessions[chat_id]['active'] = False
    
    user_name = message.from_user.first_name if message.from_user.first_name else "Foydalanuvchi"
    bot.send_message(
        chat_id, 
        f"Xush kelibsiz, {user_name}! Sizga qanday yordam bera olaman? 👇\n\nKerakli bo'limni tanlang:", 
        reply_markup=main_menu()
    )

@bot.message_handler(content_types=['text'])
def handle_menu(message):
    chat_id = message.chat.id
    text = message.text

    if text == "⬅️ Asosiy menyuga qaytish":
        if chat_id in quiz_sessions:
            quiz_sessions[chat_id]['active'] = False
        bot.send_message(chat_id, "Asosiy menyudasiz:", reply_markup=main_menu())
        
    elif text == "🔤 Transliteratsiya (Lotin/Kirill)":
        info_text = (
            "🔤 **Transliteratsiya bo'limi faollashdi**\n\n"
            "Menga matn yuboring:\n"
            "• Lotin bo'lsa — **Kirillga** o'giraman.\n"
            "• Kirill bo'lsa — **Lotinga** o'giraman.\n\n"
            "Chiqish uchun pastdagi tugmani bosing."
        )
        bot.send_message(chat_id, info_text, parse_mode="Markdown", reply_markup=back_markup())
        bot.register_next_step_handler(message, process_transliteration_step)
        
    elif text == "💾 Video saqlash":
        msg = bot.send_message(chat_id, "📥 Menga saqlamoqchi bo'lgan **videongizni** yoki **faylingizni** yuboring:", parse_mode="Markdown", reply_markup=back_markup())
        bot.register_next_step_handler(msg, save_media_handler)
        
    elif text == "📢 Sevimli kanallar":
        bot.send_message(chat_id, "📢 Kanallar bo'limi:", reply_markup=channels_menu())
        
    elif text == "➕ Yangi kanal qo'shish":
        msg = bot.send_message(chat_id, "Kanal nomini yoki havolasini yuboring:", reply_markup=back_markup())
        bot.register_next_step_handler(msg, add_channel)
        
    elif text == "📋 Kanallarimni ko'rish":
        show_channels(message)
        
    elif text == "➕ Lug'atga so'z qo'shish":
        msg = bot.send_message(chat_id, "Qaysi Unitga so'z qo'shmoqchisiz yoki yangisini yaratasiz? 👇", reply_markup=dynamic_units_menu(chat_id, "add"))
        bot.register_next_step_handler(msg, choose_unit_for_add)
        
    elif text == "🧠 So'z takrorlash":
        msg = bot.send_message(chat_id, "Qaysi Unitni takrorlashni xohlaysiz? 👇", reply_markup=dynamic_units_menu(chat_id, "quiz"))
        bot.register_next_step_handler(msg, choose_unit_for_quiz)
        
    elif text == "📥 YouTube Yuklash":
        msg = bot.send_message(chat_id, "Video linkini yuboring:", reply_markup=back_markup())
        bot.register_next_step_handler(msg, process_youtube_dl)
        
    elif text == "🌐 Tarjima":
        msg = bot.send_message(chat_id, "Matn yuboring:", reply_markup=back_markup())
        bot.register_next_step_handler(msg, process_translation)
        
    elif text == "🔍 Vikipediya":
        msg = bot.send_message(chat_id, "Mavzu yozing:", reply_markup=back_markup())
        bot.register_next_step_handler(msg, process_wiki)

# --- Transliteratsiya Qadami ---
def process_transliteration_step(message):
    if message.text == "⬅️ Asosiy menyuga qaytish": 
        return bot.send_message(message.chat.id, "Asosiy menyudasiz:", reply_markup=main_menu())
    
    text = message.text
    if text.isascii():
        bot.reply_to(message, to_cyrillic(text))
    else:
        bot.reply_to(message, to_latin(text))
    bot.register_next_step_handler(message, process_transliteration_step)

# --- 💾 Video va Media Saqlash Tizimi ---
def save_media_handler(message):
    if message.text == "⬅️ Asosiy menyuga qaytish": return start(message)
    
    file_id = None
    file_name = "noma'lum_fayl"
    
    # Xabar turini aniqlash va file_id ni olish
    if message.video:
        file_id = message.video.file_id
        file_name = message.video.file_name if message.video.file_name else f"video_{int(time.time())}.mp4"
    elif message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name
    elif message.photo:
        file_id = message.photo[-1].file_id
        file_name = f"photo_{int(time.time())}.jpg"
    
    if file_id:
        bot.send_message(message.chat.id, "⏳ Fayl yuklab olinmoqda va saqlanmoqda...")
        try:
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            # Faylni kompyuterga yozish
            save_path = os.path.join(MEDIA_DIR, file_name)
            with open(save_path, 'wb') as new_file:
                new_file.write(downloaded_file)
                
            bot.send_message(message.chat.id, f"✅ Muvaffaqiyatli saqlandi!\n📂 Nom: `{file_name}`", parse_mode="Markdown")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Faylni saqlashda xatolik yuz berdi: {e}")
    else:
        bot.send_message(message.chat.id, "⚠️ Iltimos, faqat video yoki fayl yuboring!")
        
    bot.register_next_step_handler(message, save_media_handler)

# --- Sevimli kanallar ---
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

# --- Dinamik Unit va Lug'at Kiritish ---
def choose_unit_for_add(message):
    if message.text == "⬅️ Asosiy menyuga qaytish": return start(message)
    
    if message.text == "➕ Yangi Unit yaratish":
        msg = bot.send_message(message.chat.id, "📝 Yangi Unit nomini kiriting:", reply_markup=back_markup())
        bot.register_next_step_handler(msg, create_new_unit)
    else:
        prompt_and_get_words(message, message.text)

def create_new_unit(message):
    if message.text == "⬅️ Asosiy menyuga qaytish": return start(message)
    unit_name = message.text.strip()
    if not unit_name:
        msg = bot.send_message(message.chat.id, "❌ Noto'g'ri nom. Qayta yozing:")
        bot.register_next_step_handler(msg, create_new_unit)
        return
    prompt_and_get_words(message, unit_name)

def prompt_and_get_words(message, unit_name):
    text = (
        f"📂 **Bo'lim: {unit_name}**\n\n"
        "Ushbu bo'limga qo'shmoqchi bo'lgan so'zlarni yuboring.\n"
        "**Format:** `So'z - Tarjima` (Har birini yangi qatordan yozing)"
    )
    msg = bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=back_markup())
    bot.register_next_step_handler(msg, add_word_logic, unit_name=unit_name)

def add_word_logic(message, unit_name):
    if message.text == "⬅️ Asosiy menyuga qaytish": return start(message)
    
    lines = message.text.split('\n')
    added_count = 0
    ignored_lines = []
    
    data = load_json_data(DATA_FILE)
    uid = str(message.chat.id)
    
    if uid not in data or not isinstance(data[uid], dict): data[uid] = {}
    if unit_name not in data[uid]: data[uid][unit_name] = []
        
    for line in lines:
        line = line.strip()
        if not line: continue
        normalized = line.replace('–', '-').replace('—', '-')
        if '-' in normalized:
            data[uid][unit_name].append(normalized)
            added_count += 1
        else:
            ignored_lines.append(line)
            
    save_json_data(DATA_FILE, data)
    
    res = f"✅ **'{unit_name}' bo'limiga {added_count} ta so'z saqlandi!**\n"
    if ignored_lines:
        res += "\n⚠️ Format xatolari:\n"
        for ig in ignored_lines: res += f"• `{ig}`\n"
    res += f"\n*{unit_name}* uchun yana so'z yuborishingiz mumkin:"
    msg = bot.send_message(message.chat.id, res, parse_mode="Markdown", reply_markup=back_markup())
    bot.register_next_step_handler(msg, add_word_logic, unit_name=unit_name)

# --- 20-0 Taymerli Quiz Tizimi ---
def choose_unit_for_quiz(message):
    if message.text == "⬅️ Asosiy menyuga qaytish": return start(message)
    start_quiz(message, unit_name=message.text, index=0)

def start_quiz(message, unit_name, index=0):
    chat_id = message.chat.id
    data = load_json_data(DATA_FILE)
    uid = str(chat_id)
    unit_words = data.get(uid, {}).get(unit_name, []) if isinstance(data.get(uid), dict) else []

    if unit_words:
        index = index % len(unit_words)
        word_pair = unit_words[index]
        
        parts = word_pair.split('-')
        question = parts[0].strip()
        answer = parts[1].strip() if len(parts) > 1 else word_pair
        quiz_id = random.randint(100000, 999999)
        
        msg = bot.send_message(
            chat_id, 
            f"⏳ **Teskari sanoq: 20**\n📖 Bo'lim: *{unit_name}*\n\n🤔 Buning tarjimasi nima?\n👉 **{question}**", 
            parse_mode="Markdown", reply_markup=quiz_menu()
        )
        
        quiz_sessions[chat_id] = {
            "unit_name": unit_name, "index": index, "answer": answer, 
            "active": True, "quiz_id": quiz_id, "msg_id": msg.message_id
        }
        
        threading.Thread(target=countdown_worker, args=(chat_id, msg.message_id, unit_name, question, answer, quiz_id)).start()
        bot.register_next_step_handler(msg, check_quiz_answer)
    else:
        bot.send_message(chat_id, f"🤷‍♂️ *{unit_name}* bo'limi bo'sh.", parse_mode="Markdown", reply_markup=main_menu())

def countdown_worker(chat_id, msg_id, unit_name, question, answer, quiz_id):
    for remaining in range(20, -1, -1):
        if chat_id not in quiz_sessions or not quiz_sessions[chat_id].get('active') or quiz_sessions[chat_id].get('quiz_id') != quiz_id:
            return
        try:
            bot.edit_message_text(
                chat_id=chat_id, message_id=msg_id,
                text=f"⏳ **Teskari sanoq: {remaining}**\n📖 Bo'lim: *{unit_name}*\n\n🤔 Buning tarjimasi nima?\n👉 **{question}**",
                parse_mode="Markdown", reply_markup=quiz_menu()
            )
        except: pass
        time.sleep(1)

    if chat_id in quiz_sessions and quiz_sessions[chat_id].get('active') and quiz_sessions[chat_id].get('quiz_id') == quiz_id:
        quiz_sessions[chat_id]['active'] = False
        bot.send_message(chat_id, f"⏰ **Vaqt tugadi!**\n\nTo'g'ri javob: *{answer}* edi.", parse_mode="Markdown", reply_markup=quiz_menu())

def check_quiz_answer(message):
    chat_id = message.chat.id
    if message.text == "⬅️ Asosiy menyuga qaytish":
        if chat_id in quiz_sessions: quiz_sessions[chat_id]['active'] = False
        return start(message)
        
    if message.text == "➡️ Keyingi so'z":
        if chat_id in quiz_sessions:
            quiz_sessions[chat_id]['active'] = False
            start_quiz(message, unit_name=quiz_sessions[chat_id].get('unit_name'), index=quiz_sessions[chat_id].get('index') + 1)
        return
        
    if chat_id not in quiz_sessions or not quiz_sessions[chat_id].get('active'):
        msg = bot.send_message(chat_id, "Keyingi savol uchun ➡️ tugmasini bosing.", reply_markup=quiz_menu())
        bot.register_next_step_handler(msg, check_quiz_answer)
        return

    quiz_sessions[chat_id]['active'] = False
    correct_answer = quiz_sessions[chat_id]['answer']
    
    if message.text.strip().lower() == correct_answer.lower():
        bot.send_message(chat_id, "🎉 To'g'ri! Barakalla! 👏", reply_markup=quiz_menu())
    else:
        bot.send_message(chat_id, f"❌ Noto'g'ri!\n\nTo'g'ri javob: *{correct_answer}* edi.", parse_mode="Markdown", reply_markup=quiz_menu())

# --- YouTube, Tarjimon va Wiki ---
def process_youtube_dl(message):
    if message.text == "⬅️ Asosiy menyuga qaytish": return start(message)
    bot.send_message(message.chat.id, "📥 Video qidirilmoqda/yuklanmoqda...")
    bot.register_next_step_handler(message, process_youtube_dl)

def process_translation(message):
    if message.text == "⬅️ Asosiy menyuga qaytish": return start(message)
    try:
        tr = GoogleTranslator(source='auto', target='uz').translate(message.text)
        bot.reply_to(message, f"🇺🇿 {tr}")
    except: bot.reply_to(message, "❌ Tarjimada xatolik.")
    bot.register_next_step_handler(message, process_translation)

def process_wiki(message):
    if message.text == "⬅️ Asosiy menyuga qaytish": return start(message)
    try:
        res = wikipedia.summary(message.text, sentences=2)
        bot.send_message(message.chat.id, f"📖 {res}")
    except: bot.send_message(message.chat.id, "❌ Ma'lumot topilmadi.")
    bot.register_next_step_handler(message, process_wiki)

if __name__ == "__main__":
    bot.infinity_polling()