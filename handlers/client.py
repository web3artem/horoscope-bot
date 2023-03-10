from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery

from create_bot import bot
from keyboards.client_kb import client_gender_inline_kb, client_date_inline_kb
from services.funcs import get_background_photo, validate_birthdate, validate_time

MESSAGE_ID = None


class FSMClient(StatesGroup):
    client_name = State()
    client_gender = State()
    client_birth_date = State()
    client_birth_place = State()
    client_birth_time = State()


async def start_command(message: types.Message):
    global MESSAGE_ID
    await message.delete()
    await FSMClient.client_name.set()
    await get_background_photo(message, 'media/backgrounds/background-name.jpg')
    MESSAGE_ID = message.message_id + 1


async def name_info(message: types.Message, state: FSMContext):
    await message.delete()
    await bot.delete_message(message.chat.id, MESSAGE_ID)
    async with state.proxy() as data:
        data['name'] = message.text
        data['message_id'] = message.message_id + 1
    await FSMClient.next()
    await get_background_photo(message, 'media/backgrounds/background-gender.jpg', reply_markup=client_gender_inline_kb)


async def gender_info(callback_query: CallbackQuery, state: FSMContext):
    gender = callback_query.data
    async with state.proxy() as data:
        await bot.delete_message(callback_query.message.chat.id, data['message_id'])
        data['gender'] = gender
        data['message_id'] = callback_query.message.message_id + 1
    await FSMClient.next()

    await get_background_photo(callback_query, 'media/backgrounds/birthdate-img.jpg',
                               caption='Пожалуйста, введите дату своего рождения в формате 15.11.2001')


"""Необходимо реализовать хендлер, который будет обрабатывать некорректный и корректный ввод даты рождения."""


async def check_birthdate(message: types.Message, state: FSMContext):
    await message.delete()
    if validate_birthdate(message.text):
        async with state.proxy() as data:
            await bot.delete_message(message.chat.id, data['message_id'])
            data['birth_date'] = message.text
            data['message_id'] = message.message_id + 1
        await FSMClient.next()
        await get_background_photo(message, 'media/backgrounds/birthplace-img.jpg',
                                   caption='Пожалуйста, введите место своего рождения')
    else:
        async with state.proxy() as data:
            await bot.delete_message(message.chat.id, data['message_id'])
            data['message_id'] = message.message_id + 1
        await get_background_photo(message, 'media/backgrounds/birthdate-img.jpg',
                                   caption='Пожалуйста, введите дату своего рождения в формате 15.11.2001')


async def birthplace_info(message: types.Message, state: FSMContext):
    await message.delete()
    async with state.proxy() as data:
        await bot.delete_message(message.chat.id, data['message_id'])
        data['birth_place'] = message.text
        data['message_id'] = message.message_id + 1
        await FSMClient.next()
        await get_background_photo(message, 'media/backgrounds/birthtime-img.jpg',
                                   caption='Пожалуйста, введите время своего рождения в таком формате 12:00')


async def birthtime_info(message: types.Message, state: FSMContext):
    await message.delete()
    if validate_time(message.text):
        async with state.proxy() as data:
            await bot.delete_message(message.chat.id, data['message_id'])
            data['birth_time'] = message.text
            data['message_id'] = message.message_id + 1
            print(data)
        await FSMClient.next()
        await get_background_photo(message, 'media/backgrounds/horoscope-time.jpg',
                                   caption='Утром - гороскоп на сегодняшний день\nВечером - гороскоп на завтрашний день',
                                   reply_markup=client_date_inline_kb)
    else:
        async with state.proxy() as data:
            await bot.delete_message(message.chat.id, data['message_id'])
            data['message_id'] = message.message_id + 1
        await get_background_photo(message, 'media/backgrounds/birthtime-img.jpg',
                                   caption='Пожалуйста, введите время своего рождения в таком формате 12:00')


def register_handlers_client(disp: Dispatcher):
    disp.register_message_handler(start_command, commands=['start', 'help'], state=None)
    disp.register_message_handler(name_info, state=FSMClient.client_name)
    disp.register_callback_query_handler(gender_info, Text(startswith='gender'), state=FSMClient.client_gender)
    disp.register_message_handler(check_birthdate, state=FSMClient.client_birth_date)
    disp.register_message_handler(birthplace_info, state=FSMClient.client_birth_place)
    disp.register_message_handler(birthtime_info, state=FSMClient.client_birth_time)
