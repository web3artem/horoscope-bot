import asyncio

from datetime import time

from data import config
from db.schemas.user import Distribution, User, MessageId
from db.db_gino import db


async def db_test():
    await db.set_bind(config.POSTGRES_URI)  # Устанавливаем подключение к БД
    await db.gino.create_all()

    msg = await Distribution.select().gino.all()
    print(msg)

loop = asyncio.get_event_loop()
loop.run_until_complete(db_test())
