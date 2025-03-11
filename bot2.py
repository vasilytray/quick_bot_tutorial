import re
import asyncio
import logging
from datetime import datetime
from aiogram import F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
# новый импорт!
from aiogram.utils.keyboard import ReplyKeyboardBuilder


from config_reader import config

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Для записей с типом Secret* необходимо 
# вызывать метод get_secret_value(), 
# чтобы получить настоящее содержимое вместо '*******'
bot = Bot(
    token=config.bot_token.get_secret_value(),
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
        # тут ещё много других интересных настроек
    ))

# Объект бота напрямую из .env
# bot = Bot(token=os.getenv("BOT_TOKEN"))

# Диспетчер
dp = Dispatcher()
dp["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

# @dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = [
        [
            types.KeyboardButton(text="С пюрешкой"),
            types.KeyboardButton(text="Без пюрешки")
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите способ подачи"
    )
    await message.answer("Как подавать котлеты?", reply_markup=keyboard)

@dp.message(F.text.lower() == "с пюрешкой")
async def with_puree(message: types.Message):
    await message.reply("Отличный выбор!", reply_markup=types.ReplyKeyboardRemove()) #удалим клавиатуру после ответа

@dp.message(F.text.lower() == "без пюрешки")
async def without_puree(message: types.Message):
    await message.reply("Так невкусно!")


@dp.message(Command("reply_builder"))
async def reply_builder(message: types.Message):
    builder = ReplyKeyboardBuilder()
    for i in range(1, 17):
        builder.add(types.KeyboardButton(text=str(i)))
    builder.adjust(4)
    await message.answer(
        "Выберите число:",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )

@dp.message(F.text.lower() == "10")
async def with_puree(message: types.Message):
    await message.reply("Отличный выбор!", reply_markup=types.ReplyKeyboardRemove()) #удалим клавиатуру после ответа

@dp.message(Command("help"))
@dp.message(CommandStart(
    deep_link=True, magic=F.args == "help"
))
async def cmd_start_help(message: Message):
    await message.answer("Это сообщение со справкой")


@dp.message(CommandStart(
    deep_link=True,
    magic=F.args.regexp(re.compile(r'book_(\d+)'))
))
async def cmd_start_book(
        message: Message,
        command: CommandObject
):
    book_number = command.args.split("_")[1]
    await message.answer(f"Sending book №{book_number}")

@dp.message(Command("vfy"))
@dp.message(CommandStart(
    deep_link=True, magic=F.args == "vfy"
))
async def cmd_start_vfy(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(
            text="Подтвердить контакт",
            request_contact=True
        )
    )
    # Отправляем сообщение с клавиатурой
    await message.answer(
        "Для подтверждения номера телефона нажмите кнопку ниже:",
        reply_markup=builder.as_markup(
            resize_keyboard=True,  # Опционально: автоматический размер
            one_time_keyboard=True # Опционально: скрыть после нажатия
        )
    )

# Хэндлер для обработки полученного контакта
@dp.message(lambda message: message.contact is not None)
async def handle_contact(message: types.Message):
    # Проверяем, что контакт принадлежит отправителю
    if message.from_user.id == message.contact.user_id:
        await message.answer(
            f"Спасибо за контакт, {message.contact.first_name}!\n"
            f"Номер телефона: {message.contact.phone_number}",
            reply_markup=types.ReplyKeyboardRemove()  # Убираем клавиатуру
        )
    else:
        await message.answer("Это не ваш контакт!")

# новый импорт
from aiogram.utils.keyboard import InlineKeyboardBuilder

@dp.message(Command("inline_url"))
async def cmd_inline_url(message: types.Message, bot: Bot):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="GitHub", url="https://github.com")
    )
    builder.row(types.InlineKeyboardButton(
        text="Оф. канал Telegram",
        url="tg://resolve?domain=telegram")
    )

    # Чтобы иметь возможность показать ID-кнопку,
    # У юзера должен быть False флаг has_private_forwards
    user_id = message.from_user.id
    chat_info = await bot.get_chat(user_id)
    if not chat_info.has_private_forwards:
        builder.row(types.InlineKeyboardButton(
            text="Какой-то пользователь",
            url=f"tg://user?id={user_id}")
        )

    await message.answer(
        'Выберите ссылку',
        reply_markup=builder.as_markup(),
    )

    # Запуск процесса поллинга новых апдейтов
async def main():
    
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
