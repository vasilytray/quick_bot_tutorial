#!/bin/bash 

source ./color_set.sh
source ./system_set.sh

for par in "$1" "$2" "$3" "$4"; do
    if ! [[ "$par" =~ ^[1-6]$ ]]; then
        echo "The parametrs should be only numbers from 1 to 6"
        exit 1
    fi
    done

if [ $1 -eq $2 ] || [ $3 -eq $4 ]
then 
    echo "The backgrounds and fonts should be in different colors"
    echo "May be you should restart the program?"
    exit 1
fi

if [ $# -eq 4 ]; then
    if [ -f system_set.sh ]; then 
        func_info
        exit 0
    fi
else 
    echo "Too many parametrs in the command line"
    exit 1
fi