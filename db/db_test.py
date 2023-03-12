import asyncio

from datetime import time

from data import config
from db import quick_commands as commands
from db.db_gino import db


async def db_test():
    await db.set_bind(config.POSTGRES_URI)  # Устанавливаем подключение к БД
    await db.gino.drop_all()  # Удаляем все таблицы
    await db.gino.create_all()

    await commands.add_user(1, 'ss', 'Artem', 'male', '08.05.1997', 'Gukovo', 'day')
    await commands.add_user(2, 'ss', 'Oleg', 'male', '11.05.1997', 'Gukovo', 'day')
    await commands.add_user(3, 'ss', 'ANton', 'male', '12.05.1997', 'Gukovo', 'day')
    await commands.add_user(4, 'ss', 'Denis', 'male', '13.05.1997', 'Gukovo', 'day')
    await commands.add_user(5, 'ss', 'Artem', 'male', '08.05.1997', 'Gukovo', 'day')

    users = await commands.select_all_users()
    print(users)

    count = await commands.count_users()
    print(count)

    user = await commands.select_user(1)
    print(user)


loop = asyncio.get_event_loop()
loop.run_until_complete(db_test())
