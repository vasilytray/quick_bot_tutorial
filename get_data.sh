#!/bin/bash

# Получаем IP-адрес, маску подсети и шлюз
IP_ADDRESS=$(ifconfig ens34 | grep -w "inet" | awk '{print$2}')
SUBNET_MASK=echo $(ifconfig ens34 | grep -w "netmask" |  awk '{print $4}')
GATEWAY=$(route -n | grep "^0.0.0.0" | awk '{print $2}')

# Экспорт переменных
export IP_ADDRESS=$IP_ADDRESS
export NETMASK=$NETMASK
export GATEWAY=$GATEWAY