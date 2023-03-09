from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from create_bot import dp

# Здесь необходимо ввести айдишник для доступа к админке. Получить можно в тг боте https://t.me/getmyid_bot
ADMIN_ID = 6083753042


class FSMAdmin(StatesGroup):
    photo = State()
    description = State()


# Начало диалога загрузки нового поста
# @dp.message_handler(commands='Загрузить пост', state=None)
async def cm_start(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await FSMAdmin.photo.set()
        await message.answer('Отправьте фото поста')
    else:
        await message.answer('Вы не являетесь администратором!')


# Ловим первый ответ и пишем в словарь
# @dp.message_handler(content_types=['photo'], state=FSMAdmin.description)
async def load_photo(message: types.Message, state: FSMContext):
    if message.from_user.id == ADMIN_ID:
        async with state.proxy() as data:
            data['photo'] = message.photo[0].file_id
            await FSMAdmin.next()
            await message.answer('Теперь введите текст поста')
    else:
        await message.answer('Вы не являетесь администратором!')


# Ловим второй ответ
# @dp.message_handler(state=FSMAdmin.description)
async def load_description(message: types.Message, state: FSMContext):
    if message.from_user.id == ADMIN_ID:
        async with state.proxy() as data:
            data['description'] = message.text

        async with state.proxy() as data:
            await message.reply(str(data))
        await state.finish()
    else:
        await message.answer('Вы не являетесь администратором!')


# @dp.message_handler(state='*', commands='Отмена')
# @dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    if message.from_user.id == ADMIN_ID:
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()
        await message.reply('OK')
    else:
        await message.answer('Вы не являетесь администратором!')


def register_handlers_admin(disp: Dispatcher):
    disp.register_message_handler(cm_start, commands=['Загрузить'], state=None)
    disp.register_message_handler(load_photo, content_types=['photo'], state=FSMAdmin.photo)
    disp.register_message_handler(load_description, state=FSMAdmin.description)
    dp.register_message_handler(cancel_handler, state='*', commands='Отмена')
    dp.register_message_handler(cancel_handler, Text(equals='отмена', ignore_case=True), state='*')
