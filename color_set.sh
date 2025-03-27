#!/bin/bash

func_col(){
    case "$1" in
        1) echo -e "\033[107m";;
        2) echo -e "\033[41m";;
        3) echo -e "\033[42m";;
        4) echo -e "\033[46m";;
        5) echo -e "\033[45m";;
        6) echo -e "\033[40m";;
    esac
}

func_text_col(){
    case "$2" in
        1) echo -e "\033[97m";;
        2) echo -e "\033[31m";;
        3) echo -e "\033[32m";;
        4) echo -e "\033[36m";;
        5) echo -e "\033[35m";;
        6) echo -e "\033[30m";;
    esac
}