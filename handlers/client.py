from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InputFile, CallbackQuery

from create_bot import bot
from keyboards.client_kb import client_gender_inline_kb


class FSMClient(StatesGroup):
    client_name = State()
    client_gender = State()
    client_birth_date = State()


async def start_command(message: types.Message):
    photo_path = 'media/backgrounds/background-name.jpg'
    photo = InputFile(photo_path)
    await FSMClient.client_name.set()
    await bot.send_photo(chat_id=message.from_user.id,
                         photo=photo)


async def name_info(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    photo_path = 'media/backgrounds/background-gender.jpg'
    photo = InputFile(photo_path)
    await FSMClient.next()
    await bot.send_photo(chat_id=message.from_user.id,
                         photo=photo,
                         reply_markup=client_gender_inline_kb)


async def gender_info(callback_query: CallbackQuery, state: FSMContext):
    gender = callback_query.data
    await FSMClient.next()
    await callback_query.answer("Your gender has been recorded!")


def register_handlers_client(disp: Dispatcher):
    disp.register_message_handler(start_command, commands=['start', 'help'], state=None)
    disp.register_message_handler(name_info, state=FSMClient.client_name)
    disp.register_callback_query_handler(gender_info, Text(startswith='gender'), state=FSMClient.client_gender)
