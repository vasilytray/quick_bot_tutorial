## Бот в контейнер для запуска на ВМ

### 1. Структура проекта

```py
mybot/
├── bot/
│   ├── __init__.py
│   └── main.py
├── .env                # Файл с переменными окружения
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .gitignore
```

### 2. .env файл

```py
BOT_TOKEN=ваш_токен_бота
```
### 3. docker-compose.yml

```yaml

version: '3.8'

services:
  bot:
    build: .
    env_file:
      - .env
    restart: unless-stopped
```

### 4. Обновленный Dockerfile

```dockerfile

FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "bot.main"]
```

### 5. Пример кода бота (bot/main.py)

```python

import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Чтение токена из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Бот запущен в Docker контейнере!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Инструкция по запуску

### Создайте файл .env в корне проекта:

```bash
echo "BOT_TOKEN=ваш_действительный_токен" > .env
Соберите и запустите контейнер:
```
```bash
docker-compose up --build -d
Проверьте работу бота:
```
```bash
docker-compose logs -f
```

### Важные изменения:

Убраны системные зависимости из Dockerfile (gcc и python3-dev не нужны для простых ботов)

Добавлен **env_file** в ``docker-compose.yml`` для автоматической загрузки переменных из **.env**

Упрощена структура **Dockerfile**

Добавлено автоматическое пересоздание контейнера при рестарте **(restart: unless-stopped)**

#### Для обновления бота:

Внесите изменения в код

#### Пересоберите контейнер:

```bash
docker-compose up --build -d
```

### Безопасность:

Никогда не коммитьте .env в git

Добавьте .env в .gitignore

Используйте разные .env файлы для разработки и продакшена

### Проверка работы:

```bash
# Проверить статус контейнера
docker-compose ps
```
```sh
# Посмотреть логи
docker-compose logs -f --tail=50
```
```sh
# Остановить контейнер
docker-compose down
```

### 8. Настройка виртуальной машины

Установите Docker:

```sh
# Для Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose -y
```

Скопируйте файлы проекта на VM:

```sh
scp -r mybot/ user@vm_ip:/path/to/project
```

Откройте доступ к портам (если нужно):

```sh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

Запустите контейнер на VM:

```sh
cd /path/to/project
docker-compose up -d --build
```

проверьте статус контейнера

```sh
docker ps
```