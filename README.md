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