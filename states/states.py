from aiogram.dispatcher.filters.state import State, StatesGroup


# Состояния для регистрации пользователя
class FSMClientRegistration(StatesGroup):
    client_name = State()
    client_gender = State()
    client_birth_date = State()
    client_birth_place = State()
    client_birth_time = State()
    client_birth_time_set = State()
    client_send_date = State()
    client_agree = State()
    client_decline = State()
    client_change_info = State()
    client_what_to_change = State()
    client_daytime_change = State()
    schedule = State()


