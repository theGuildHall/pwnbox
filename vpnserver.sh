#!/bin/bash

#cat /etc/openvpn/*.conf | grep "remote " | cut -d " " -f 2 | cut -d "." -f 1 | cut -d "-" -f 2-

vpn=$(cat `systemctl status openvpn@* | grep "/usr/sbin/openvpn" | tr -s " " | cut -d " " -f 12` | grep "remote " | cut -d " " -f 2)

if [[ $vpn == *"hackthebox"* ]]
then
    cat `systemctl status openvpn@* | grep "/usr/sbin/openvpn" | tr -s " " | cut -d " " -f 12` | grep "remote " | cut -d " " -f 2 | cut -d "." -f 1 | cut -d "-" -f 2-
else
    cat `systemctl status openvpn@* | grep "/usr/sbin/openvpn" | tr -s " " | cut -d " " -f 12` | grep "remote " | cut -d " " -f 2
fi
