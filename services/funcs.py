from datetime import datetime

from aiogram import types
from create_bot import bot
from aiogram.types import InputFile, CallbackQuery


async def get_background_photo(message: types.Message | CallbackQuery,
                               path: str, caption=None,
                               text=None,
                               reply_markup=None):
    photo_path = path
    photo = InputFile(photo_path)

    if text is None:
        await bot.send_photo(message.from_user.id, photo, caption=caption, reply_markup=reply_markup)
    else:
        await bot.send_message(message.from_user.id, photo, text=text, reply_markup=reply_markup)


def validate_birthdate(birthdate: str):
    try:
        datetime.strptime(birthdate, '%d.%m.%Y')
        return True
    except ValueError:
        return False
