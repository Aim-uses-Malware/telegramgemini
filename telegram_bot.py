import telebot
import json
import datetime
from config import TELEGRAM_BOT_TOKEN
from gemini_api import generate_gemini_response

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# History that resets after number you set
user_histories = {}
MAX_HISTORY_LENGTH = 1000

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello! I'm Gemini-bot. Ask your question.")

@bot.message_handler(func=lambda message: True) #Messages logger!
def echo_all(message):
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    message_text = message.text
    with open("messages_logger.txt", "a", encoding="utf-8") as f:
        f.write(f"{timestamp} - User ID: {user_id}, Username: {username}, First Name: {first_name}, Last Name: {last_name}, Message: {message_text}\n")

    user_id = message.from_user.id
    prompt = message.text

    # Получаем историю разговоров для пользователя
    if user_id in user_histories:
        history = user_histories[user_id]
    else:
        history = []

    # Формируем контекст для запроса
    context = "\n".join([f"User: {q}\nGemini: {a}" for q, a in history])
    full_prompt = f"{context}\nUser: {prompt}\nGemini:"

    # Получаем ответ от Gemini
    response_text = generate_gemini_response(full_prompt)

    # Обновляем историю разговоров
    history.append((prompt, response_text))
    if len(history) > MAX_HISTORY_LENGTH:
        history = history[-MAX_HISTORY_LENGTH:]
    user_histories[user_id] = history

    bot.reply_to(message, response_text)

def start_bot():
    try:
        bot.infinity_polling()
        print("Бот успешно запущен!")
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")

if __name__ == "__main__":
    start_bot()
