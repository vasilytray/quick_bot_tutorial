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
```
Соберите и запустите контейнер:

```bash
docker-compose up --build -d
```
Проверьте работу бота:
```bash
docker-compose logs -f
```

### Важные изменения:

Убраны системные зависимости из Dockerfile (gcc и python3-dev не нужны для простых ботов)

Добавлен **env_file** в ``docker-compose.yml`` для автоматической загрузки переменных из **.env**

Упрощена структура **Dockerfile**

Добавлено автоматическое пересоздание контейнера при рестарте **(restart: unless-stopped)**

#### Для обновления бота:

Внесите изменения в код или подтяните из GitHub изменения, например:
```sh
git pull --rebase git@github.com:vasilytray/quick_bot_tutorial.git
```

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

## Актуализация бота с github

### 1. подключить проект на ВМ к git.

В директории /home/mybot/ инициализируем git
```sh
git init
```

В состав Git входит утилита git config, которая позволяет просматривать и настраивать параметры, контролирующие все аспекты работы Git, а также его внешний вид.

Чтобы посмотреть все установленные настройки и узнать где именно они заданы, используйте команду:
```sh
git config --list --show-origin
```

Настроим конкретный проект git под конкретного пользователя локально!:

```sh
git config --local user.name "John Doe"
git config --local user.email johndoe@example.com
```

Локальные настройки будут находиться в Файле config в каталоге Git (т. е. .git/config) репозитория.

Теперь необходимо добавить все наши существующие в дирректории файлы в систему git
```sh
git add *
```

Чтобы проконтролировать, что все файлы добавлены выведем их статус (у добавленных будет статус new file:)
```sh
git status
```
или выведем короткое отображение:
```sh
git status -s
```
при этом добавленные файлы будут иметь пометку 'A'

Останется только закоммитить изменения
```sh
git commit -m "first add"
```

Далее либо запушить на GitHub в новый репозиторий, либо если на GitHub есть версия данного проекта синхронизировать
с репозиторием на GitHub.

### 2. Подключеие проекта к GitHub
#### Настройка подключения к GitHub

Для работы с GitHub без необходимости постоянно вводить логин и пароль при синхронизации локального и удаленного репозитория (находящегося на GitHub) нужно выполнить еще одну важную операцию — добавления ssh-ключей на github.com

Сначала нужно сгенерировать ssh-ключи, а затем один из них (публичный) добавить в настройки GitHub.

```sh
# Создание ssh-ключей
ssh-keygen -t ed25519  -C "your_email@example.com"
# Дальше будет несколько вопросов. На все вопросы нужно нажимать Enter.

# Запуск агента ssh, который следит за ключами
eval "$(ssh-agent -s)"

# Добавления нового ssh-ключа в агент
ssh-add ~/.ssh/id_ed25519
```

Когда **ssh-ключи** созданы и добавлены в систему, можно приступать к интеграции с **GitHub**. Подробно эта процедура описана в документации. 
В двух словах:

1. Выведите содержимое файла ~/.ssh/id_ed25519.pub и скопируйте его:
```sh
cat ~/.ssh/id_ed25519.pub
```

[Добавьте ssh-ключ в аккаунт GitHub.](https://github.com/settings/keys) При добавлении вас попросят назвать ключ. Напишите что-нибудь в стиле home.

Проверьте, что подключение работает
```sh
ssh -T git@github.com
Hi tirion! You've successfully authenticated, but GitHub does not provide shell access.
```

> Есть несколько способов подтянуть репозиторий:
> 1. в существующий проект можно подтянуть командой:
> ```git pull --rebase git@github.com:vasilytray/quick_bot_tutorial.git```
> возможно появятся коллизии с существующими в дирректории файлами.
> git предложит удалить файлы, вызывающие коллизии. (возможно необходимо добавить файли в git и закоммитить)
> 2. Можно клонировать репозиторий и работать с ним.

Клонируем репозиторий с github
```sh
git clone git@github.com:<ИМЯ НА ГИТХАБЕ>/mybot.git
```

Да добавляем наш файл с секретами ``.env ``в проект на ВМ иначе запустить не получиться.

далее запускаем контейнер с ботом как описано выше.

#### Обновление бота из репозитория GitHub

Подтянем изменения из github
```sh
git pull --rebase
```