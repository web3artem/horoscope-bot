import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from loader import dp, bot
from data.config import ADMINS
from .admin_filters import IsAdmin
from keyboards.admin_kb import admin_main_kb, admin_post_kb, admin_correct_kb, admin_change_kb
from states.admin_states import FSMAdmin
from db.schemas.user import User, Distribution
from .client import logger
from aiogram.utils.exceptions import BotBlocked
from .client import schedule_morning, schedule_tomorrow


async def send_morning(message: types.Message):
    await schedule_morning()
    await message.answer('Гороскоп на утро был отправлен')


async def send_tomorrow(message: types.Message):
    await schedule_tomorrow()
    await message.answer('Гороскоп на вечер был отправлен')


def register_handlers_admin(disp: Dispatcher):
    disp.register_message_handler(send_morning, IsAdmin(), Text(equals='Отправить гороскоп на утро'), state='*')
    disp.register_message_handler(send_tomorrow, IsAdmin(), Text(equals='Отправить гороскоп на вечер'), state='*')
