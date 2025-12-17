import sqlite3
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
TOKEN = ""  # Замените на ваш токен
bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('info.db')
    cursor = conn.cursor()
    
    # Удаляем старые таблицы если они есть
    cursor.execute('DROP TABLE IF EXISTS Преподаватели')
    cursor.execute('DROP TABLE IF EXISTS Студенты')
    
    # Создаем новую таблицу для пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Пользователи (
        user_id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        username TEXT,
        register_time TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

# Класс состояний для FSM
class RegistrationStates(StatesGroup):
    waiting_for_registration = State()

# Клавиатура с кнопкой регистрации
def get_registration_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Зарегистрироваться")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

# Команда /start
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        "Для регистрации нажмите кнопку ниже:",
        reply_markup=get_registration_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_registration)

# Обработка кнопки регистрации
@router.message(RegistrationStates.waiting_for_registration, F.text == "📝 Зарегистрироваться")
async def register_user(message: Message, state: FSMContext):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""
    username = message.from_user.username or ""
    register_time = datetime.now()
    
    # Сохраняем пользователя в базу данных
    conn = sqlite3.connect('koopteh.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT OR REPLACE INTO Пользователи (user_id, first_name, last_name, username, register_time)
        VALUES (?, ?, ?, ?, ?)
        ''', (user_id, first_name, last_name, username, register_time))
        
        conn.commit()
        
        # Получаем данные о пользователе
        cursor.execute('SELECT * FROM Пользователи WHERE user_id = ?', (user_id,))
        user_data = cursor.fetchone()
        
        await message.answer(
            "✅ Регистрация прошла успешно!\n\n"
            f"📋 Ваши данные:\n"
            f"🆔 ID: {user_data[0]}\n"
            f"👤 Имя: {user_data[1]}\n"
            f"👥 Фамилия: {user_data[2] if user_data[2] else 'Не указана'}\n"
            f"📛 Username: @{user_data[3] if user_data[3] else 'Не указан'}\n"
            f"🕐 Время регистрации: {user_data[4]}",
            reply_markup=get_registration_keyboard()
        )
        
        logger.info(f"Пользователь зарегистрирован: {user_id}")
        
    except Exception as e:
        logger.error(f"Ошибка при регистрации: {e}")
        await message.answer("❌ Произошла ошибка при регистрации. Попробуйте позже.")
    
    finally:
        conn.close()
    
    await state.clear()

# Команда /me для просмотра своих данных
@router.message(Command("me"))
async def cmd_me(message: Message):
    user_id = message.from_user.id
    
    conn = sqlite3.connect('koopteh.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM Пользователи WHERE user_id = ?', (user_id,))
    user_data = cursor.fetchone()
    
    if user_data:
        await message.answer(
            f"📋 Ваши данные:\n"
f"🆔 ID: {user_data[0]}\n"
            f"👤 Имя: {user_data[1]}\n"
            f"👥 Фамилия: {user_data[2] if user_data[2] else 'Не указана'}\n"
            f"📛 Username: @{user_data[3] if user_data[3] else 'Не указан'}\n"
            f"🕐 Время регистрации: {user_data[4]}"
        )
    else:
        await message.answer(
            "❌ Вы еще не зарегистрированы.\n"
            "Нажмите кнопку '📝 Зарегистрироваться'",
            reply_markup=get_registration_keyboard()
        )
    
    conn.close()

# Команда /users для просмотра всех пользователей (только для админов)
@router.message(Command("users"))
async def cmd_users(message: Message):
    # Здесь можно добавить проверку на админа
    # if message.from_user.id not in ADMIN_IDS: return
    
    conn = sqlite3.connect('koopteh.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM Пользователи')
    count = cursor.fetchone()[0]
    
    cursor.execute('SELECT * FROM Пользователи')
    users = cursor.fetchall()
    
    if users:
        response = f"👥 Всего зарегистрированных пользователей: {count}\n\n"
        for user in users:
            response += (
                f"🆔 ID: {user[0]}\n"
                f"👤 Имя: {user[1]}\n"
                f"👥 Фамилия: {user[2] if user[2] else 'Не указана'}\n"
                f"📛 Username: @{user[3] if user[3] else 'Не указан'}\n"
                f"🕐 Регистрация: {user[4]}\n"
                f"{'-'*30}\n"
            )
        
        # Разбиваем на части если сообщение слишком длинное
        if len(response) > 4000:
            parts = [response[i:i+4000] for i in range(0, len(response), 4000)]
            for part in parts:
                await message.answer(part)
        else:
            await message.answer(response)
    else:
        await message.answer("📭 Нет зарегистрированных пользователей.")
    
    conn.close()

# Обработка текстовых сообщений
@router.message(F.text)
async def handle_text(message: Message, state: FSMContext):
    current_state = await state.get_state()
    
    # Если пользователь не в процессе регистрации, предлагаем зарегистрироваться
    if current_state is None:
        await message.answer(
            "Для регистрации нажмите кнопку ниже:",
            reply_markup=get_registration_keyboard()
        )
        await state.set_state(RegistrationStates.waiting_for_registration)

# Основная функция
async def main():
    # Инициализация базы данных
    init_db()
    
    # Запуск бота
    logger.info("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

