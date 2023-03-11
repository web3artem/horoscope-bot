import datetime
import string

from asyncpg import UniqueViolationError

from db.db_gino import db
from db.schemas.user import User


async def add_user(user_id: int, username: str, name: str,
                   gender: str, birthdate,
                   birthplace: str, day_or_night: str, birthtime = None):
    try:
        user = User(user_id=user_id, username=username, name=name,
                    gender=gender, birth_date=birthdate, birth_place=birthplace,
                    birth_time=birthtime, receive_day_period=day_or_night)
        await user.create()
    except UniqueViolationError:
        print("Пользователь не добавлен")


async def select_all_users():
    users = await User.query.gino.all()
    return users


async def count_users():
    count = await db.func.count(User.user_id).gino.scalar()
    return count


async def select_user(user_id: int):
    user = await User.query.where(User.user_id == user_id).gino.first()
    return user


async def update_info(user_id:int, old_field_name: string, new_field_name: string):
    user = await User.query.where(User.user_id == user_id).gino.first()
    print(user)
