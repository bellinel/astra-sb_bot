import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from database import Database
from handler import workers_router

# Инициализируем логгер
logger = logging.getLogger(__name__)


# Хэндлер на команду /start



# Функция конфигурирования и запуска бота
async def main():
    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s'
    )

    # Загружаем переменные окружения из .env файла
    load_dotenv()

    # Получаем переменные окружения
    bot_token = os.getenv("BOT_TOKEN")
    database_path = os.getenv("DATABASE_PATH", "db.sqlite3")

    if not bot_token:
        logger.error("Необходимо указать BOT_TOKEN в переменных окружения")
        return

    # Инициализируем бот и диспетчер
    bot = Bot(token=bot_token)
    dp = Dispatcher()
    data_base = Database()
    await data_base.init()

    # Создаем подключение к базе данных
    

    # Регистрируем хэндлеры
    dp.include_router(workers_router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main()) 