
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
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


# Команда /start
@router.message(CommandStart())
async def cmd_start(message: Message):
    name = message.from_user.first_name
    await message.answer(f"Привет, {name}!")


# Команда /help
@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "Доступные команды:\n\n"
        "/start — приветствие\n"
        "/help — список команд\n"
        "/register — регистрация\n"
        "/profile — просмотр профиля"
    )


# Команда /register
@router.message(Command("register"))
async def register(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Registration.name)
    await message.answer("Введите ваше имя:")


# Шаг 1: ввод имени
@router.message(Registration.name)
async def get_name(message: Message, state: FSMContext):
    if not message.text or not message.text.strip():
        await message.answer("Введите корректное имя:")
        return

    await state.update_data(name=message.text.strip())
    await state.set_state(Registration.age)
    await message.answer("Введите возраст:")


# Шаг 2: ввод возраста
@router.message(Registration.age)
async def get_age(message: Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        await message.answer(
            "Это не число! Пожалуйста, введите возраст цифрами:"
        )
        return

    age = int(message.text)

    if age <= 0:
        await message.answer(
            "Возраст должен быть больше нуля. Введите возраст:"
        )
        return

    await state.update_data(age=age)
    data = await state.get_data()

    builder = InlineKeyboardBuilder()
    builder.button(
        text="Подтвердить",
        callback_data="confirm_reg"
    )
    builder.button(
        text="Начать заново",
        callback_data="restart_reg"
    )
    builder.adjust(2)

    await state.set_state(Registration.confirmation)

    await message.answer(
        f"Проверьте свои данные:\n\n"
        f"Имя — {data['name']}\n"
        f"Возраст — {data['age']}",
        reply_markup=builder.as_markup()
    )


# Подтверждение регистрации
@router.callback_query(
    Registration.confirmation,
    F.data == "confirm_reg"
)
async def confirm_registration(
    callback: CallbackQuery,
    state: FSMContext
):
    data = await state.get_data()
    user_id = callback.from_user.id

    users_data[user_id] = {
        "name": data["name"],
        "age": data["age"]
    }

    await callback.message.edit_text(
        "Регистрация завершена!"
    )
    await callback.answer()
    await state.clear()


# Начать регистрацию заново
@router.callback_query(
    Registration.confirmation,
    F.data == "restart_reg"
)
async def restart_registration(
    callback: CallbackQuery,
    state: FSMContext
):
    await state.clear()
    await state.set_state(Registration.name)

    await callback.message.edit_text(
        "Начнем заново. Шаг 1: Введите ваше имя:"
    )
    await callback.answer()


# Команда /profile
@router.message(Command("profile"))
async def show_profile(message: Message):
    user_id = message.from_user.id

    if user_id not in users_data:
        await message.answer(
            "Вы не зарегистрированы. "
            "Напишите /register, чтобы пройти регистрацию"
        )
        return

    user = users_data[user_id]

    await message.answer(
        f"Ваши данные:\n"
        f"Имя — {user['name']}\n"
        f"Возраст — {user['age']}"
    )
