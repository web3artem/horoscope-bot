from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery

from create_bot import bot
from keyboards.client_kb import client_gender_inline_kb
from services.funcs import get_background_photo, validate_birthdate


class FSMClient(StatesGroup):
    client_name = State()
    client_gender = State()
    client_birth_date = State()
    client_birth_place = State()


async def start_command(message: types.Message):
    await FSMClient.client_name.set()
    await get_background_photo(message, 'media/backgrounds/background-name.jpg')


async def name_info(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    await FSMClient.next()
    await get_background_photo(message, 'media/backgrounds/background-gender.jpg', reply_markup=client_gender_inline_kb)


async def gender_info(callback_query: CallbackQuery, state: FSMContext):
    gender = callback_query.data
    async with state.proxy() as data:
        data['gender'] = gender
    await FSMClient.next()

    await get_background_photo(callback_query, 'media/backgrounds/birthdate-img.jpg',
                               caption='Пожалуйста, введите дату своего рождения в формате 15.11.2001')


"""Необходимо реализовать хендлер, который будет обрабатывать некорректный и корректный ввод даты рождения."""

# async def birth_date(message: types.Message, state: FSMContext):
#     birthdate = message.text
#     birth_format = '%d.%m.%Y'
#     await FSMClient.next()
#
#     while True:  # Если дата введена корректно, то выходим из цикла
#         try:
#             datetime.strptime(birthdate, birth_format)  # проверка даты
#             async with state.proxy() as data:
#                 data['birth_date'] = birthdate
#             break
#         except ValueError:
#             await get_background_photo(message, 'media/backgrounds/birthdate-img.jpg',
#                                        caption='Пожалуйста, введите дату своего рождения в формате 15.11.2001')
#
#     await get_background_photo(message, 'media/backgrounds/birthplace-img.jpg',
#                                caption='Пожалуйста, введите место своего рождения')


# async def process_birthdate(message: types.Message, state: FSMContext):
#     if validate_birthdate(message.text):
#         await FSMClient.next()
#     else:
#         await FSMClient.previous()
#         print(FSMClient.)
    # await bot.send_message(text='Спасибо, все в порядке', chat_id=message.chat.id)


def register_handlers_client(disp: Dispatcher):
    disp.register_message_handler(start_command, commands=['start', 'help'], state=None)
    disp.register_message_handler(name_info, state=FSMClient.client_name)
    disp.register_callback_query_handler(gender_info, Text(startswith='gender'), state=FSMClient.client_gender)
    disp.register_message_handler(process_birthdate, state=FSMClient.client_birth_date)
