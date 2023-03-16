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


# Здесь необходимо ввести айдишник для доступа к админке. Получить можно в тг боте https://t.me/getmyid_bot

async def admin_start(message: types.Message):
    await message.answer(
        text='Добро пожаловать в админку. Выберите действие на клавиатуре',
        reply_markup=admin_main_kb)


async def post_creation(message: types.Message):
    await message.delete()
    await FSMAdmin.AdminPhoto.set()
    await bot.send_message(message.from_user.id, text='Добавить фото к посту?', reply_markup=admin_post_kb)


async def photo_for_post(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'photo_yes':
        await FSMAdmin.AdminPhotoLoading.set()
        await callback_query.answer()
        await bot.send_message(callback_query.from_user.id, text='Загрузите, пожалуйста, фото')
    else:
        await FSMAdmin.AdminDesc.set()
        await callback_query.answer()
        await bot.send_message(callback_query.from_user.id, text='Введите текст поста')


async def photo_loading(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = message.photo[0].file_id
        await FSMAdmin.AdminDesc.set()
        await message.answer(text='Фото было успешно загружено, теперь введите текст поста')


async def desc_loading(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['desc'] = message.text
        await FSMAdmin.AdminSummarize.set()
        await message.answer(text='Описание было успешно добавлено, проверьте, пожалуйста, все ли правильно?')

        try:
            await bot.send_photo(message.from_user.id, photo=data['photo'])
        except Exception as e:
            print(e)
        await bot.send_message(message.from_user.id, text=data['desc'], reply_markup=admin_correct_kb)


async def summarize(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'correct_yes':
        async with state.proxy() as data:
            rows = await User.query.gino.all()
            for row in rows:
                if row.user_id in ADMINS:
                    continue
                try:
                    await bot.send_photo(row.user_id, photo=data['photo'])
                except Exception as ex:
                    if type(ex) == BotBlocked:
                        await Distribution.delete.where(Distribution.id == row.user_id).gino.status()
                        logger.info(
                            f'Пользователь {row.user_id} - {row.username} был удален из базы по причине блокировки бота')
                        await User.delete.where(User.user_id == row.user_id).gino.status()
                    logger.error(f'Ошибка при отправке фото пользователю {row.user_id}: {ex}')
                await callback_query.answer()
                try:
                    await bot.send_message(row.user_id, text=data['desc'])
                    await bot.send_message(callback_query.from_user.id, text="Пост был успешно отправлен")
                except Exception as ex:
                    if type(ex) == BotBlocked:
                        await Distribution.delete.where(Distribution.id == callback_query.from_user.id).gino.status()
                        await User.delete.where(User.user_id == callback_query.from_user.id).gino.status()
                        logger.info(
                            f'Пользователь {row.user_id} - {row.username} был удален из базы по причине блокировки бота')
                    logger.error(f'Ошибка при отправке фото пользователю {row.user_id}: {ex}')

                await state.finish()
    else:
        await callback_query.answer()
        await FSMAdmin.AdminChange.set()
        await bot.send_message(callback_query.from_user.id,
                               "Что необходимо изменить?", reply_markup=admin_change_kb)


async def change(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'photo_change':
        await FSMAdmin.AdminPhotoLoading.set()
        await callback_query.answer()
        await bot.send_message(callback_query.from_user.id, 'Загрузите корректное фото')
    else:
        await FSMAdmin.AdminDesc.set()
        await callback_query.answer()
        await bot.send_message(callback_query.from_user.id, 'Введите текст поста')


async def change_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = message.photo[0].file_id
        await FSMAdmin.AdminPhotoLoading.set()


async def change_desc(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['desc'] = message.text
        await FSMAdmin.AdminDesc.set()


def register_handlers_admin(disp: Dispatcher):
    disp.register_message_handler(admin_start, IsAdmin(), commands=['admin'])
    # Отправление поста всем пользователям
    disp.register_message_handler(post_creation, IsAdmin(), Text(equals='Отправить пост'))
    disp.register_callback_query_handler(photo_for_post, IsAdmin(), state=FSMAdmin.AdminPhoto)
    disp.register_message_handler(photo_loading, IsAdmin(), content_types='photo', state=FSMAdmin.AdminPhotoLoading)
    disp.register_message_handler(desc_loading, IsAdmin(), state=FSMAdmin.AdminDesc)
    disp.register_callback_query_handler(summarize, IsAdmin(), state=FSMAdmin.AdminSummarize)
    disp.register_callback_query_handler(change, IsAdmin(), state=FSMAdmin.AdminChange)
    disp.register_message_handler(change_photo, IsAdmin(), content_types='photo', state=FSMAdmin.AdminChangePhoto)

    # Отправка гороскопа на утро

