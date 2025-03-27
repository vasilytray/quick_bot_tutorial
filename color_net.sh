#!/bin/bash

# Находим данные о сети
IP_ADDRESS=$(ifconfig eth0 | grep "inet addr" | cut -d: -f2 | awk '{print $1}')
SUBNET_MASK=$(ifconfig eth0 | grep "Mask" | cut -d: -f4 | awk '{print $1}')
GATEWAY=$(route -n | grep "^0.0.0.0" | awk '{print $2}')

# Вывод данных с розовыми значениями
echo -e "\nСерверные данные:"
echo -e "\nIP-адрес:\t\033[38;5;219m$IP_ADDRESS\033[0m"
echo -e "Маска подсети:\t\033[38;5;219m$SUBNET_MASK\033[0m"
echo -e "Шлюз:\t\t\033[38;5;219m$GATEWAY\033[0m\n"
# run chmod +x color_net.sh
# run ./color_net.sh