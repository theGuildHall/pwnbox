#!/bin/bash
cat /etc/openvpn/*.conf | grep "remote " | cut -d " " -f 2 | cut -d "." -f 1 | cut -d "-" -f 2-
