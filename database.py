import aiosqlite
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, MetaData
from datetime import datetime
import logging

# Базовый класс для всех моделей SQLAlchemy
Base = declarative_base()

class Database:
    """Класс для работы с базой данных"""
    def __init__(self, db_name: str = "bot.db"):
        # Создаем URL подключения для асинхронного SQLite
        self.db_url = f"sqlite+aiosqlite:///{db_name}"
        # Создаем асинхронный движок
        self.engine = create_async_engine(self.db_url, echo=False)
        # Создаем фабрику сессий
        self.session_factory = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        self.logger = logging.getLogger(__name__)
        
    async def init(self):
        """Инициализация базы данных"""
        async with self.engine.begin() as conn:
            # Создаем все таблицы, которые еще не созданы
            await conn.run_sync(Base.metadata.create_all)
            self.logger.info("База данных инициализирована")
    
    async def close(self):
        """Закрытие соединения с базой данных"""
        await self.engine.dispose()
        self.logger.info("Соединение с базой данных закрыто")


class Worker(Base):
    __tablename__ = "workers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    user_name = Column(String, nullable=False)
    start_address = Column(String)
    time_to_start_work = Column(DateTime)
    left_address = Column(String)
    time_to_left_work = Column(DateTime)
    work_time = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    
    
    def __repr__(self):
        return f"<Worker(id={self.id}, user_id={self.user_id}, user_name='{self.user_name}')>"


