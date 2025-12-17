import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = ''  # Вставьте ваш токен сюда

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка входящих сообщений"""
    user_message = update.message.text.lower()
    
    if user_message == 'кот':
        # Отправка фото кота (замените URL на ваше фото)
        photo_url = 'https://avatars.mds.yandex.net/i?id=e235f276f43c12514512e83139187ac235c81ae0-4121129-images-thumbs&n=13'
        await update.message.reply_photo(photo_url, caption='Смешной кот!')
    
    elif user_message == 'стикер':
        # Отправка стикера кота (нужен ID стикера)
        # Чтобы получить ID стикера, отправьте его боту @idstickerbot
        sticker_id = 'CAACAgIAAxkBAAEQBAhpQVWCUvPhLoQtYYozfFZd-rAJ-AAC6SsAAlxTEElR70BAl4wpdjYE'
        await update.message.reply_sticker(sticker_id)
    
    elif user_message == 'мяу':
        # Отправка голосового сообщения (нужен файл с мяуканьем)
        # Для тестирования можно использовать ссылку на аудиофайл
        voice_url = '5336924158691412842.ogg'
        await update.message.reply_voice(voice_url,)  
    
    elif user_message == 'привет':
        user_name = update.effective_user.first_name
        await update.message.reply_text(f"Привет, {user_name}! Я получил ваше сообщение 'Привет'!")

def main() -> None:
    """Запуск бота"""
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчик для текстовых сообщений
    handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    application.add_handler(handler)
    
    # Запускаем бота
    print("Бот запущен...")
    application.run_polling(poll_interval=3.0)

if __name__ == "__main__":
    main()

