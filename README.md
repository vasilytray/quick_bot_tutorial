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

