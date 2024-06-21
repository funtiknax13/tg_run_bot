import asyncio
import datetime

from aiogram.types import CallbackQuery

from forms import RunForm, SneakersForm
from db import DBmanager
from config import config
from keyboards import miss_field, check_data

from aiogram.filters import Command, StateFilter

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode

import os
from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(storage=MemoryStorage())

db_connect = DBmanager(os.getenv('DB_NAME'), config())


@dp.message(StateFilter(None), Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет, этот бот поможет тебе анализировать и систематизировать твои пробежки.\n"
                         "Используй команды /add - для добавления пробежки и /run - вывод всех пробежек",
                         parse_mode=ParseMode.HTML)


@dp.message(StateFilter(None), Command("add"))
async def cmd_add_run(message: types.Message, state: FSMContext):
    await message.answer("Загрузи изображение трека\n",
                         parse_mode=ParseMode.HTML)
    await state.set_state(RunForm.track)


@dp.message(F.photo, RunForm.track)
async def process_run_form(message: types.Message, state: FSMContext):
    photo_data = message.photo[-1]
    await state.update_data(track=photo_data.file_id)
    await state.set_state(RunForm.run_date)
    await message.answer("Введите дату старта пробежки в формате ДД.ММ.ГГГГ",
                         parse_mode=ParseMode.HTML)


@dp.message(RunForm.run_date)
async def process_run_form(message: types.Message, state: FSMContext):
    await state.update_data(run_date=datetime.datetime.strptime(message.text, '%d.%m.%Y').date())
    await state.set_state(RunForm.distance)
    await message.answer("Введите дистанцию (для дробных чисел используйте точку. Например: 21.195)",
                         parse_mode=ParseMode.HTML)


@dp.message(RunForm.distance)
async def process_run_form(message: types.Message, state: FSMContext):
    await state.update_data(distance=float(message.text))
    await state.set_state(RunForm.run_time)
    await message.answer("Введите время в формате ЧЧ:ММ:СС",
                         parse_mode=ParseMode.HTML)


@dp.message(RunForm.run_time)
async def process_run_form(message: types.Message, state: FSMContext):
    try:
        run_time = datetime.datetime.strptime(message.text, '%H:%M:%S').time()
        await state.update_data(run_time=run_time)
        await state.set_state(RunForm.description)
        await message.answer("Добавь описание",
                             parse_mode=ParseMode.HTML)
    except Exception as e:
        print(e)
        await state.set_state(RunForm.run_time)
        await message.answer("Неверный формат. Введите время в формате ЧЧ:ММ:СС",
                             parse_mode=ParseMode.HTML)


@dp.message(RunForm.description)
async def process_run_form(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(RunForm.sneakers)
    await message.answer("Выбери кроссовки этой тренировки",
                         parse_mode=ParseMode.HTML)


@dp.message(RunForm.sneakers)
async def process_run_form(message: types.Message, state: FSMContext):
    await state.update_data(sneakers=int(message.text))
    run_data = await state.get_data()
    run_data["user_id"] = message.from_user.id
    run_data["create_date"] = datetime.datetime.now()
    run_data["is_moderate"] = False

    await db_connect.add_run(**run_data)
    await state.clear()
    await message.answer_photo(photo=run_data["track"],
                               caption=f'Пробежка на <b>{run_data["distance"]}</b> км сохранена.',
                               parse_mode=ParseMode.HTML)


@dp.message(StateFilter(None), Command("sadd"))
async def cmd_add_sneakers(message: types.Message, state: FSMContext):
    await message.answer("Введи брэнд кроссовок\n",
                         parse_mode=ParseMode.HTML)
    await state.set_state(SneakersForm.brand)


@dp.message(SneakersForm.brand)
async def process_sneakers_form(message: types.Message, state: FSMContext):
    await state.update_data(brand=message.text)
    await state.set_state(SneakersForm.model)
    await message.answer("Введи модель кроссовок",
                         parse_mode=ParseMode.HTML)


@dp.message(SneakersForm.model)
async def process_sneakers_form(message: types.Message, state: FSMContext):
    await state.update_data(model=message.text)
    await state.set_state(SneakersForm.photo)
    await message.answer("Загрузи фото кроссовок", reply_markup=miss_field(),
                         parse_mode=ParseMode.HTML)


@dp.callback_query(F.data, SneakersForm.photo)
async def process_sneakers_form(call: CallbackQuery, state: FSMContext):
    # await call.message.edit_reply_markup(reply_markup=None)
    await state.update_data(photo=None)
    await call.message.answer("Добавь описание", reply_markup=miss_field(),
                              parse_mode=ParseMode.HTML)
    await state.set_state(SneakersForm.description)


@dp.message(F.photo, SneakersForm.photo)
async def process_sneakers_form(message: types.Message, state: FSMContext):
    photo_data = message.photo[-1]
    await state.update_data(photo=photo_data.file_id)
    await state.set_state(SneakersForm.description)
    await message.answer("Добавь описание", reply_markup=miss_field(),
                         parse_mode=ParseMode.HTML)


@dp.callback_query(F.data, SneakersForm.description)
async def process_sneakers_form(call: CallbackQuery, state: FSMContext):
    # await call.message.edit_reply_markup(reply_markup=None)
    await state.update_data(description=None)
    await call.message.answer("Укажи пробег (если это дробное число, укажи через точку - 121.5)",
                              reply_markup=miss_field(),
                              parse_mode=ParseMode.HTML)
    await state.set_state(SneakersForm.distance)


@dp.message(F.text, SneakersForm.description)
async def process_sneakers_form(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(SneakersForm.distance)
    await message.answer("Укажи пробег (если это дробное число, укажи через точку - 121.5)",
                         reply_markup=miss_field(),
                         parse_mode=ParseMode.HTML)


@dp.callback_query(F.data, SneakersForm.distance)
async def process_sneakers_form(call: CallbackQuery, state: FSMContext):
    # await call.message.edit_reply_markup(reply_markup=None)
    await state.update_data(distance=0)
    sneakers_data = await state.get_data()
    caption = f'Пожалуйста, проверь все ли верно: \n\n' \
              f'<b>Брэнд</b>: {sneakers_data["brand"]}\n' \
              f'<b>Модель</b>: {sneakers_data["model"]}\n' \
              f'<b>Дистанция</b>: {sneakers_data["distance"]} км\n' \
              f'<b>Описание</b>: {sneakers_data["description"] if sneakers_data["description"] else '-'}\n'
    if sneakers_data["photo"]:
        await call.message.answer_photo(photo=sneakers_data["photo"],
                                        caption=caption,
                                        reply_markup=check_data(),
                                        parse_mode=ParseMode.HTML)
    else:
        await call.message.answer(text=caption, reply_markup=check_data(), parse_mode=ParseMode.HTML)
    await state.set_state(SneakersForm.check_state)


@dp.message(F.text, SneakersForm.distance)
async def process_sneakers_form(message: types.Message, state: FSMContext):
    try:
        await state.update_data(distance=float(message.text))
        sneakers_data = await state.get_data()
        caption = f'Пожалуйста, проверь все ли верно: \n\n' \
                  f'<b>Брэнд</b>: {sneakers_data["brand"]}\n' \
                  f'<b>Модель</b>: {sneakers_data["model"]}\n' \
                  f'<b>Дистанция</b>: {sneakers_data["distance"]} км\n' \
                  f'<b>Описание</b>: {sneakers_data["description"] if sneakers_data["description"] else '-'}\n'
        if sneakers_data["photo"]:
            await message.answer_photo(photo=sneakers_data["photo"],
                                       caption=caption,
                                       reply_markup=check_data(),
                                       parse_mode=ParseMode.HTML)
        else:
            await message.answer(text=caption, reply_markup=check_data(), parse_mode=ParseMode.HTML)
        await state.set_state(SneakersForm.check_state)
    except:
        await message.answer("Неверный формат. Укажи пробег, если это дробное число, укажи через точку - 121.5",
                             reply_markup=miss_field(),
                             parse_mode=ParseMode.HTML)
        await state.set_state(SneakersForm.distance)


@dp.callback_query(F.data == 'correct', SneakersForm.check_state)
async def process_sneakers_form(call: CallbackQuery, state: FSMContext):
    sneakers_data = await state.get_data()
    sneakers_data["create_date"] = datetime.datetime.now()
    sneakers_data["user_id"] = call.message.from_user.id
    await db_connect.add_sneakers(**sneakers_data)
    await state.clear()
    await call.message.answer(text=f'Кроссовки <b>{sneakers_data["brand"]} {sneakers_data["model"]}</b> сохранены.',
                              parse_mode=ParseMode.HTML)


@dp.callback_query(F.data == 'incorrect', SneakersForm.check_state)
async def process_sneakers_form(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer("Введи брэнд кроссовок\n",
                              parse_mode=ParseMode.HTML)
    await state.set_state(SneakersForm.brand)


@dp.message(StateFilter(None), Command("run"))
async def cmd_run_list(message: types.Message):
    data = await db_connect.get_run_list(message.from_user.id)
    run_list = ''
    for item in data:
        run_list += f'{item}\n'
        # run_list += f'{item[0]}: {item[2]}\nВремя создания:{item[3].strftime("%d-%m-%Y %H:%M")}\n\n'

    await message.answer("<b>Твои пробежки:</b>\n" + run_list,
                         parse_mode=ParseMode.HTML)


@dp.message(StateFilter(None))
async def unknown_commands(message: types.Message):
    await message.answer("Я не знаю такой команды, выбери /add - для добавления пробежки и /run - вывод всех пробежек",
                         parse_mode=ParseMode.HTML)


async def main():
    await db_connect.create_table()
    await dp.start_polling(bot)


asyncio.run(main())

