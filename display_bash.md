Хорошо, я разработаю скрипт на bash для Ubuntu, который будет выводить IP-адрес, маску подсети и шлюз с указанными цветами. Я разделю скрипт на 
два файла: один для получения данных (`get_data.sh`), а другой для отображения данных (`display_output.sh`).

### Файл 1: get_data.sh (получение данных)
Этот файл будет содержать функции и команды, необходимые для извлечения данных о сервере.

```bash
#!/bin/bash

# Получаем IP-адрес, маску подсети и шлюз
IP_ADDRESS=$(ip a | grep 'inet ' | head -n 1 | awk '{print $2}' | cut -d'/' -f1)
NETMASK=$(ip a | grep 'inet ' | head -n 1 | awk '{print $4}')
GATEWAY=$(route -n | grep '^0.0.0.0' | awk '{print $2}')

# Экспорт переменных
export IP_ADDRESS=$IP_ADDRESS
export NETMASK=$NETMASK
export GATEWAY=$GATEWAY
```

### Файл 2: display_output.sh (вывод данных)
Этот файл будет содержать код для форматирования и отображения данных с указанными цветами.

```bash
#!/bin/bash

# Импортируем данные из get_data.sh
source ./get_data.sh

# Определяем цвета
BLUE='\e[34m'
WHITE_BG='\e[47m'
RESET='\e[0m'

# Выводим данные
echo -e "${BLUE}${WHITE_BG}IP-адрес: ${RESET}${BLUE}${WHITE_BG}$IP_ADDRESS${RESET}"
echo -e "${BLUE}${WHITE_BG}Маска подсети: ${RESET}${BLUE}${WHITE_BG}$NETMASK${RESET}"
echo -e "${BLUE}${WHITE_BG}Шлюз: ${RESET}${BLUE}${WHITE_BG}$GATEWAY${RESET}"

# Выводим значения цветов в формате #
echo -e "\nЗначения цветов:"
echo -e "Цвет текста (синий): #0000FF"
echo -e "Фон (белый): #FFFFFF"
```

### Объяснение:

1. `get_data.sh`:
   - Использует команду `ip a` для получения информации о сетевых интерфейсах.
   - Извлекает IP-адрес, маску подсети и шлюз с помощью grep, awk и cut.
   - Экспортирует переменные, чтобы они могли быть доступны в другом файле.

2. `display_output.sh`:
   - Импортирует данные из `get_data.sh`.
   - Определяет ANSI-коды для синего текста и белого фона.
   - Выводит данные в форматированном виде с указанными цветами.
   - В конце выводит значения цветов в формате HEX.

### Как использовать:

1. Сохраните оба файла в одной директории:
   ```bash
   nano get_data.sh
   nano display_output.sh
   ```

2. Добавьте права на выполнение:
   ```bash
   chmod +x get_data.sh | chmod +x display_output.sh
   ```

3. Запустите скрипт:
   ```bash
   ./display_output.sh
   ```

Скрипт будет выводить данные сервера с синим текстом на белом фоне и затем показывать значения цветов в формате HEX.