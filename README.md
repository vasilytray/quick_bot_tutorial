# Туториал по tg_bot и aiogram-3
[Все проводится по гайду](https://mastergroosha.github.io/aiogram-3-guide/)

## Установка виртуального окружения venv и версионности git
инициализируем git
```
git init
```
установим виртуальную среду **venv** в  папку **venv**
```sh
python -m venv venv
```
запишем в файл зависимостей первую запись для установки **aiogram**
```sh
echo "aiogram<4.0" > requirements.txt
```
добавим туда же **pydantic-settings**
```sh
echo "pydantic-settings" >> requirements.txt
```
активируем виртуальную среду
```sh
source venv/bin/activate
```
для выхода из **venv** можно использовать:
```sh
deactivate
```
Добавим файл .gitignore и файл с секретами .env (.env - укажем в .gitignore)

```sh
# Игнорирование виртуальной среды Python
venv/
.venv/
myenv/

#Игнорирование рабочих каталогов
bin/
include/
lib/
lib64/

# Игнорирование файлов с окружением
.env
.gitignore
pyvenv.cfg


# Игнорирование скомпилированных файлов Python
__pycache__/
**/__pycache__/

```

Установим наконец наши зависимости

```sh
pip install -r requirements.txt 
```

## Первый бот

```py
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token="12345678:AaBbCcDdEeFfGgHh")
# Диспетчер
dp = Dispatcher()

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello!")

# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
```
### Создадим файл конфигурации и переопределим файл секретов в него

Итак, создадим рядом с **bot.py** отдельный файл **config_reader.py** о следующим содержимым

config_reader.py
```py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    # Желательно вместо str использовать SecretStr 
    # для конфиденциальных данных, например, токена бота
    bot_token: SecretStr

    # Начиная со второй версии pydantic, настройки класса настроек задаются
    # через model_config
    # В данном случае будет использоваться файла .env, который будет прочитан
    # с кодировкой UTF-8
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


# При импорте файла сразу создастся 
# и провалидируется объект конфига, 
# который можно далее импортировать из разных мест
config = Settings()
```
Теперь немного отредактируем наш bot.py:


```py bot.py
# импорты
from config_reader import config

# Для записей с типом Secret* необходимо 
# вызывать метод get_secret_value(), 
# чтобы получить настоящее содержимое вместо '*******'
bot = Bot(token=config.bot_token.get_secret_value())
```

## Работа с сообщениями

Разберёмся, как применять различные типы форматирования к сообщениям и работать с медиафайлами.

### ТЕКСТ

В распоряжении у разработчика имеется три способа разметки текста: HTML, Markdown и MarkdownV2.
Наиболее продвинутыми из них считаются HTML и MarkdownV2

> Часто требуется получить id user-а (user_id), получить его можно так:
```py
user_id = message.from_user.id
```

#### Форматированный вывод
За выбор форматирования при отправке сообщений отвечает аргумент ``parse_mode``, например:

```py
from aiogram import F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode

# Если не указать фильтр F.text, 
# то хэндлер сработает даже на картинку с подписью /test
@dp.message(F.text, Command("test"))
async def any_message(message: Message):
    await message.answer(
        "Hello, <b>world</b>!", 
        parse_mode=ParseMode.HTML
    )
    await message.answer(
        "Hello, *world*\!", 
        parse_mode=ParseMode.MARKDOWN_V2
    )
```

В aiogram можно задать параметры бота по умолчанию. Для этого создайте объект DefaultBotProperties и передайте туда нужные настройки:

```py
from aiogram.client.default import DefaultBotProperties

bot = Bot(
    token=config.bot_token.get_secret_value(),
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
        # тут ещё много других интересных настроек
    )
)

# где-то в функции...
await message.answer("Сообщение с <u>HTML-разметкой</u>")
# чтобы явно отключить форматирование в конкретном запросе, 
# передайте parse_mode=None
await message.answer(
    "Сообщение без <s>какой-либо разметки</s>", 
    parse_mode=None
)
```

#### Экранирование ввода

Второе чуть сложнее, но более продвинутое: воспользоваться специальным инструментом, 
который будет собирать отдельно текст и отдельно информацию о том, какие его куски должны быть отформатированы.

```py
from aiogram.filters import Command
from aiogram.utils.formatting import Text, Bold

@dp.message(Command("hello"))
async def cmd_hello(message: Message):
    content = Text(
        "Hello, ",
        Bold(message.from_user.full_name)
    )
    await message.answer(
        **content.as_kwargs()
    )
```

В примере выше конструкция ****content.as_kwargs()** вернёт аргументы **text, entities, parse_mode** и подставит их в вызов **answer()**

Упомянутый инструмент форматирования довольно комплексный, [официальная документация](https://core.telegram.org/bots/api#formatting-options) демонстрирует удобное отображение сложных конструкций

#### Сохранение форматирования
Представим, что бот должен получить форматированный текст от пользователя и добавить туда что-то своё, например, отметку времени. 

Напишем простой код:
```py
# новый импорт!
from datetime import datetime

@dp.message(F.text)
async def echo_with_time(message: Message):
    # Получаем текущее время в часовом поясе ПК
    time_now = datetime.now().strftime('%H:%M')
    # Создаём подчёркнутый текст
    added_text = html.underline(f"Создано в {time_now}")
    # Отправляем новое сообщение с добавленным текстом
    await message.answer(f"{message.text}\n\n{added_text}", parse_mode="HTML")
```

НО!  ``message.text`` возвращает просто текст, без каких-либо оформлений. 
Чтобы получить текст в нужном форматировании, воспользуемся альтернативными свойствами: ``message.html_text`` или ``message.md_text``.

#### Работа с entities
**Telegram** сильно упрощает жизнь разработчикам, выполняя предобработку сообщений пользователей на своей стороне. Например, некоторые сущности, типа **e-mail**, **номера телефона, юзернейма** и др. можно не доставать регулярными выражениями, а извлечь напрямую из объекта **Message** и поля **entities**, содержащего массив объектов типа [MessageEntity](https://core.telegram.org/bots/api#messageentity).

Здесь кроется важный подвох. *Telegram возвращает не сами значения, а их начало в тексте и длину*. 
```py
@dp.message(F.text)
async def extract_data(message: Message):
    data = {
        "url": "<N/A>",
        "email": "<N/A>",
        "code": "<N/A>"
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
        f"Пароль: {html.quote(data['code'])}"
    )
```

#### Команды и их аргументы

В составе aiogram есть фильтр Command(), упрощающий жизнь разработчика. 

Реализуем последний пример в коде:

```py
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
```

Проблема кастомных префиксов в группах только в том, что боты не-админы со включенным Privacy Mode (по умолчанию) могут не увидеть такие команды из-за особенностей логики сервера. 
Самый частый use-case — боты-модераторы групп, которые уже являются администраторами.


#### Диплинки
Существует одна команда в **Telegram**, у которой есть чуть больше возможностей. Это **/start**. Дело в том, что можно сформировать ссылку вида t.me/bot?start=xxx и пре переходе по такой ссылке пользователю покажут кнопку «Начать», при нажатии которой бот получит сообщение **/start xxx**.

Учтите, что диплинки через start отправляют пользователя в личку с ботом. Чтобы выбрать группу и отправить диплинк туда, замените start на startgroup. Также у aiogram существует удобная функция для создания диплинков прямо из вашего кода.

Первый дииплинк https://t.me/your_bot?start=help выведет сообщение, соответсвующее команде /help

Второй диплиинк https://t.me/your_bot?start=book_2 выведет соответствующее 
сообщение, полученное из регулярного выражения

```
Sending book №2
```

*Больше диплинков, но не для ботов:*

В документации **Telegram** есть подробное описание всевозможных диплинков для клиентских приложений: https://core.telegram.org/api/links

#### Предпросмотр ссылок
Обычно при отправке текстового сообщения со ссылками **Telegram** пытается найти и показать предпросмотр первой по порядку ссылки. Это поведение можно настроить по своему желанию, передав в качестве аргумента **link_preview_options** метода **send_message()** объект L**inkPreviewOptions**

```py
# Новый импорт
from aiogram.types import LinkPreviewOptions

@dp.message(Command("links"))
async def cmd_links(message: Message):
    links_text = (
        "https://nplus1.ru/news/2024/05/23/voyager-1-science-data"
        "\n"
        "https://t.me/telegram"
    )
    # Ссылка отключена
    options_1 = LinkPreviewOptions(is_disabled=True)
    await message.answer(
        f"Нет превью ссылок\n{links_text}",
        link_preview_options=options_1
    )

    # -------------------- #

    # Маленькое превью
    # Для использования prefer_small_media обязательно указывать ещё и url
    options_2 = LinkPreviewOptions(
        url="https://nplus1.ru/news/2024/05/23/voyager-1-science-data",
        prefer_small_media=True
    )
    await message.answer(
        f"Маленькое превью\n{links_text}",
        link_preview_options=options_2
    )

    # -------------------- #

    # Большое превью
    # Для использования prefer_large_media обязательно указывать ещё и url
    options_3 = LinkPreviewOptions(
        url="https://nplus1.ru/news/2024/05/23/voyager-1-science-data",
        prefer_large_media=True
    )
    await message.answer(
        f"Большое превью\n{links_text}",
        link_preview_options=options_3
    )

    # -------------------- #

    # Можно сочетать: маленькое превью и расположение над текстом
    options_4 = LinkPreviewOptions(
        url="https://nplus1.ru/news/2024/05/23/voyager-1-science-data",
        prefer_small_media=True,
        show_above_text=True
    )
    await message.answer(
        f"Маленькое превью над текстом\n{links_text}",
        link_preview_options=options_4
    )

    # -------------------- #

    # Можно выбрать, какая ссылка будет использоваться для предпосмотра,
    options_5 = LinkPreviewOptions(
        url="https://t.me/telegram"
    )
    await message.answer(
        f"Предпросмотр не первой ссылки\n{links_text}",
        link_preview_options=options_5
    )
```
Также некоторые параметры предпросмотра можно указать по умолчанию в DefaultBotProperties

### Медиафайлы

#### Отправка файлов

У большинства медиафайлов есть свойства ``file_id`` и ``file_unique_id``. Первый можно использовать для повторной отправки одного и того же файла много раз, причём отправка будет мгновенной, т.к. сам файл уже лежит на серверах **Telegram**

#### Скачивание файлов

бот может скачать медиа к себе на компьютер/сервер. Для этого у объекта типа Bot есть метод download()

```py
@dp.message(F.photo)
async def download_photo(message: Message, bot: Bot):
    await bot.download(
        message.photo[-1],
        destination=f"/tmp/{message.photo[-1].file_id}.jpg"
    )


@dp.message(F.sticker)
async def download_sticker(message: Message, bot: Bot):
    await bot.download(
        message.sticker,
        # для Windows пути надо подправить
        destination=f"/tmp/{message.sticker.file_id}.webp"
    )
```
#### Альбомы

Начиная с версии 3.1, в [aiogram есть «сборщик» альбомов,](https://docs.aiogram.dev/en/latest/utils/media_group.html)

### Сервисные (служебные) сообщения

Сообщения в Telegram делятся на текстовые, медиафайлы и служебные (они же — сервисные). Настало время поговорить о последних.

У такого служебного сообщения будет content_type равный "**new_chat_members**", но вообще это объект Message, у которого заполнено одноимённое поле.
```py
@dp.message(F.new_chat_members)
async def somebody_added(message: Message):
    for user in message.new_chat_members:
        # проперти full_name берёт сразу имя И фамилию 
        # (на скриншоте выше у юзеров нет фамилии)
        await message.reply(f"Привет, {user.full_name}")

```

## Кнопки

### Обычные кнопки
Это то, что выводится внизу экрана

#### Кнопки как шаблоны

Напишем хэндлер, который будет при нажатии на команду /start отправлять сообщение с двумя кнопками в bot2.py.

С точки зрения Bot API, клавиатура — это массив массивов кнопок, а если говорить проще, массив рядов.:

```py
@dp.message(Command("start"))
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
```

Осталось научить бота реагировать на нажатие таких кнопок. Как уже было сказано выше, 
необходимо делать проверку на полное совпадение текста. 

Сделаем это при помощи магического *фильтра F*

```py
@dp.message(F.text.lower() == "с пюрешкой")
async def with_puree(message: types.Message):
    await message.reply("Отличный выбор!", reply_markup=types.ReplyKeyboardRemove()) #удалим клавиатуру после ответа
```
#### Keyboard Builder

Сборщик клавиатур для генерации кнопок.

Нам пригодятся следующие методы:

``add(<KeyboardButton>)`` — добавляет кнопку в память сборщика;
``adjust(int1, int2, int3...)`` — делает строки по int1, int2, int3... кнопок;
``as_markup()`` — возвращает готовый объект клавиатуры;
``button(<params>)`` — добавляет кнопку с заданными параметрами, тип кнопки (Reply или Inline) определяется автоматически.

Создадим пронумерованную клавиатуру размером 4×4:
```py
# новый импорт!
from aiogram.utils.keyboard import ReplyKeyboardBuilder

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
```

#### Специальные обычные кнопки¶
На момент написания этой главы в Telegram существует шесть специальных видов обычных кнопок, не являющихся обычными шаблонами сообщений. Они предназначены для:

отправки текущей геолокации;
отправки своего контакта с номером телефона;
создания опроса/викторины;
выбора и отправки боту данных пользователя с нужными критериями;
выбора и отправки боту данных (супер)группы или канала с нужными критериями;
запуска веб-приложения (WebApp).
Поговорим про них подробнее.

**Отправка текущей геолокации.** Здесь всё просто: где пользователь находится, те координаты и отправляет. Это будет статическое гео, а не Live Location, который обновляется автоматически. Разумеется, хитрые юзеры могут подменить своё местонахождение, иногда даже на уровне всей системы (Android).

**Отправка своего контакта с номером телефона.** При нажатии на кнопку (с предварительным подтверждением) пользователь отправляет свой контакт с номером телефона боту. Те же хитрые юзеры могут проигнорировать кнопку и отправить любой контакт, но в этом случае на них можно найти управу: достаточно проверить в хэндлере или в фильтре равенство message.``contact.user_id == message.from_user.id``.

**Создание опроса/викторины.** По нажатию на кнопку пользователю предлагается создать опрос или викторину, которые потом отправятся в текущий чат. Необходимо передать объект KeyboardButtonPollType, необязательный аргумент type служит для уточнения типа опроса (опрос или викторина).

**Выбор и отправка боту данных пользователя с нужными критериями.** Показывает окно выбора пользователя из списка чатов юзера, нажавшего на кнопку. Необходимо передать объект KeyboardButtonRequestUser, в котором надо указать сгенерированный любым способом айди запроса и критерии, например, "бот", "есть подписка Telegram Premium" и т.д. После выбора юзера бот получит сервисное сообщение с типом **UserShared**.

**Выбор и отправка боту чата с нужными критериями.** Показывает окно выбора пользователя из списка чатов юзера, нажавшего на кнопку. Необходимо передать объект KeyboardButtonRequestChat, в котором надо указать сгенерированный любым способом айди запроса и критерии, например, "группа или канал", "юзер — создатель чата" и т.д. После выбора юзера бот получит сервисное сообщение с типом ChatShared.

**Запуск веб-приложения (WebApp)**. При нажатии на кнопку открывает WebApp. Необходимо передать объект WebAppInfo. В этой книге веб-аппы пока рассматриваться не будут.

две заготовки хэндлеров на приём нажатий от нижних двух кнопок:
```py
# новый импорт
from aiogram import F

@dp.message(F.user_shared)
async def on_user_shared(message: types.Message):
    print(
        f"Request {message.user_shared.request_id}. "
        f"User ID: {message.user_shared.user_id}"
    )


@dp.message(F.chat_shared)
async def on_user_shared(message: types.Message):
    print(
        f"Request {message.chat_shared.request_id}. "
        f"User ID: {message.chat_shared.chat_id}"
    )
```

### Инлайн-кнопки

В отличие от обычных кнопок, инлайновые цепляются не к низу экрана, а к сообщению, с которым были отправлены. В этой главе мы рассмотрим два типа таких кнопок: **URL** и **Callback**.

#### URL-кнопки

Самые простые инлайн-кнопки относятся к типу URL, т.е. «ссылка». Поддерживаются только протоколы **HTTP(S)** и **tg://**

При попытке создать URL-кнопку с ID юзера, у которого отключен переход по форварду, бот получит ошибку **Bad Request: BUTTON_USER_PRIVACY_RESTRICTED**. Соответственно, прежде чем показывать такую кнопку, необходимо выяснить состояние упомянутой настройки. Для этого можно вызвать метод **getChat** и в ответе проверить состояние поля **has_private_forwards**. Если оно равно **True**, значит, попытка добавить **URL-ID** кнопку приведёт к ошибке.

#### Callback-кнопки

У колбэк-кнопок есть специальное значение **(data)**, по которому ваше приложение опознаёт, что нажато и что надо сделать. И выбор правильного data очень важен! Стоит также отметить, что, в отличие от обычных кнопок, нажатие на колбэк-кнопку позволяет сделать практически что угодно, от заказа пиццы до запуска вычислений на кластере суперкомпьютеров.

Сервер Telegram  отправив нам кнопку callback ждет от нас подтверждения о доставке колбэка. Нам необходимо вызвать метод **answer()**  в общем случае в него можем ничего не передавать, но можно вызвать специальное окошко (всплывающее сверху или поверх экрана):

```py
@dp.callback_query(F.data == "random_value")
async def send_random_value(callback: types.CallbackQuery):
    await callback.message.answer(str(randint(1, 10)))
    await callback.answer(
        text="Спасибо, что воспользовались ботом!",
        show_alert=True
    )
    # или просто await callback.answer()
```
> В функции send_random_value мы вызывали метод answer() не у message, а у callback.message. Это связано с тем, что колбэк-хэндлеры работают не с сообщениями (тип Message), а с колбэками (тип CallbackQuery), у которого другие поля, и само сообщение — всего лишь его часть. Учтите также, что message — это сообщение, к которому была прицеплена кнопка (т.е. отправитель такого сообщения — сам бот). Если хотите узнать, кто нажал на кнопку, смотрите поле from (в вашем коде это будет callback.from_user, т.к. слово from зарезервировано в Python)

Иногда пользователь, вызвав несколько раз сообщение с колбэками, может нажимать кнопки новых и старых сообщений и тогда может возникнуть ошибка, которую мы получим от Bot API, что старый и новый тексты совпадают, а бот словит исключение: ``Bad Request: message is not modified: specified new message content and reply markup are exactly the same as a current content and reply markup of the message.

Ошибка MessageNotModified относится к категории Bad Request, поэтому у нас есть выбор: проигнорировать весь подобный класс ошибок, либо отловить весь класс BadRequest и попытаться по тексту ошибки опознать конкретную причину. 

Чтобы игнорировать весь подобный  класс обновим функцию ``update_num_text()``

```py
# Новые импорты!
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest

async def update_num_text(message: types.Message, new_value: int):
    with suppress(TelegramBadRequest):
        await message.edit_text(
            f"Укажите число: {new_value}",
            reply_markup=get_keyboard()
        )
```
