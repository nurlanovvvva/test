from aiogram import Router, F, types
from config import database
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.command import Command

survey_router = Router()


class BookSurvey(StatesGroup):
    name = State()
    age = State()
    occupation = State()
    salary = State()

@survey_router.message(Command("opros"))
async def start_opros(message: types.Message, state: FSMContext):
    await state.set_state(BookSurvey.name)
    await message.answer("Вы можете остановить опрос в любой момент написав 'стоп'")
    await message.answer("Как Вас зовут?")


@survey_router.message(Command("stop"))
@survey_router.message(F.text.lower() == "стоп")
async def stop(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Спасибо за прохождение опроса!")


@survey_router.message(BookSurvey.name)
async def process_name(message: types.Message, state: FSMContext):
    print("Имя:", message.text)
    await state.update_data(name=message.text)
    await state.set_state(BookSurvey.age)
    await message.answer("Сколько Вам лет?")


@survey_router.message(BookSurvey.age)
async def process_age(message: types.Message, state: FSMContext):
    age = message.text
    if not age.isdigit():
        await message.answer("Вводите только цифры!")
        return
    age = int(age)
    if age < 17 or age > 90:
        await message.answer("Возраст должен быть от 17 до 90 лет!")
        return
    await state.update_data(age=age)
    await state.set_state(BookSurvey.occupation)
    await message.answer("Род занятий?")


@survey_router.message(BookSurvey.occupation)
async def process_gender(message: types.Message, state: FSMContext):
    await state.update_data(occupation=message.text)
    await state.set_state(BookSurvey.salary)
    await message.answer("Заработная плата?")


@survey_router.message(BookSurvey.salary)
async def process_genre(message: types.Message, state: FSMContext):
    await state.update_data(salary=message.text)
    data = await state.get_data()
    print(data)
    # сохранение data в БД
    await database.execute("""
               INSERT INTO survey_results (name, age, occupation, salary) 
               VALUES (?, ?, ?, ?)""",
                           (data['name'], data['age'], data['occupation'], data['salary'])
                           )

    await state.clear()
    await message.answer("Спасибо за пройденный опрос!")


