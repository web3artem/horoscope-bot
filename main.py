import asyncio

from aiogram import executor

from handlers import client, admin
from loader import dp
from handlers.client import schedule
from handlers.admin_filters import IsAdmin


async def on_startup(_):
    print("Бот был запущен!")

    from db.db_gino import on_startup
    await on_startup(dp)

dp.bind_filter(IsAdmin)
client.register_handlers_client(dp)
admin.register_handlers_admin(dp)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(schedule(10))
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, loop=loop)
