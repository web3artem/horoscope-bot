from aiogram import types, Dispatcher
from aiogram.types import InputFile
from create_bot import dp, bot


# @dp.message_handler(commands=['start', 'help'])
async def start_command(message: types.Message):
    photo_path = 'media/backgrounds/background-name.jpg'
    photo = InputFile(photo_path)
    await bot.send_photo(chat_id=message.from_user.id,
                         photo=photo)
    await message.delete()


def register_handlers_client(disp: Dispatcher):
    disp.register_message_handler(start_command, commands=['start', 'help'])
