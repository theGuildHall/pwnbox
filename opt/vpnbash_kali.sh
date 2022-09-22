#!/bin/bash
htbip=$(ip addr | grep tun0 | grep inet | grep 10. | tr -s " " | cut -d " " -f 3 | cut -d "/" -f 1)

if [[ $htbip == *"10."* ]]
then
   echo "[%B%F{%(#.red.blue)}$(/opt/vpnserver.sh)%b%F{%(#.blue.green)}]-[%B%F{%(#.red.blue)}$htbip%b%F{%(#.blue.green)}]-"
else
   echo ""
fi