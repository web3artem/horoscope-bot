import datetime
from datetime import timedelta

import aiohttp
from loguru import logger

from aiogram import types
from aiogram.types import InputFile, CallbackQuery
from bs4 import BeautifulSoup
import lxml

from db.db_gino import db
from db.schemas.user import User, Distribution
from loader import bot


async def get_background_photo(message: types.Message | CallbackQuery,
                               path: str, caption=None,
                               text=None,
                               reply_markup=None):
    photo_path = path
    photo = InputFile(photo_path)

    if text is None:
        return await bot.send_photo(message.from_user.id, photo, caption=caption, reply_markup=reply_markup)
    else:
        return await bot.send_message(message.from_user.id, photo, text=text, reply_markup=reply_markup)


def validate_birthdate(birthdate: str):
    try:
        datetime.datetime.strptime(birthdate, '%d.%m.%Y')
        return True
    except ValueError:
        return False


def validate_time(time: str):
    try:
        datetime.datetime.strptime(time, '%H:%M')
        return True
    except ValueError:
        return False


# Функция для проверки существования пользователя в базе данных по user_id
async def user_exists(table_name: db, user_id: int) -> bool:
    query = table_name.query.where(table_name.user_id == user_id)
    result = await db.scalar(query)
    return bool(result)


def zodiac_sign(date_of_birth: datetime.date):
    day = date_of_birth.day
    month = date_of_birth.strftime('%B').lower()
    astro_sign = None
    if month == 'december':
        astro_sign = 'sagittarius' if (day < 22) else 'capricorn'

    elif month == 'january':
        astro_sign = 'capricorn' if (day < 20) else 'aquarius'

    elif month == 'february':
        astro_sign = 'aquarius' if (day < 19) else 'pisces'

    elif month == 'march':
        astro_sign = 'pisces' if (day < 21) else 'aries'

    elif month == 'april':
        astro_sign = 'aries' if (day < 20) else 'taurus'

    elif month == 'may':
        astro_sign = 'taurus' if (day < 21) else 'gemini'

    elif month == 'june':
        astro_sign = 'gemini' if (day < 21) else 'cancer'

    elif month == 'july':
        astro_sign = 'cancer' if (day < 23) else 'leo'

    elif month == 'august':
        astro_sign = 'leo' if (day < 23) else 'virgo'

    elif month == 'september':
        astro_sign = 'virgo' if (day < 23) else 'libra'

    elif month == 'october':
        astro_sign = 'libra' if (day < 23) else 'scorpio'

    elif month == 'november':
        astro_sign = 'scorpio' if (day < 22) else 'sagittarius'

    return astro_sign


# Функция для ежедневной генерации шапки гороскопа
async def generate_horoscope_header(user_id):
    month_dict = {
        1: 'Января',
        2: 'Февраля',
        3: 'Марта',
        4: 'Апреля',
        5: 'Мая',
        6: 'Июня',
        7: 'Июля',
        8: 'Августа',
        9: 'Сентября',
        10: 'Октября',
        11: 'Ноября',
        12: 'Декабря'
    }
    today = datetime.date.today()
    day = today.day
    month = today.month
    tomorrow = (today + timedelta(days=1)).day

    data = User.select('gender', 'name', 'receive_day_period').where(User.user_id == user_id)
    data = await db.all(data)
    gender = data[0][0]
    name = data[0][1]
    day_period = data[0][2]

    if gender == 'Мужчина':
        dear = 'Дорогой'
    else:
        dear = 'Дорогая'

    if day_period == 'tomorrow':
        return f'<b>{dear} {name}, завтра {tomorrow} {month_dict[month]}\n\nОбщий гороскоп дня.\n</b>'
    else:
        return f'<b>{dear} {name}, сегодня {day} {month_dict[month]}\n\nОбщий гороскоп дня.\n</b>'


async def career_horoscope(zodiac: str, part_of_day: str = None):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://astrohelper.ru/career-horoscope/{zodiac}' if part_of_day == 'morning' else
                               f'https://astrohelper.ru/career-horoscope/{zodiac}/tomorrow') as response:
            resp = await response.text()
            soup = BeautifulSoup(resp, 'lxml')
            res = soup.find_all('div', class_='mt-3')[0]
            result = '. '.join(res.text.split('.')[:2]) + '.'
            return result


async def health_horoscope(zodiac: str, part_of_day: str = None):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://astrohelper.ru/health-horoscope/{zodiac}' if part_of_day == 'morning' else
                               f'https://astrohelper.ru/health-horoscope/{zodiac}/tomorrow') as response:
            resp = await response.text()
            soup = BeautifulSoup(resp, 'lxml')
            res = soup.find_all('div', class_='mt-3')[0]
            result = '. '.join(res.text.split('.')[:2]) + '.'
            return result


async def love_horoscope(zodiac: str, part_of_day: str = None):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://astrohelper.ru/love-horoscope/{zodiac}' if part_of_day == 'morning' else
                               f'https://astrohelper.ru/love-horoscope/{zodiac}/tomorrow') as response:
            resp = await response.text()
            soup = BeautifulSoup(resp, 'lxml')
            res = soup.find_all('div', class_='mt-3')[0]
            result = '. '.join(res.text.split('.')[:2]) + '.'
            return result


async def finance_horoscope(zodiac: str, part_of_day: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f'https://astrohelper.ru/finance-horoscope/{zodiac}/tomorrow/' if part_of_day == 'tomorrow'
                else f'https://astrohelper.ru/finance-horoscope/{zodiac}/') as response:
            resp = await response.text()
            soup = BeautifulSoup(resp, 'lxml')
            res = soup.find_all('div', class_='mt-3')[0]
            result = '. '.join(res.text.split('.')[:2]) + '.'
            return result


async def main_horoscope(zodiac: str, part_of_day: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f'https://astrohelper.ru/horoscope/{zodiac}/tomorrow/' if part_of_day == 'tomorrow'
                else f'https://astrohelper.ru/horoscope/{zodiac}/') as response:
            resp = await response.text()
            soup = BeautifulSoup(resp, 'lxml')
            res = soup.find_all('div', class_='mt-3')[0]
            result = '. '.join(res.text.split('.')[:2]) + '.'
            return result


async def generate_horoscope_for_today(user_id: int, time_preference: str):
    zodiac_signs = {
        "aries": "Овен",
        "taurus": "Телец",
        "gemini": "Близнецы",
        "cancer": "Рак",
        "leo": "Лев",
        "virgo": "Дева",
        "libra": "Весы",
        "scorpio": "Скорпион",
        "sagittarius": "Стрелец",
        "capricorn": "Козерог",
        "aquarius": "Водолей",
        "pisces": "Рыбы"
    }
    user = await User.select('birth_date').where(User.user_id == user_id).gino.first()
    zodiac = zodiac_sign(user.birth_date)
    with open('media/backgrounds/astro-background.jpg', 'rb') as photo:
        await bot.send_photo(user_id, photo, caption=f'{await generate_horoscope_header(user_id)}\n'
                                                     f'{await main_horoscope(zodiac, time_preference)}')
        await bot.send_message(user_id,
                               text=f'<b>Твой персональный гороскоп. {zodiac_signs[zodiac]}.</b>'
                                    f'\n\n💼 💼 💼\n\n{await career_horoscope(zodiac, time_preference)}'
                                    f'\n\n❤️ ❤️ ❤️\n\n{await love_horoscope(zodiac, time_preference)}'
                                    f'\n\n💰 💰 💰\n\n{await finance_horoscope(zodiac, time_preference)}'
                                    f'\n\n🏥🏥🏥\n\n{await health_horoscope(zodiac, time_preference)}'
                                    f'\n\n\n<b>Прекрасного дня!</b> 🌸🌸🌸')


# Отправляем готовый гороскоп (Шапка + body)
async def prepare_data(user_id: int):
    logger.info(f'Формируется гороскоп для пользователя {user_id}')
    data = await User.select('receive_day_period').where(User.user_id == user_id).gino.first()
    time_preference = data[0]
    await Distribution.update.values(was_sent=True).where(Distribution.id == user_id).gino.status()
    await generate_horoscope_for_today(user_id, time_preference)
    logger.info(f'Гороскоп был отправлен пользователю {user_id}')


def validate_str_len(msg: str, str_len: int):
    if len(msg) > str_len:
        return False
    return True
