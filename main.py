import os
import telebot
from telebot import types
from dotenv import load_dotenv
from transliterate import to_cyrillic, to_latin


load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("Xatolik: BOT_TOKEN topilmadi! .env faylingizni tekshiring.")

bot = telebot.TeleBot(TOKEN)

PORTFOLIO_URL = "https://wwwwpixelin.lovable.app" 

# --- Keyboards (Tugmalar) ---

def main_menu():
    """Asosiy menyu tugmalari"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    
    portfolio_button = types.KeyboardButton(
        text="🌐 Portfolioni ko'rish (Mini App)", 
        web_app=types.WebAppInfo(url=PORTFOLIO_URL)
    )
    transliterate_button = types.KeyboardButton(text="🔤 Transliteratsiya (Lotin/Kirill)")
    
    markup.add(portfolio_button, transliterate_button)
    return markup

def back_menu():
    """Ortga qaytish tugmasi"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back_button = types.KeyboardButton(text="⬅️ Ortga qaytish")
    markup.add(back_button)
    return markup


@bot.message_handler(commands=['start', 'help'])
def start(message):
    user_name = message.from_user.first_name if message.from_user.first_name else "Foydalanuvchi"
    user_name = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
    bot.send_message(
        message.chat.id, 
        f"Xush kelibsiz, {user_name}! Sizga qanday yordam bera olaman? 👇\n\nKerakli bo'limni tanlang:", 
        reply_markup=main_menu()
    )


@bot.message_handler(func=lambda m: True)
def handle_text(message):
    text = message.text
    
    if text == "🔤 Transliteratsiya (Lotin/Kirill)":
        info_text = (
            "🔤 **Transliteratsiya bo'limi**\n\n"
            "Menga matn yuboring:\n"
            "• Agar matn **Lotin** alifbosida bo'lsa — **Kirillga** o'girib beraman.\n"
            "• Agar matn **Kirill** alifbosida bo'lsa — **Lotinga** o'girib beraman.\n\n"
            "Asosiy menyuga qaytish uchun pastdagi tugmani bosing."
        )
        bot.send_message(message.chat.id, info_text, parse_mode="Markdown", reply_markup=back_menu())
        return

    elif text == "⬅️ Ortga qaytish":
        bot.send_message(message.chat.id, "Asosiy menyuga qaytdingiz:", reply_markup=main_menu())
        return

    else:
        if text.isascii():
            bot.reply_to(message, to_cyrillic(text))
        else:
            bot.reply_to(message, to_latin(text))


if __name__ == "__main__":
    print("--- Bot barcha tugmalar bilan muvaffaqiyatli ishga tushdi! ---")
    bot.infinity_polling()