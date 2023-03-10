from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

client_gender_inline_btn1 = InlineKeyboardButton('Мужчина 👨‍🦱', callback_data='gender_male')
client_gender_inline_btn2 = InlineKeyboardButton('Женщина 👱‍♀️', callback_data='gender_female')
client_gender_inline_kb = InlineKeyboardMarkup().add(client_gender_inline_btn1, client_gender_inline_btn2)

client_morning_inline_btn1 = InlineKeyboardButton('Утро ☀️', callback_data='date_morning')
client_evening_inline_btn2 = InlineKeyboardButton('Вечер 🌙', callback_data='date_evening')
client_date_inline_kb = InlineKeyboardMarkup().add(client_morning_inline_btn1, client_evening_inline_btn2)
