#!/bin/bash

source ./color_set.sh

n_b=$(func_col $1)
n_sh=$(func_text_col 2 $2)
ec_b=$(func_col $3)
ec_sh=$(func_text_col 2 $4)
null_col="\033[0m"

func_info(){
    echo -e "${n_b}${n_sh}HOSTNAME${null_col} =" ${ec_b}${ec_sh}$HOSTNAME${null_col}
    echo -e "${n_b}${n_sh}TIMEZONE${null_col} =" ${ec_b}${ec_sh}$(timedatectl show --property=Timezone --value) "UTC" $(date +%z | sed 's/\([+-]\{0,1\}.\{2\}\).*/\1/' | sed 's/^+0/+/; s/^-0/-/')${null_col}
    echo -e "${n_b}${n_sh}USER${null_col} =" ${ec_b}${ec_sh}$USER${null_col}${null_col}
    echo -e "${n_b}${n_sh}OS${null_col} =" ${ec_b}${ec_sh}$(cat /etc/issue)${null_col}
    echo -e "${n_b}${n_sh}DATE${null_col} =" ${ec_b}${ec_sh}$(date +'%d %B %Y %R:%S')${null_col}
    echo -e "${n_b}${n_sh}UPTIME${null_col} =" ${ec_b}${ec_sh}$(uptime -p | sed 's/up //')${null_col}
    echo -e "${n_b}${n_sh}UPTIME_SEC${null_col} = ${ec_b}${ec_sh}$(awk '{print $1}' /proc/uptime) seconds${null_col}"
    echo -e "${n_b}${n_sh}IP${null_col} =" ${ec_b}${ec_sh}$(hostname -I | awk '{print $1}' | sed -n '1p')${null_col}
    echo -e "${n_b}${n_sh}MASK${null_col} =" ${ec_b}${ec_sh}$(ifconfig | grep -w "inet" | awk '{print $4}' | sed -n '1p')${null_col}  
    echo -e "${n_b}${n_sh}GATEWAY${null_col} =" ${ec_b}${ec_sh}$(ip route | grep 'default via' | awk '{print $3}' | sed -n '1p')${null_col}
    echo -e "${n_b}${n_sh}RAM_TOTAL${null_col} =" ${ec_b}${ec_sh}$(vmstat -s | grep 'total memory' | awk '{printf "%.3f GB", $1/1048576}')${null_col}
    echo -e "${n_b}${n_sh}RAM_USED${null_col} =" ${ec_b}${ec_sh}$(vmstat -s | grep 'used memory' | awk '{printf "%.3f GB", $1/1048576}')${null_col}
    echo -e "${n_b}${n_sh}RAM_FREE${null_col} =" ${ec_b}${ec_sh}$(vmstat -s | grep 'free memory' | awk '{printf "%.3f GB", $1/1048576}')${null_col}
    echo -e "${n_b}${n_sh}SPACE_ROOT${null_col} =" ${ec_b}${ec_sh}$(df -m / | grep '/dev/' | awk '{printf "%.2f M", $2}')${null_col}
    echo -e "${n_b}${n_sh}SPACE_ROOT_USED${null_col} =" ${ec_b}${ec_sh}$(df -m / | grep '/dev/' | awk '{printf "%.2f M", $3}')${null_col}
    echo -e "${n_b}${n_sh}SPACE_ROOT_FREE${null_col} =" ${ec_b}${ec_sh}$(df -m / | grep '/dev/' | awk '{printf "%.2f M", $2}')${null_col}
}