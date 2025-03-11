import os
import asyncio
import logging
from datetime import datetime


from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.enums.dice_emoji import DiceEmoji
from aiogram import F, html
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from aiogram.utils.formatting import Text, Bold, as_list, as_marked_section, as_key_value, HashTag
from aiogram.types import FSInputFile, URLInputFile, BufferedInputFile
# новый импорт!
from aiogram.utils.markdown import hide_link #для скрытой ссылки


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
            "Если ты мне отправишь гифку, я тебе ей же и отвечу",
            "----------",
            "/more   - Еще больше возможностей!",

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

@dp.message(Command("more"))
async def cmd_more(message: types.Message):
    # await message.answer("Привет! ")
    content = as_list(
        Text(
            
            Bold(message.from_user.first_name),
            "  Еще я могу вот что: ",
        ),
        as_marked_section(
            Bold(""),
            "Если ты напишешь в тексте ",
            "адрес сайта,",
            "e-mail,",
            "Номер телефона,",
            "Я распознаю их и напишу что нашел", 
            "/dice   - Подкину для тебя кубик, загадай число ;)",
            "/settimer <time> <message> - через установленное время сообще Message ;)", 
            "/hidden_link   - Подкину для тебя угарную фотку ;)",
            marker="✅ ",
        ),
        HashTag("#еще"),
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

# сохраним формат введенного пользователем текста - после теста отключим хендлер
#@dp.message(F.text)
async def echo_with_time(message: Message):
    # Получаем текущее время в часовом поясе ПК
    time_now = datetime.now().strftime('%H:%M')
    # Создаём подчёркнутый текст
    added_text = html.underline(f"Написано в {time_now}")
    not_anderstand = (message.from_user.first_name)
    # Отправляем новое сообщение с добавленным текстом
    await message.answer(f"{message.html_text}\n\n{not_anderstand}!!! Я не понимаю эту команду :(\nДля получения списка известных мне команд напиши /start \n{added_text}", parse_mode="HTML")

# Извлекаем из сообщений пользователя данные url, email, телефон и код
#@dp.message(F.text)
async def extract_data(message: Message):
    data = {
        "url": "<N/A>",
        "email": "<N/A>",
        "phone_number": "<N/A>",
        # "code": "<N/A>"
    }
    entities = message.entities or []
    for item in entities:
        if item.type in data.keys():
            # Неправильно
            # data[item.type] = message.text[item.offset : item.offset+item.length]
            # Правильно
            data[item.type] = item.extract_from(message.text)
    await message.reply(
        "Вот что я нашёл:\n"
        f"URL: {html.quote(data['url'])}\n"
        f"E-mail: {html.quote(data['email'])}\n"
        f"Телефон: {html.quote(data['phone_number'])}\n"
        # f"Пароль: {html.quote(data['code'])}"
    )

@dp.message(Command("settimer", prefix="/!")) # добавим дополнительные префиксы для  оперделения команды
async def cmd_settimer(
        message: Message,
        command: CommandObject
):
    # Если не переданы никакие аргументы, то
    # command.args будет None
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
        return
    # Пробуем разделить аргументы на две части по первому встречному пробелу
    try:
        delay_time, text_to_send = command.args.split(" ", maxsplit=1)
    # Если получилось меньше двух частей, вылетит ValueError
    except ValueError:
        await message.answer(
            "Ошибка: неправильный формат команды. Пример:\n"
            "/settimer <time> <message>"
        )
        return
    await message.answer(
        "Таймер добавлен!\n"
        f"Время: {delay_time}\n"
        f"Текст: {text_to_send}"
    )

# Мгновенный ответ пользователю гифкой, которую он прислал
@dp.message(F.animation)
async def echo_gif(message: Message):
    await message.reply_animation(message.animation.file_id)
    
    # await message.answer_animation(message.file_id)
    await message.answer_animation(
        animation=message.animation.file_id,
        caption="Я сегодня:",
        show_caption_above_media=True
    )

@dp.message(Command('images'))
async def upload_photo(message: Message):
    # Сюда будем помещать file_id отправленных файлов, чтобы потом ими воспользоваться
    file_ids = []

    # Чтобы продемонстрировать BufferedInputFile, воспользуемся "классическим"
    # открытием файла через `open()`. Но, вообще говоря, этот способ
    # лучше всего подходит для отправки байтов из оперативной памяти
    # после проведения каких-либо манипуляций, например, редактированием через Pillow
    with open("buffer_emulation.jpg", "rb") as image_from_buffer:
        result = await message.answer_photo(
            BufferedInputFile(
                image_from_buffer.read(),
                filename="image from buffer.jpg"
            ),
            caption="Изображение из буфера"
        )
        file_ids.append(result.photo[-1].file_id)

    # Отправка файла из файловой системы
    image_from_pc = FSInputFile("image_from_pc.jpg")
    result = await message.answer_photo(
        image_from_pc,
        caption="Изображение из файла на компьютере"
    )
    file_ids.append(result.photo[-1].file_id)

    # Отправка файла по ссылке
    image_from_url = URLInputFile("https://picsum.photos/seed/groosha/400/300")
    result = await message.answer_photo(
        image_from_url,
        caption="Изображение по ссылке"
    )
    file_ids.append(result.photo[-1].file_id)
    await message.answer("Отправленные файлы:\n"+"\n".join(file_ids))

# отправка приветственного сообщения вошедшему
@dp.message(F.new_chat_members)
async def somebody_added(message: Message):
    for user in message.new_chat_members:
        # проперти full_name берёт сразу имя И фамилию 
        # (на скриншоте выше у юзеров нет фамилии)
        await message.reply(f"Привет, {user.full_name}")

# Прячем ссылку в HTML
@dp.message(Command("hidden_link"))
async def cmd_hidden_link(message: Message):
    await message.answer(
        f"{hide_link('https://i.pinimg.com/736x/26/3b/80/263b80dab1464429dd3f082a6601ad76.jpg')}"
        f"Документация Telegram: *существует*\n"
        f"Пользователи: *не читают документацию*\n"
        f"Груша:"
    )

# пока не работает, надо понять как получить file_id
@dp.message(Command("gif"))
async def send_gif(message: Message):
    await message.answer_animation(
        animation="<file_id>",
        caption="Я сегодня:",
        show_caption_above_media=True
    )

# Запуск процесса поллинга новых апдейтов
async def main():
    # Регистрируем хэндлер cmd_test2 по команде /start
    dp.message.register(cmd_test2, Command("test2"))
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())