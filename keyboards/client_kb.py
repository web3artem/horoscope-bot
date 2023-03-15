from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import callback_data

client_gender_inline_btn1 = InlineKeyboardButton('Мужчина 👨‍🦱', callback_data='gender_male')
client_gender_inline_btn2 = InlineKeyboardButton('Женщина 👱‍♀️', callback_data='gender_female')
client_gender_inline_kb = InlineKeyboardMarkup().add(client_gender_inline_btn1, client_gender_inline_btn2)

client_morning_inline_btn1 = InlineKeyboardButton('Утро ☀️', callback_data='date_morning')
client_evening_inline_btn2 = InlineKeyboardButton('Вечер 🌙', callback_data='date_evening')
client_date_inline_kb = InlineKeyboardMarkup().add(client_morning_inline_btn1, client_evening_inline_btn2)

agree_inline_btn1 = InlineKeyboardButton('Да ✅', callback_data='client_agree')
decline_inline_btn2 = InlineKeyboardButton('Нет ❌', callback_data='client_decline')
agree_inline_kb = InlineKeyboardMarkup().add(agree_inline_btn1, decline_inline_btn2)

dont_know_inline_btn1 = InlineKeyboardButton('Не знаю ❌', callback_data='know_no')
know_inline_btn2 = InlineKeyboardButton('Знаю ✅', callback_data='know_yes')
dont_know_inline_kb = InlineKeyboardMarkup().add(know_inline_btn2, dont_know_inline_btn1)

change_name_inline_btn1 = InlineKeyboardButton('Имя', callback_data='change_name')
change_date_inline_btn3 = InlineKeyboardButton('Дата рождения', callback_data='change_date')
change_receive_day_period_inline_btn6 = InlineKeyboardButton('В какое время получать гороскоп?',
                                                             callback_data='change_receive_day_period')
change_inline_kb = InlineKeyboardMarkup().add(change_name_inline_btn1, change_date_inline_btn3).add(
    change_receive_day_period_inline_btn6
)

client_morning_inline_btn1 = InlineKeyboardButton('Утро ☀️', callback_data='day_morning')
client_evening_inline_btn2 = InlineKeyboardButton('Вечер 🌙', callback_data='day_evening')
client_day_inline_kb = InlineKeyboardMarkup().add(client_morning_inline_btn1, client_evening_inline_btn2)

client_registration_inline_btn1 = InlineKeyboardButton('Спасибо 😎', callback_data='registration')
client_registration_inline_kb = InlineKeyboardMarkup().add(client_registration_inline_btn1)
