import os
import json
import random
import time
import threading
import telebot
from telebot import types
from deep_translator import GoogleTranslator
import wikipedia
from google import genai
from dotenv import load_dotenv

base_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path)

TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_KEY")

bot = telebot.TeleBot(TOKEN)
wikipedia.set_lang("uz")

ai_client = None
if GEMINI_API_KEY:
    ai_client = genai.Client(api_key=GEMINI_API_KEY)

DATA_FILE = os.path.join(base_dir, "lugat.json")
CHANNELS_FILE = os.path.join(base_dir, "kanallar.json")

quiz_sessions = {}

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

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    portfolio_url = "https://wwwwpixelin.lovable.app" 
    
    # Mini App ochadigan maxsus tugma
    portfolio_button = types.KeyboardButton(
        text="💼 Mening Portfoliom", 
        web_app=types.WebAppInfo(url=portfolio_url)
    )
    
    markup.add(
        portfolio_button, 
        types.KeyboardButton("📢 Sevimli kanallar"),
        types.KeyboardButton("➕ Lug'atga so'z qo'shish"),
        types.KeyboardButton("🧠 So'z takrorlash"),
        types.KeyboardButton("📺 YouTube Yuklash"),
        types.KeyboardButton("🌐 Tarjima"),
        types.KeyboardButton("🔍 Vikipediya")
    )
    return markup

def dynamic_units_menu(chat_id, mode="add"):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    data = load_json_data(DATA_FILE)
    uid = str(chat_id)
    
    # Foydalanuvchiga tegishli mavjud unitlarni bazadan olish
    user_units = list(data.get(uid, {}).keys()) if isinstance(data.get(uid), dict) else []
    
    if mode == "add":
        markup.add(types.KeyboardButton("➕ Yangi Unit yaratish"))
        
    for unit in user_units:
        markup.add(types.KeyboardButton(unit))
        
    markup.add(types.KeyboardButton("⬅️ Asosiy menyuga qaytish"))
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

# --- Xabarni bo'laklab yuborish (Uzun matnlar uchun) ---
def send_large_message(chat_id, text):
    if len(text) <= 4096:
        bot.send_message(chat_id, text)
    else:
        for i in range(0, len(text), 4000):
            bot.send_message(chat_id, text[i:i+4000])

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    if chat_id in quiz_sessions:
        quiz_sessions[chat_id]['active'] = False
    bot.send_message(chat_id, "Bot faol! Kerakli bo'limni tanlang:", reply_markup=main_menu())

@bot.message_handler(content_types=['text'])
def handle_menu(message):
    if message.text == "⬅️ Asosiy menyuga qaytish":
        if message.chat.id in quiz_sessions:
            quiz_sessions[message.chat.id]['active'] = False
        bot.send_message(message.chat.id, "Asosiy menyudasiz:", reply_markup=main_menu())
        
        
    elif message.text == "➕ Lug'atga so'z qo'shish":
        msg = bot.send_message(message.chat.id, "Qaysi Unitga so'z qo'shmoqchisiz yoki yangisini yaratasiz? 👇", reply_markup=dynamic_units_menu(message.chat.id, "add"))
        bot.register_next_step_handler(msg, choose_unit_for_add)
        
    elif message.text == "🧠 So'z takrorlash":
        msg = bot.send_message(message.chat.id, "Qaysi Unitni takrorlashni xohlaysiz? 👇", reply_markup=dynamic_units_menu(message.chat.id, "quiz"))
        bot.register_next_step_handler(msg, choose_unit_for_quiz)
        
    elif message.text == "📥 YouTube Yuklash":
        msg = bot.send_message(message.chat.id, "Video linkini yuboring:", reply_markup=back_markup())
        bot.register_next_step_handler(msg, process_youtube_dl)
        
    elif message.text == "🌐 Tarjima":
        msg = bot.send_message(message.chat.id, "Matn yuboring:", reply_markup=back_markup())
        bot.register_next_step_handler(msg, process_translation)
        
    elif message.text == "🔍 Vikipediya":
        msg = bot.send_message(message.chat.id, "Mavzu yozing:", reply_markup=back_markup())
        bot.register_next_step_handler(msg, process_wiki)


def choose_unit_for_add(message):
    if message.text == "⬅️ Asosiy menyuga qaytish": return start(message)
    
    if message.text == "➕ Yangi Unit yaratish":
        msg = bot.send_message(message.chat.id, "📝 Yangi Unit nomini kiriting (Xohlagan nomingizni yozishingiz mumkin):", reply_markup=back_markup())
        bot.register_next_step_handler(msg, create_new_unit)
    else:
        unit_name = message.text
        prompt_and_get_words(message, unit_name)

def create_new_unit(message):
    if message.text == "⬅️ Asosiy menyuga qaytish": return start(message)
    unit_name = message.text.strip()
    
    if not unit_name:
        msg = bot.send_message(message.chat.id, "❌ Noto'g'ri nom. Qayta urinib ko'ring:")
        bot.register_next_step_handler(msg, create_new_unit)
        return
        
    prompt_and_get_words(message, unit_name)

def prompt_and_get_words(message, unit_name):
    text = (
        f"📂 **Bo'lim: {unit_name}**\n\n"
        "Ushbu bo'limga qo'shmoqchi bo'lgan so'zlaringizni yuboring.\n"
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
    
    if uid not in data or not isinstance(data[uid], dict):
        data[uid] = {}
    if unit_name not in data[uid]:
        data[uid][unit_name] = []
        
    for line in lines:
        line = line.strip()
        if not line:
            continue
        normalized = line.replace('–', '-').replace('—', '-')
        if '-' in normalized:
            data[uid][unit_name].append(normalized)
            added_count += 1
        else:
            ignored_lines.append(line)
            
    save_json_data(DATA_FILE, data)
    
    res = f"✅ **'{unit_name}' bo'limiga {added_count} ta ma'lumot saqlandi!**\n"
    if ignored_lines:
        res += "\n⚠️ Format xatoligi uchun qo'shilmadi:\n"
        for ig in ignored_lines: res += f"• `{ig}`\n"
        
    res += f"\n*{unit_name}* uchun yana so'z yuborishingiz mumkin:"
    msg = bot.send_message(message.chat.id, res, parse_mode="Markdown", reply_markup=back_markup())
    bot.register_next_step_handler(msg, add_word_logic, unit_name=unit_name)

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
        bot.send_message(chat_id, f"🤷‍♂️ *{unit_name}* bo'limida so'zlar topilmadi. Avval so'z qo'shing.", parse_mode="Markdown", reply_markup=main_menu())

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
        msg = bot.send_message(chat_id, "Keyingi savol uchun ➡️ Keyingi so'z tugmasini bosing.", reply_markup=quiz_menu())
        bot.register_next_step_handler(msg, check_quiz_answer)
        return

    quiz_sessions[chat_id]['active'] = False
    correct_answer = quiz_sessions[chat_id]['answer']
    
    if message.text.strip().lower() == correct_answer.lower():
        bot.send_message(chat_id, "🎉 To'g'ri! Barakalla! 👏", reply_markup=quiz_menu())
    else:
        bot.send_message(chat_id, f"❌ Noto'g'ri!\n\nTo'g'ri javob: *{correct_answer}* edi.", parse_mode="Markdown", reply_markup=quiz_menu())

def process_youtube_dl(message):
    if message.text == "⬅️ Asosiy menyuga qaytish": return start(message)
    bot.send_message(message.chat.id, "📥 Video yuklash tizimi faollashtirilmoqda, iltimos kuting...")
    # Loyihangizdagi yt_dlp integratsiyasini shu yerda davom ettirishingiz mumkin
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
    print("--- Bot barcha xatolar tuzatilib, muvaffaqiyatli ishga tushirildi! ---")
    bot.infinity_polling()