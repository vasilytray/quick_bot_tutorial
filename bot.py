import os
import asyncio
import logging
from datetime import datetime


from aiogram import Bot, Dispatcher, types
from aiogram.enums.dice_emoji import DiceEmoji
from aiogram import F, html
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.formatting import Text, Bold, as_list, as_marked_section, as_key_value, HashTag
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
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

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # await message.answer("Привет! ")
    content = as_list(
        Text(
            "Привет! ",
            Bold(message.from_user.first_name)
        ),
        as_marked_section(
            Bold("Я умею:"),
            "/test1  - Отвечу Test1",
            "/answer - Просто отвечу",
            "/reply  - Отвечу ответом",
            "/name   - Поприветствую тебя по Имени и Фамилии",
            "/aboute   - Дам тебе характеристику", 
            "/dice   - Подкину для тебя кубик, загадай число ;)",
            marker="✅ ",
        ),
        as_marked_section(
            Bold("Failed:"),
            "Не смогу назвать номер твоего телефона :( )",
            marker="❌ ",
        ),
        HashTag("#я"),
        # Text(
        #     "Номер телефона, ",
        #     Bold(message.contact.phone_number)
        # )
    )
    await message.answer(
        **content.as_kwargs()
    )

# Хэндлер на команду /test1
@dp.message(Command("test1"))
async def cmd_test1(message: types.Message):
    await message.reply("Test 1")

# Хэндлер на команду /test2
# Без декоратора, т.к. регистрируется ниже в функции main()
async def cmd_test2(message: types.Message):
    await message.reply("Test 2")


@dp.message(Command("answer"))
async def cmd_answer(message: types.Message):
    await message.answer("Это простой ответ")

# Хэндлер на команду /name

@dp.message(Command("name"))
async def cmd_name(message: Message):
    await message.answer(
        f"Доброго дня тебе, <b>{html.bold(html.quote(message.from_user.full_name))}</b>",
        parse_mode=ParseMode.HTML
        # f"Мой ник, <b>{html.bold(html.quote(message.from_user.username))}</b>",
        # parse_mode=ParseMode.HTML
    )

@dp.message(Command("aboute"))
async def cmd_aboute(message: Message):
    content = as_list(
        Text(
            "User_name, ",
            Bold(message.from_user.username)
        ),
        as_marked_section(
            Bold("Это Ты:"),
            "Молодец",
            "Красава",
            "Умка",
            marker="✅ ",
        ),
        as_marked_section(
            Bold("Это точно не ты:"),
            "Душнила",
            marker="❌ ",
        ),
        HashTag("#характеристика"),
        # Text(
        #     "Номер телефона, ",
        #     Bold(message.contact.phone_number)
        # )
    )
    await message.answer(
        **content.as_kwargs()
    )

@dp.message(Command("reply"))
async def cmd_reply(message: types.Message):
    await message.reply('Это ответ с "ответом"')


@dp.message(Command("dice"))
async def cmd_dice(message: types.Message):
    await message.answer_dice(emoji=DiceEmoji.DICE)

# передача сообщения в другой чат с номером чата -1001826767638
@dp.message(Command("dice2"))
async def cmd_dice2(message: types.Message, bot: Bot):
    await bot.send_dice(-1001826767638, emoji=DiceEmoji.DICE)

# запрос даты запуска бота
@dp.message(Command("info"))
async def cmd_info(message: types.Message, started_at: str):
    await message.answer(f"Бот запущен {started_at}")

# Запуск процесса поллинга новых апдейтов
async def main():
    # Регистрируем хэндлер cmd_test2 по команде /start
    dp.message.register(cmd_test2, Command("test2"))
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())