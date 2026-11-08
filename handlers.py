
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

# Хранилище пользователей
users_data = {}


# Состояния регистрации
class Registration(StatesGroup):
    name = State()
    age = State()
    confirmation = State()


# Команда /register
@router.message(Command("register"))
async def register(message: Message, state: FSMContext):
    await state.set_state(Registration.name)
    await message.answer("Привет! Давай зарегистрируемся. Как тебя зовут?")



# Получение имени
@router.message(Registration.name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Registration.age)
    await message.answer("Отлично! Теперь введи свой возраст:")



# Получение возраста
@router.message(Registration.age)
async def get_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введи возраст цифрами.")
        return

    age = int(message.text)

    if age < 1 or age > 120:
        await message.answer("Введи корректный возраст от 1 до 120.")
        return

    await state.update_data(age=age)
    data = await state.get_data()

    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить", callback_data="confirm")
    builder.button(text="❌ Отменить", callback_data="cancel")
    builder.adjust(2)

    await state.set_state(Registration.confirmation)

    await message.answer(
        f"Проверь свои данные:\n\n"
        f"Имя: {data['name']}\n"
        f"Возраст: {data['age']}",
        reply_markup=builder.as_markup()
    )




# Подтверждение регистрации
@router.callback_query(F.data == "confirm")
async def confirm_registration(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    user_id = callback.from_user.id

    users_data[user_id] = {
        "name": data["name"],
        "age": data["age"]
    }

    await callback.message.edit_text(
        "✅ Регистрация успешно завершена!"
    )

    await callback.answer()
    await state.clear()


# Отмена регистрации
@router.callback_query(F.data == "cancel")
async def cancel_registration(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Регистрация отменена.")
    await callback.answer()
    await state.clear()



# Просмотр профиля
@router.message(Command("profile"))
async def show_profile(message: Message):
    user_id = message.from_user.id

    if user_id not in users_data:
        await message.answer(
            "У тебя ещё нет профиля. Сначала пройди регистрацию: /register"
        )
        return

    user = users_data[user_id]

    await message.answer(
        f"👤 Твой профиль:\n\n"
        f"Имя: {user['name']}\n"
        f"Возраст: {user['age']}"
    )
