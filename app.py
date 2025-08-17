import telebot
from telebot import types
from datetime import datetime, timedelta

# Константы
BOT_TOKEN = "6232552919:AAFZeTvscnudAVdWs6rwd9P1QBcOkgrpqyw"
CHANNEL_ID = "-1001958513038"

# Временные хранилища
pending_comments = {}
last_sent_time = {}

# Инициализация бота
bot = telebot.TeleBot(BOT_TOKEN)

# Проверка подписки пользователя
def is_user_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# Обработка фото
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Проверка подписки
    if not is_user_subscribed(user_id):
        bot.send_message(chat_id, (
            "--------------------------------------------------------------------\n"
            "| ❌❌ Пожалуйста подпишитесь на канал.\n"
            "--------------------------------------------------------------------\n"
            "| ❌❌ Бот не работает без подписки в канале.\n"
            "--------------------------------------------------------------------\n"
            "| ✅✅ Канал   -  @Crash_russia_48\n"
            "--------------------------------------------------------------------\n"
        ))
        return

    # Проверка времени последней отправки
    last_time = last_sent_time.get(user_id)
    if last_time and (datetime.utcnow() - last_time) < timedelta(minutes=30):
        bot.send_message(chat_id, "Вы можете отправлять фото только каждые 30 минут. Пожалуйста, подождите.")
        return

    # Обработка фото
    photo = message.photo[-1]
    file_id = photo.file_id
    pending_comments[user_id] = (file_id, "")

    bot.send_message(chat_id, (
        "--------------------------------------\n"
        "| ✅   Фото принято. \n"
        "--------------------------------------\n"
        "| 📝 Теперь напишете \n"
        "| 📝 коммент для фото.\n"
        "--------------------------------------\n"
    ))

# Обработка текстовых сообщений
@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if user_id in pending_comments:
        file_id, comment = pending_comments[user_id]
        if comment == "":
            # Запрос комментария
            pending_comments[user_id] = (file_id, message.text)
            inline_keyboard = types.InlineKeyboardMarkup([
                [
                    types.InlineKeyboardButton("✅ ДА ✅", callback_data="send_with_username"),
                    types.InlineKeyboardButton("❌ НЕТ ❌", callback_data="send_without_username")
                ]
            ])
            bot.send_message(chat_id, (
                "--------------------------------------\n"
                "| ✅ Коммент принет\n"
                "--------------------------------------\n"
                "|  Отправить никнейм.\n"
                "|  С комментом.❓\n"
                "--------------------------------------\n"
            ), reply_markup=inline_keyboard)
    elif message.text == "/start":
        bot.send_message(chat_id, (
            "|👋👋👋Привет! Пользователь.👋👋👋\n"
            "--------------------------------------------------------------------\n"
            "|♦♦️Подпишитель на Канал♦️♦️\n"
            "--------------------------------------------------------------------\n"
            "|⏩@Crash_russia_48⏪\n"
            "--------------------------------------------------------------------\n"
            "|❌❌❌без подписки❌❌❌"
        ))
        bot.send_message(chat_id, (
            "----------------------------------------------------\n"
            "| 🔵    📷  Киньте фото  📷       \n "
            "----------------------------------------------------\n"
            "| 🔴которое хотите отправить. \n"
            "----------------------------------------------------\n\n"
            "‼️ Внимение ‼️\n\n"
            "|  Отправляйте только одно фото.\n"
            "|  Другие фото не пройдут.\n"
            "|  Пройдет только последнее фото,\n"
            "|  которое ты отправишь."
        ))

# Обработка callback-кнопок
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    data = call.data

    if user_id in pending_comments:
        file_id, comment = pending_comments.pop(user_id)

        send_with_username = (data == "send_with_username")
        username = call.from_user.username if call.from_user.username else "Аноним"

        if send_with_username:
            caption = (
                "--------------------------------------------------------------------\n"
                f"Ник: {username}\n"
                "--------------------------------------------------------------------\n\n"
                f"|| ⏬⏬  Коммент  ⏬⏬ ||\n\n {comment}"
            )
        else:
            caption = comment

        try:
            # Отправка фото в канал
            bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=file_id,
                caption=caption
            )

            # Обновляем время последней отправки
            last_sent_time[user_id] = datetime.utcnow()

            # Отправляем подтверждение пользователю
            bot.send_message(
                chat_id=call.from_user.id,
                text=(
                    "----------------------------------------\n"
                    "| ✅ Ваше фото успешно\n"
                    "| ✅ Отправлено в канал.\n"
                    "----------------------------------------\n"
                )
            )
        except Exception as e:
            bot.send_message(
                chat_id=call.from_user.id,
                text=f"| 📛 Ошибка пересылки фото:\n\n {str(e)}"
            )

        # Удаляем или очищаем сообщение с кнопками
        try:
            bot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=None
            )
        except:
            pass

# Запуск бота
if __name__ == '__main__':
    print("Бот запущен")
    bot.polling(none_stop=True)
    
