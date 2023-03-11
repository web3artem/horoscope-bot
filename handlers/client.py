from datetime import datetime, date
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery
from asyncpg import UniqueViolationError

from db.schemas.user import User
from keyboards.client_kb import *
from loader import bot
from utils.funcs import get_background_photo, validate_birthdate, validate_time

MESSAGE_ID = None


class FSMClient(StatesGroup):
    client_name = State()
    client_gender = State()
    client_birth_date = State()
    client_birth_place = State()
    client_birth_time = State()
    client_birth_time_set = State()
    client_send_date = State()
    client_agree = State()


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
    if gender == 'gender_male':
        gender = 'Мужчина'
    else:
        gender = 'Женщина'
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
        await FSMClient.client_birth_time.set()
        await bot.send_message(message.chat.id, text='Вы знаете свою дату рождения?', reply_markup=dont_know_inline_kb)


async def birth_time(callback_query: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        await bot.delete_message(callback_query.message.chat.id, data['message_id'])
        data['message_id'] = callback_query.message.message_id + 1
        if callback_query.data == 'know_no':
            await FSMClient.client_send_date.set()
            data['birth_time'] = None
            await get_background_photo(callback_query, 'media/backgrounds/horoscope-time.jpg',
                                       caption='Утром - гороскоп на сегодня\nВечером - гороскоп на завтра',
                                       reply_markup=client_date_inline_kb)
        else:
            await FSMClient.client_birth_time_set.set()
            await get_background_photo(callback_query, 'media/backgrounds/birthtime-img.jpg',
                                       caption='Пожалуйста, введите время своего рождения в таком формате 12:00')


async def set_birth_time(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await bot.delete_message(message.chat.id, data['message_id'])
        data['message_id'] = message.message_id + 1
        data['birth_time'] = message.text
        await FSMClient.next()
        await get_background_photo(message, 'media/backgrounds/horoscope-time.jpg',
                                   caption='Утром - гороскоп на сегодня\nВечером - гороскоп на завтра',
                                   reply_markup=client_date_inline_kb)


async def prepare_datas(callback_query: CallbackQuery, state: FSMContext):
    part_of_the_day = callback_query.data
    if part_of_the_day == 'date_morning':
        part_of_the_day = "Утром"
    else:
        part_of_the_day = "Вечером"
    async with state.proxy() as data:
        await bot.delete_message(callback_query.message.chat.id, data['message_id'])
        data['message_id'] = callback_query.message.message_id + 1
        data['part_of_the_day'] = part_of_the_day
        await FSMClient.next()
        await bot.send_message(callback_query.message.chat.id,
                               text=f'Проверьте, пожалуйста, данные:\nИмя - {data["name"]}'
                                    f'\nПол: {data["gender"]}'
                                    f'\nДата рождения: {data["birth_date"]}'
                                    f'\nМесто рождения: {data["birth_place"]}'
                                    f'\nВремя рождения: {data["birth_time"]}'
                                    f'\nПолучать рассылку: {data["part_of_the_day"]}',
                               reply_markup=agree_inline_kb)


async def agree(callback_query: CallbackQuery, state: FSMContext):
    if callback_query.data == 'agree':
        async with state.proxy() as data:
            await bot.delete_message(callback_query.message.chat.id, data['message_id'])
            user = User(user_id=callback_query.from_user.id,
                        username=callback_query.from_user.username,
                        name=data['name'],
                        gender=data['gender'],
                        birth_date=datetime.strptime(data['birth_date'], '%d.%m.%Y').date(),
                        birth_place=data['birth_place'],
                        birth_time=None if data['birth_time'] is None else datetime.strptime(data['birth_time'],
                                                                                             '%H:%M').time(),
                        receive_day_period=data['part_of_the_day'])
            try:
                await user.create()
            except UniqueViolationError:
                print('Пользователь с таким ключом уже существует')
    else:
        async with state.proxy() as data:
            pass


def register_handlers_client(disp: Dispatcher):
    disp.register_message_handler(start_command, commands=['start', 'help'], state=None)
    disp.register_message_handler(name_info, state=FSMClient.client_name)
    disp.register_callback_query_handler(gender_info, Text(startswith='gender'), state=FSMClient.client_gender)
    disp.register_message_handler(check_birthdate, state=FSMClient.client_birth_date)
    disp.register_message_handler(birthplace_info, state=FSMClient.client_birth_place)
    disp.register_callback_query_handler(birth_time, Text(startswith='know'),
                                         state=FSMClient.client_birth_time)
    disp.register_message_handler(set_birth_time, state=FSMClient.client_birth_time_set)
    disp.register_callback_query_handler(prepare_datas, Text(startswith='date'), state=FSMClient.client_send_date)
    disp.register_callback_query_handler(agree, Text(startswith='agree'), state=FSMClient.client_agree)
