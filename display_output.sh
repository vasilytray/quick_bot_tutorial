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