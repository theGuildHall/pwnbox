#!/bin/bash
echo -e "\e[32m       ▄▄▄▀▄▄▄"
echo -e "\e[32m  ▄▄▀▀▀       ▀▀▄▄▄"
echo -e "\e[32m █▀▀▄▄         ▄▄▀▀█ \e[37m █  █         ▐▌     ▄█▄ █          ▄▄▄▄"
echo -e "\e[32m █    ▀▀▀▄▄▄▀▀▀    █ \e[37m █▄▄█ ▀▀█ █▀▀ ▐▌▄▀    █  █▀█ █▀█    █▌▄█ ▄▀▀▄ ▀▄▀"
echo -e "\e[32m █        █        █ \e[37m █  █ █▄█ █▄▄ ▐█▀▄    █  █ █ █▄▄    █▌▄█ ▀▄▄▀ █▀█"
echo -e "\e[32m █        █        █"
echo -e "\e[32m █        █        █ \e[37m P  E  N   -   T  E  S  T  I  N  G     L  A  B  S"
echo -e "\e[32m ▀▀▄▄     █     ▄▄▀▀"
echo -e "\e[32m     ▀▀▀▄▄█▄▄▀▀▀"
echo " "
cat /opt/banner | /usr/games/lolcat -S 55

read -r -p "Press ENTER key to close. " response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
then
    exit
fi
