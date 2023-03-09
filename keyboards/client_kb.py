from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

client_gender_inline_btn1 = InlineKeyboardButton('Мужчина 👨‍🦱', callback_data='gender_male')
client_gender_inline_btn2 = InlineKeyboardButton('Женщина 👱‍♀️', callback_data='gender_female')
client_gender_inline_kb = InlineKeyboardMarkup().add(client_gender_inline_btn1, client_gender_inline_btn2)
