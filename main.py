from aiogram import executor

from loader import dp
from handlers import client, admin


async def on_startup(_):
    print("Бот был запущен!")

    from db.db_gino import on_startup
    await on_startup(dp)


client.register_handlers_client(dp)
admin.register_handlers_admin(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
