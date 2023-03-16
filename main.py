import asyncio

from aiogram import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from handlers import client, admin, admin_send_horoscope
from loader import dp
from handlers.client import schedule_morning, schedule_tomorrow
from handlers.admin_filters import IsAdmin

scheduler_morning = AsyncIOScheduler()
scheduler_evening = AsyncIOScheduler()


async def on_startup(_):
    print("Бот был запущен!")

    from db.db_gino import on_startup
    await on_startup(dp)


dp.bind_filter(IsAdmin)
client.register_handlers_client(dp)
admin.register_handlers_admin(dp)
admin_send_horoscope.register_handlers_admin(dp)

if __name__ == '__main__':
    scheduler_morning.add_job(schedule_morning, 'cron', hour=6)
    scheduler_evening.add_job(schedule_tomorrow, 'cron', hour=16)
    scheduler_morning.start()
    scheduler_evening.start()
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
