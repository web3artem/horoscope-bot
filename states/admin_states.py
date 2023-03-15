from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMAdmin(StatesGroup):
    AdminPhoto = State()
    AdminPhotoLoading = State()
    AdminDesc = State()
    AdminSummarize = State()
    AdminChange = State()
    AdminChangePhoto = State()
    AdminChangeDesc = State()