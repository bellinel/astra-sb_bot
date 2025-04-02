from sqlalchemy import select
from database import Database
from database import Worker
from datetime import datetime
async def add_user_to_db(user_data: dict) -> None:
    """Добавляет нового пользователя в базу данных"""
    db = Database()
    try:
        async with db.session_factory() as session:
            start_time = user_data["time_to_start_work"]
            start_time = start_time.replace(microsecond=0)
            end_time = user_data["time_to_left_work"]
            end_time = end_time.replace(microsecond=0)
            new_user = Worker(
                user_id=user_data["user_id"],
                user_name=user_data["user_name"],
                start_address=user_data["start_address"],
                time_to_start_work=start_time,
                left_address=user_data["left_address"],
                time_to_left_work=end_time,
                work_time=user_data["work_time"],
                created_at=datetime.now().replace(microsecond=0)
            )
            session.add(new_user)
            await session.commit()
    except Exception as e:
        print(f"Ошибка при добавлении пользователя: {e}")
    finally:
        await db.close()

async def get_all_workers() -> list:
    """Получает всех работников из базы данных"""
    db = Database()
    try:
        async with db.session_factory() as session:
            workers = await session.execute(select(Worker))
            return workers.scalars().all()
    except Exception as e:
        print(f"Ошибка при получении работников: {e}")
        return []
    finally:
        await db.close()

async def delete_all_workers() -> None:
    """Удаляет все записи из таблицы работников"""
    db = Database()
    try:
        async with db.session_factory() as session:
            await session.execute(Worker.__table__.delete())
            await session.commit()
    except Exception as e:
        print(f"Ошибка при удалении работников: {e}")
    finally:
        await db.close()
