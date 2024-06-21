from aiogram.fsm.state import StatesGroup, State


class RunForm(StatesGroup):
    track = State()
    run_date = State()
    distance = State()
    run_time = State()
    description = State()
    sneakers = State()
    check_state = State()


class SneakersForm(StatesGroup):
    brand = State()
    model = State()
    photo = State()
    distance = State()
    description = State()
    check_state = State()

