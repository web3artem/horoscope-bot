import datetime

from sqlalchemy import Column, BigInteger, DATE, TIME, VARCHAR, sql, Boolean, ForeignKey

from db.db_gino import TimedBaseModel, db


class User(TimedBaseModel):
    __tablename__ = 'users'
    user_id = Column(BigInteger, unique=True, nullable=False, primary_key=True)

    # Telegram username
    username = Column(VARCHAR(32), nullable=True)

    name = Column(VARCHAR(32))
    gender = Column(VARCHAR(7))
    birth_date = Column(DATE)
    birth_place = Column(VARCHAR(32))
    birth_time = Column(TIME, nullable=True)
    receive_day_period = Column(VARCHAR(32))

    query: sql.select


class Distribution(db.Model):
    __tablename__ = 'distribution'

    id = Column(BigInteger, ForeignKey('users.user_id'), nullable=False, unique=True)
    was_sent = Column(Boolean, nullable=False, default=False)


class MessageId(db.Model):
    __tablename__ = 'message'

    user_id = Column(BigInteger, unique=True, nullable=False, primary_key=True)
    message_id = Column(BigInteger)
