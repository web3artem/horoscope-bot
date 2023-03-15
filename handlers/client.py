import asyncio
import sys
from datetime import datetime

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery
from aiogram.utils.exceptions import BotBlocked, MessageToDeleteNotFound
from asyncpg import UniqueViolationError
from loguru import logger

from db.db_gino import db
from db.quick_commands import delete_mess, save_message_id
from db.schemas.user import User, MessageId, Distribution
from keyboards.client_kb import *
from loader import bot
from states.states import FSMClientRegistration
from utils import funcs

logger.add(sys.stderr, format="<white>{time:HH:mm:ss}</white>"
                              " | <green>{level: <8}</green>"
                              " | <cyan>{line}</cyan>"
                              " - <white>{message}</white>")
logger.add('logs/file_{time}.log')


async def start_command(message: types.Message):
    if await funcs.user_exists(User, message.from_user.id):
        await message.answer('Здравствуйте.\n\nСпасибо, что вернулись в нашего бота. Вы получите гороскоп по '
                             'расписанию.\n\nЕсли хотите получить его сейчас нажмите на соответствующую кнопку в меню.')
        logger.info(f'Пользователь {message.from_user.id} - {message.from_user.username} уже зарегистрирован..')
    else:
        await message.delete()
        await FSMClientRegistration.client_name.set()
        mess = await funcs.get_background_photo(message, 'media/backgrounds/background-name.jpg')
        logger.info(f'Пользователь {message.from_user.id} - {message.from_user.username} начал регистрацию.')
        # Создание записи в БД для удаления сообщений

        await MessageId(user_id=message.from_user.id, message_id=mess.message_id).create()


# Функция рассылки
async def schedule(time_dilation: int):
    now = datetime.now()
    await asyncio.sleep(time_dilation)

    counter = 0

    while True:
        dist = await Distribution.select('id', 'was_sent').gino.all()

        for user_id, flag in dist:
            if counter == len(dist):
                counter = 0
                await asyncio.sleep(3600)

            if now.hour == 1 and await User.select('receive_day_period').where(
                    User.user_id == user_id).gino.scalar() == 'morning':
                await Distribution.update.values(was_sent=False).where(Distribution.id == user_id).gino.status()

            if now.hour == 19 and await User.select('receive_day_period').where(
                    User.user_id == user_id).gino.scalar() == 'tomorrow':
                await Distribution.update.values(was_sent=False).where(Distribution.id == user_id).gino.status()

            if not await Distribution.select('was_sent').where(Distribution.id == user_id).gino.scalar():
                # Обрабатываем, если бот заблочен
                try:
                    await funcs.prepare_data(user_id)
                    counter += 1
                except BotBlocked:
                    logger.info(f'Пользователь {user_id} заблокировал бот.')
                    await Distribution.delete.where(Distribution.id == user_id).gino.status()
                    await User.delete.where(User.user_id == user_id).gino.status()


async def send(message: types.Message | CallbackQuery):
    user_id = message.from_user.id
    logger.info(f'Пользователь {user_id} - {message.from_user.username} запросил гороскоп с помощью /send.')

    if await funcs.user_exists(User, user_id):
        try:
            await message.answer('Отправляем гороскоп ❤️ ❤️ ❤️')
            await funcs.prepare_data(user_id)

            if await Distribution.query.where(Distribution.id == user_id).gino.scalar() is None:
                await Distribution(id=user_id, was_sent=True).create()

        except Exception as ex:
            logger.error(ex)
    else:
        await message.answer('Вы пока не прошли регистрацию, введите /start')


async def change(message: types.Message | CallbackQuery):
    await FSMClientRegistration.client_change_info.set()
    logger.info(f'Пользователь {message.from_user.id} хочет изменить данные')
    if type(message) == types.Message:
        await bot.send_message(message.chat.id,
                               text='Выберите какие данные необходимо изменить 🥺',
                               reply_markup=change_inline_kb)
    else:
        await bot.send_message(message.message.chat.id,
                               text='Выберите какие данные необходимо изменить 🥺',
                               reply_markup=change_inline_kb)


async def get_my_info(message: types.Message | CallbackQuery):
    data = User.select('name', 'gender', 'birth_date', 'birth_place', 'birth_time', 'receive_day_period').where(
        User.user_id == message.from_user.id)
    data = await db.all(data)

    if data[0][5] == 'tomorrow':
        time_preference = 'Утром'
    else:
        time_preference = 'Вечером'

    await message.answer(text=f'Имя: {data[0][0]}\n\n'
                              f'Пол: {data[0][1]}\n\n'
                              f'Дата рождения: {data[0][2]}\n\n'
                              f'Место рождения: {data[0][3]}\n\n'
                              f'Время рождения: {data[0][4] if not None else "Не знаете"}\n\n'
                              f'Получать рассылку: {time_preference}\n\n'
                              f'Если какие-либо данные неправильные, то выполните команду /change')


async def name_info(message: types.Message, state: FSMContext):
    await message.delete()

    if not funcs.validate_str_len(message.text, 32):
        try:
            await bot.delete_message(message.chat.id, delete_mess(message.from_user.id))
        except MessageToDeleteNotFound:
            pass
        mes = await message.answer(text='Имя должно быть не более 32 символов\n\nВведите, пожалуйста, корректное имя ')
        await save_message_id(message, mes.message_id)
        await FSMClientRegistration.client_name.set()

    else:
        try:
            await bot.delete_message(message.chat.id, await delete_mess(message))
        except MessageToDeleteNotFound:
            pass
        async with state.proxy() as data:
            data['name'] = message.text
            data['user_id'] = message.from_user.id
        await FSMClientRegistration.next()
        mes = await funcs.get_background_photo(message, 'media/backgrounds/background-gender.jpg',
                                               reply_markup=client_gender_inline_kb)
        await save_message_id(message, mes.message_id)


async def gender_info(callback_query: CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(callback_query.message.chat.id, await delete_mess(callback_query))
    except MessageToDeleteNotFound:
        pass
    gender = callback_query.data
    if gender == 'gender_male':
        gender = 'Мужчина'
    else:
        gender = 'Женщина'
    async with state.proxy() as data:
        data['gender'] = gender
    await FSMClientRegistration.next()
    await callback_query.answer()
    mes = await funcs.get_background_photo(callback_query, 'media/backgrounds/birthdate-img.jpg',
                                           caption='Пожалуйста, введите дату своего рождения в формате 01.01.1111')
    await save_message_id(callback_query, mes.message_id)


async def check_birthdate(message: types.Message, state: FSMContext):
    await message.delete()
    if funcs.validate_birthdate(message.text):
        await bot.delete_message(message.chat.id, await delete_mess(message))
        async with state.proxy() as data:
            data['birth_date'] = message.text
        await FSMClientRegistration.next()
        mes = await funcs.get_background_photo(message, 'media/backgrounds/birthplace-img.jpg',
                                               caption='Пожалуйста, введите место своего рождения')
        await save_message_id(message, mes.message_id)
    else:
        mes = await funcs.get_background_photo(message, 'media/backgrounds/birthdate-img.jpg',
                                               caption='Пожалуйста, введите дату своего рождения в формате 01.01.1111')
        try:
            await bot.delete_message(message.chat.id, await delete_mess(message))
        except MessageToDeleteNotFound:
            pass
        await save_message_id(message, mes.message_id)


async def birthplace_info(message: types.Message, state: FSMContext):
    await message.delete()
    try:
        await bot.delete_message(message.chat.id, await delete_mess(message))
    except MessageToDeleteNotFound:
        pass
    async with state.proxy() as data:
        data['birth_place'] = message.text
        await FSMClientRegistration.client_birth_time.set()
        mes = await bot.send_message(message.chat.id, text='Вы знаете свое время рождения?',
                                     reply_markup=dont_know_inline_kb)
        await save_message_id(message, mes.message_id)


async def birth_time(callback_query: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        try:
            await bot.delete_message(callback_query.message.chat.id, await delete_mess(callback_query))
        except MessageToDeleteNotFound:
            pass
        if callback_query.data == 'know_no':
            await FSMClientRegistration.client_send_date.set()
            data['birth_time'] = None
            await callback_query.answer()
            mes = await funcs.get_background_photo(callback_query, 'media/backgrounds/horoscope-time.jpg',
                                                   caption='Утром - гороскоп на сегодня\nВечером - гороскоп на завтра',
                                                   reply_markup=client_date_inline_kb)
            await save_message_id(callback_query, mes.message_id)
        else:
            await FSMClientRegistration.client_birth_time_set.set()
            await callback_query.answer()
            mes = await funcs.get_background_photo(callback_query, 'media/backgrounds/birthtime-img.jpg',
                                                   caption='Пожалуйста, введите время своего рождения в таком формате 12:00')
            await save_message_id(callback_query, mes.message_id)


async def set_birth_time(message: types.Message, state: FSMContext):
    await message.delete()
    try:
        await bot.delete_message(message.chat.id, await delete_mess(message))
    except MessageToDeleteNotFound:
        pass
    if funcs.validate_time(message.text):
        birthtime = message.text
    else:
        birthtime = None

    async with state.proxy() as data:
        data['birth_time'] = birthtime
        await FSMClientRegistration.next()
        mes = await funcs.get_background_photo(message, 'media/backgrounds/horoscope-time.jpg',
                                               caption='Утром - гороскоп на сегодня\nВечером - гороскоп на завтра',
                                               reply_markup=client_date_inline_kb)
        await save_message_id(message, mes.message_id)


async def prepare_datas(callback_query: CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(callback_query.message.chat.id, await delete_mess(callback_query))
    except MessageToDeleteNotFound:
        pass
    part_of_the_day = callback_query.data
    if part_of_the_day == 'date_morning':
        part_of_the_day = "Утром"
    else:
        part_of_the_day = "Вечером"
    async with state.proxy() as data:
        data['part_of_the_day'] = part_of_the_day
        await FSMClientRegistration.next()
        mes = await bot.send_message(callback_query.message.chat.id,
                                     text=f'Проверьте, пожалуйста, данные:\nИмя: {data["name"]}'
                                          f'\nПол: {data["gender"]}'
                                          f'\nДата рождения: {data["birth_date"]}'
                                          f'\nМесто рождения: {data["birth_place"]}'
                                          f'\nВремя рождения: {data["birth_time"]}'
                                          f'\nПолучать рассылку: {data["part_of_the_day"]}',
                                     reply_markup=agree_inline_kb)
        await save_message_id(callback_query, mes.message_id)
        await callback_query.answer()


async def agree(callback_query: CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(callback_query.message.chat.id, await delete_mess(callback_query))
    except MessageToDeleteNotFound:
        pass
    async with state.proxy() as data:
        if data['part_of_the_day'] == 'Утром':
            time_preference = 'morning'
        else:
            time_preference = 'tomorrow'
        user = User(user_id=callback_query.from_user.id,
                    username=callback_query.from_user.username,
                    name=data['name'],
                    gender=data['gender'],
                    birth_date=datetime.strptime(data['birth_date'], '%d.%m.%Y').date(),
                    birth_place=data['birth_place'],
                    birth_time=None if data['birth_time'] is None else datetime.strptime(data['birth_time'],
                                                                                         '%H:%M').time(),
                    receive_day_period=time_preference)
        try:
            await user.create()
            logger.info(f'Пользователь {callback_query.from_user.id} - {callback_query.from_user.username}'
                        f' успешно зарегистрирован в базе данных.')
        except UniqueViolationError:
            logger.error(f'Пользователь {callback_query.from_user.id} - {callback_query.from_user.username}'
                         f' ранее был зарегистрирован.')

        if callback_query.data == 'client_agree':
            await send(callback_query)
            await callback_query.answer()

        else:
            await FSMClientRegistration.client_change_info.set()
            mes = await bot.send_message(callback_query.message.chat.id,
                                         text='Выберите какие данные необходимо изменить 🥺',
                                         reply_markup=change_inline_kb)
            await save_message_id(callback_query, mes.message_id)
            await callback_query.answer()


async def change_info(callback_query: CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(callback_query.message.chat.id, await delete_mess(callback_query))
    except MessageToDeleteNotFound:
        pass
    async with state.proxy() as data:
        data_to_change = callback_query.data.split('_')[1]
        if data_to_change != 'receive':
            await FSMClientRegistration.client_what_to_change.set()
            if data_to_change == 'birthtime':
                if funcs.validate_time(data_to_change):
                    birthtime = data_to_change
                else:
                    birthtime = None
            data['data_to_change'] = birthtime
            mes = await bot.send_message(callback_query.message.chat.id,
                                         text='Введите корректные данные 😌')
            await save_message_id(callback_query, mes.message_id)
            await callback_query.answer()
        else:
            await FSMClientRegistration.client_daytime_change.set()
            with open('media/backgrounds/horoscope-time.jpg', 'rb') as photo:
                await bot.send_photo(callback_query.message.chat.id,
                                     reply_markup=client_day_inline_kb, photo=photo)
                await callback_query.answer()


async def what_to_change(message: types.Message, state: FSMContext):
    try:
        await bot.delete_message(message.chat.id, await delete_mess(message))
    except MessageToDeleteNotFound:
        pass
    await message.delete()
    user = User(user_id=message.from_user.id)
    async with state.proxy() as data:
        match data['data_to_change']:
            case 'name':
                await user.update(name=message.text).apply()
            case 'gender':
                await user.update(gender=message.text).apply()
            case 'date':
                await user.update(birth_date=datetime.strptime(message.text, '%d.%m.%Y').date()).apply()
            case 'birthplace':
                await user.update(birth_place=message.text).apply()
            case 'birthtime':
                await user.update(birth_time=datetime.strptime(message.text, '%H:%M').time()).apply()
        mes = await bot.send_message(message.from_user.id,
                                     text='Данные были успешно изменены 😄')
        await save_message_id(message, mes.message_id)
        logger.info(f'Пользователь {message.from_user.id} изменил данные')
        await state.finish()
        await send(message)


async def change_daytime(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    if callback_query.data == "day_morning":
        day_info = 'morning'
    else:
        day_info = 'tomorrow'
    user = User(user_id=callback_query.from_user.id)
    await user.update(receive_day_period=day_info).apply()
    await bot.send_message(callback_query.from_user.id,
                           text='Данные были успешно изменены 😄')
    logger.info(f'Пользователь {callback_query.from_user.id} изменил время получение гороскопа')
    await send(callback_query)
    await callback_query.answer()


def register_handlers_client(disp: Dispatcher):
    disp.register_message_handler(start_command, commands=['start', 'help'], state='*')
    disp.register_message_handler(name_info, state=FSMClientRegistration.client_name)
    disp.register_callback_query_handler(gender_info, Text(startswith='gender'),
                                         state=FSMClientRegistration.client_gender)
    disp.register_message_handler(check_birthdate, state=FSMClientRegistration.client_birth_date)
    disp.register_message_handler(birthplace_info, state=FSMClientRegistration.client_birth_place)
    disp.register_callback_query_handler(birth_time, Text(startswith='know'),
                                         state=FSMClientRegistration.client_birth_time)
    disp.register_message_handler(set_birth_time, state=FSMClientRegistration.client_birth_time_set)
    disp.register_callback_query_handler(prepare_datas, Text(startswith='date'),
                                         state=FSMClientRegistration.client_send_date)
    disp.register_callback_query_handler(agree, Text(startswith='client'), state=FSMClientRegistration.client_agree)
    disp.register_callback_query_handler(change_info, Text(startswith='change'),
                                         state=FSMClientRegistration.client_change_info)
    disp.register_message_handler(what_to_change, state=FSMClientRegistration.client_what_to_change)
    disp.register_callback_query_handler(change_daytime, Text(startswith='day'),
                                         state=FSMClientRegistration.client_daytime_change)
    disp.register_message_handler(send, commands=['send'], state='*')
    disp.register_message_handler(change, commands=['change'], state='*')
    disp.register_message_handler(get_my_info, commands=['get_info'], state='*')
