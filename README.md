# Pwnbox

![htb screenshot](images/htb_screenshot.png?raw=true "Pwnbox")

Want to replicate Hack the Box very own Pwnbox? Follow the guide below!
This should give you the "look and feel" of pwnbox used by Hack The Box.
Everything shown here can be done in your own Parrot OS, whether it is VM or main OS.
However, I suggest you look into what each command does, where it goes, and how you can go about customizing it to your own taste. For me, whenever I ssh into my Parrot machine, it gives me fun hackthebox logo. Go on, make it your own!

```bash

  █  █         ▐▌     ▄█▄ █          ▄▄▄▄
  █▄▄█ ▀▀█ █▀▀ ▐▌▄▀    █  █▀█ █▀█    █▌▄█ ▄▀▀▄ ▀▄▀
  █  █ █▄█ █▄▄ ▐█▀▄    █  █ █ █▄▄    █▌▄█ ▀▄▄▀ █▀█

  P  E  N   -   T  E  S  T  I  N  G     L  A  B  S

  what the box?
```

## Setup

Clone this repo, then run `setup.sh` file to install pwnbox

## Setup OpenVPN

We also need to add your vpn file to your /etc/openvpn location:

`sudo cp [your VPN FILE].ovpn /etc/openvpn/`

`sudo mv /etc/openvpn/[your VPN file].ovpn /etc/openvpn/[your VPN file].conf`

Make sure you rename your file to `.conf`. Then you can start your VPN like you would normally do.

## Update theme

Go to the top menu bar and choose:

System -> Preferences -> Look and Feel -> Appearance

You should now see a theme called "HackTheBox". Select it and select "Apply Background".

> At this point, you should have most of the Pwnbox 'look and feel'. However, if you want to further customize it, keep following allong.

## Customizing panels

On the top panel, right click one of the three system monitors graphs (the ones showing your 'process', 'memory', and 'network'). Select "Remove from Panel".

Next, on the top panel, right click the "shell" icon (the one that looks like a bash prompt). Select "Properties".

> NOTE : You will see the "Launcher Properties" pop up. This is where you can really customize your ParrotOS. You don't need to follow what Hack the Box did. You can add ANY script you want, any command, icon, etc, to your OS! This is how you can truly personalize it.

Click on the bash icon to the left, and a window should pop up asking you to select an icon. Navigate to /usr/share/icons/htb/ and choose `bash.svg`.

- ## To get the 'ping panel'

    Right click on a blank space on the top panel and choose "Add to Panel". In the search bar, type "command", select "command" then click "add". The current time should populate on the top panel. Right click on it, and in the command section, paste in `/opt/vpnpanel.sh`, with an interval of "5" seconds. It should show "HTB VPN: Disconnected" unless you are on the vpn.

- ## To get the "processor" menu

    Right click on a blank space on the top panel and search for "System monitor". Select it and add it. Right click on the little black box that appeared, select "preferences" and under "System monitor width", update it to "135" pixels, and updated the field below it to "100" milliseconds.

- ## 'Plank', the MacOS bar on the bottom

    Start by deleting the bottom panel by `right clicking` and selecting `delete this panel`.

    `sudo apt install plank -y`

    Once Plank is installed, on the top bar, go to "System -> Preferences -> Personal -> Startup Application". Right hand side, select "Add" and fill in the values:

    - Name: Plank
    - Command: plank
    - Delay: 0

    Plank will now startup whenever you reboot your machine.

# Conclusion

> This should be it for the setup! The actual pwnbox has some extra icons on the desktop such as a shortcut to "bloodhound", "burpsuite", and others. There's even a MacOS launcher bar on the bottom. I'm going to leave that up to you to add. 

> I highly suggest adding VNC support if needed. I am currently running tigerVNC on my Parrot machine and it works great! 

> Otherwise, that finishes that for this tutorial.
