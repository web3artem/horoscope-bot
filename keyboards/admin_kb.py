from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

admin_main_kb = ReplyKeyboardMarkup([
    [KeyboardButton(text='Отправить пост'), KeyboardButton(text='Добавить администратора')],
    [KeyboardButton(text='Отправить гороскоп на утро'), KeyboardButton(text='Отправить гороскоп на вечер')]],
    resize_keyboard=True, one_time_keyboard=True)

admin_photo_yes_b1 = InlineKeyboardButton(text='Да ✅', callback_data='photo_yes')
admin_photo_no_b2 = InlineKeyboardButton(text='Нет ❌', callback_data='photo_no')
admin_post_kb = InlineKeyboardMarkup().add(admin_photo_yes_b1, admin_photo_no_b2)

admin_correct_yes_b1 = InlineKeyboardButton(text='Да ✅', callback_data='correct_yes')
admin_correct_no_b2 = InlineKeyboardButton(text='Нет ❌', callback_data='correct_no')
admin_correct_kb = InlineKeyboardMarkup().add(admin_correct_yes_b1, admin_correct_no_b2)

admin_change_b1 = InlineKeyboardButton(text='Фото', callback_data='photo_change')
admin_change_b2 = InlineKeyboardButton(text='Описание', callback_data='desc_change')
admin_change_kb = InlineKeyboardMarkup().add(admin_change_b1, admin_change_b2)
