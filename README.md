# Pwnbox

![htb screenshot](htb_screenshot.png?raw=true "Pwnbox")

**For those using Kali, I added some steps at the bottom to get the new zsh terminal in 2020.3 to show your server/IP**

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

## Step 0: Parrot MATE

Just want to clarify that the instructions below work on Parrot Mate, available to download here: [https://download.parrot.sh/parrot/iso/4.10/Parrot-security-4.10_x64.iso](https://download.parrot.sh/parrot/iso/4.10/Parrot-security-4.10_amd64.iso)

## Step 1: Clone Repo 
In my setup below, I have created a directory called "gitclones" in my home directory.

`mkdir ~/gitclones && cd ~/gitclones`

`git clone https://github.com/theGuildHall/pwnbox.git`

## Step 2: Copy over the files

`cd ~/gitclones/pwnbox`

`sudo cp *.sh /opt && sudo cp -R bloodhound/ /opt && sudo cp -R htb/ /opt && sudo cp -R icons/ /opt && sudo cp banner /opt`

We also need to add your vpn file to your /etc/openvpn location:

`sudo cp [your VPN FILE].ovpn /etc/openvpn/`

`sudo mv /etc/openvpn/[your VPN file].ovpn /etc/openvpn/[your VPN file].conf`

Make sure you rename your file to `.conf`. Then you can start your VPN like you would normally do.

## Step 3: Update your terminal

### Bash terminal

nano .bashrc
erase everything inside it (or better yet, make a backup of it cause that's a good habit: `cp ~/.bashrc ~/.bashrc.bak`)
Copy this into your .bashrc file:

```bash
# ~/.bashrc: executed by bash(1) for non-login shells.
# see /usr/share/doc/bash/examples/startup-files (in the package bash-doc)
# for examples

# If not running interactively, don't do anything
case $- in
    *i*) ;;
      *) return;;
esac

export PATH=/usr/local/bin:/usr/bin:/bin:/usr/local/games:/usr/games:/usr/share/games:/usr/local/sbin:/usr/sbin:/sbin:~/.local/bin:/snap/bin:$PATH

# don't put duplicate lines or lines starting with space in the history.
# See bash(1) for more options
HISTCONTROL=ignoreboth

# append to the history file, don't overwrite it
shopt -s histappend

# for setting history length see HISTSIZE and HISTFILESIZE in bash(1)
HISTSIZE=1000
HISTFILESIZE=2000

# check the window size after each command and, if necessary,
# update the values of LINES and COLUMNS.
shopt -s checkwinsize

# If set, the pattern "**" used in a pathname expansion context will
# match all files and zero or more directories and subdirectories.
#shopt -s globstar

# make less more friendly for non-text input files, see lesspipe(1)
#[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"

# set variable identifying the chroot you work in (used in the prompt below)
if [ -z "${debian_chroot:-}" ] && [ -r /etc/debian_chroot ]; then
    debian_chroot=$(cat /etc/debian_chroot)
fi

# set a fancy prompt (non-color, unless we know we "want" color)
case "$TERM" in
    xterm-color) color_prompt=yes;;
esac

# uncomment for a colored prompt, if the terminal has the capability; turned
# off by default to not distract the user: the focus in a terminal window
# should be on the output of commands, not on the prompt
force_color_prompt=yes

if [ -n "$force_color_prompt" ]; then
    if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
	# We have color support; assume it's compliant with Ecma-48
	# (ISO/IEC-6429). (Lack of such support is extremely rare, and such
	# a case would tend to support setf rather than setaf.)
	color_prompt=yes
    else
	color_prompt=
    fi
fi

if [ "$color_prompt" = yes ]; then
    PS1="\[\033[1;32m\]\342\224\214\342\224\200$([[ $(/opt/vpnbash.sh) == *"10."* ]] && echo "[\[\033[1;34m\]$(/opt/vpnserver.sh)\[\033[1;32m\]]\342\224\200[\[\033[1;37m\]$(/opt/vpnbash.sh)\[\033[1;32m\]]\342\224\200")[\[\033[1;37m\]\u\[\033[01;32m\]@\[\033[01;34m\]\h\[\033[1;32m\]]\342\224\200[\[\033[1;37m\]\w\[\033[1;32m\]]\n\[\033[1;32m\]\342\224\224\342\224\200\342\224\200\342\225\274 [\[\e[01;33m\]??\[\e[01;32m\]]\\$ \[\e[0m\]"
else
    PS1='┌──[\u@\h]─[\w]\n└──╼ \$ '
fi

# Set 'man' colors
if [ "$color_prompt" = yes ]; then
	man() {
	env \
	LESS_TERMCAP_mb=$'\e[01;31m' \
	LESS_TERMCAP_md=$'\e[01;31m' \
	LESS_TERMCAP_me=$'\e[0m' \
	LESS_TERMCAP_se=$'\e[0m' \
	LESS_TERMCAP_so=$'\e[01;44;33m' \
	LESS_TERMCAP_ue=$'\e[0m' \
	LESS_TERMCAP_us=$'\e[01;32m' \
	man "$@"
	}
fi

unset color_prompt force_color_prompt

# If this is an xterm set the title to user@host:dir
case "$TERM" in
xterm*|rxvt*)
    PS1="\[\033[1;32m\]\342\224\200\$([[ \$(/opt/vpnbash.sh) == *\"10.\"* ]] && echo \"[\[\033[1;34m\]\$(/opt/vpnserver.sh)\[\033[1;32m\]]\342\224\200[\[\033[1;37m\]\$(/opt/vpnbash.sh)\[\033[1;32m\]]\342\224\200\")[\[\033[1;37m\]\u\[\033[01;32m\]@\[\033[01;34m\]\h\[\033[1;32m\]]\342\224\200[\[\033[1;37m\]\w\[\033[1;32m\]]\\$\[\e[0m\] "
    ;;
*)
    ;;
esac

# enable color support of ls and also add handy aliases
if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    alias dir='dir --color=auto'
    alias vdir='vdir --color=auto'

    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
fi

# some more ls aliases
alias ll='ls -lh'
alias la='ls -lha'
alias l='ls -CF'
alias em='emacs -nw'
alias dd='dd status=progress'
alias _='sudo'
alias _i='sudo -i'
alias please='sudo'
alias fucking='sudo'
alias chuck_norris_says='sudo'

# Alias definitions.
# You may want to put all your additions into a separate file like
# ~/.bash_aliases, instead of adding them here directly.
# See /usr/share/doc/bash-doc/examples in the bash-doc package.

if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi

# enable programmable completion features (you don't need to enable
# this, if it's already enabled in /etc/bash.bashrc and /etc/profile
# sources /etc/bash.bashrc).
if ! shopt -oq posix; then
  if [ -f /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
  elif [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
  fi
fi
```

Then reload your bashrc file:

`source ~/.bashrc`

> NOTE: Once you are connected to the HTB vpn, you'll see your IP and other info in your termianl. Otherwise, it'll just show your username/host and current working directory.

> NOTE 2: Pwnbox now has an **updated** terminal. This is purely by choice so if you want to use what Pwnbox has, replace the "PS1" line above that has "xterm*|rxvt*)..." with this new *PS1* output:

`\[\033[1;32m\]\342\224\200$([[ $(/opt/vpnbash.sh) == *"10."* ]] && echo "[\[\033[1;34m\]$(/opt/vpnserver.sh)\[\033[1;32m\]]\342\224\200[\[\033[1;37m\]$(/opt/vpnbash.sh)\[\033[1;32m\]]\342\224\200")[\[\033[1;37m\]\u\[\033[01;32m\]@\[\033[01;34m\]\h\[\033[1;32m\]]\342\224\200[\[\033[1;37m\]\w\[\033[1;32m\]]\$\[\e[0m\]`

### Powershell terminal (optional)

Since ParrotOS doesn't come with the Powershell core installed, you can add it with:

`sudo apt install -y powershell`

Confirm that it is installed with

`pwsh`

Once installed, you can further customize the terminal by creating a folder in your `/home/[username]/.config/powershell/Microsoft.PowerShell_profile.ps1`

`mkdir ~/.config/powershell/`

Then copy over the `Microsoft.PowerShell_profile.ps1` to your location (copy and pasting leads to a bunch of question marks)

`cp ~/gitclones/pwnbox/Microsoft.PowerShell_profile.ps1 ~/.config/powershell/Microsoft.PowerShell_profile.ps1`

## Step 4: Update theme

Copy background image to machine:

`sudo cp ~/gitclones/pwnbox/htb.jpg /usr/share/backgrounds/`

Copy icons and sublime text to machine:

`sudo cp -R ~/gitclones/pwnbox/Material-Black-Lime-Numix-FLAT/ /usr/share/icons/`

`sudo cp -R ~/gitclones/pwnbox/htb /usr/share/icons/`

`sudo mkdir /usr/share/themes/HackTheBox && sudo cp ~/gitclones/pwnbox/index.theme /usr/share/themes/HackTheBox`


Now go to the top menu bar and choose:

System -> Preferences -> Look and Feel -> Appearance

You should now see a theme called "HackTheBox". Select it and select "Apply Background".

### At this point, you should have most of the Pwnbox 'look and feel'. However, if you want to further customize it, keep following allong.

---

## Step 5: Updating the 'Panels'

On the top panel, right click one of the three system monitors graphs (the ones showing your 'process', 'memory', and 'network'). Select "Remove from Panel".

Next, on the top panel, right click the "shell" icon (the one that looks like a bash prompt). Select "Properties".

### NOTE:You will see the "Launcher Properties" pop up. This is where you can really customize your ParrotOS. You don't need to follow what Hack the Box did. You can add ANY script you want, any command, icon, etc, to your OS! This is how you can truly personalize it.

Click on the bash icon to the left, and a window should pop up asking you to select an icon. Navigate to /usr/share/icons/htb/ and choose `bash.svg`.

### To install sublime text...

`sudo cp -R ~/gitclones/pwnbox/sublime_text /opt`

Then on the top panel, right click on the "notepad" and select "properties". In the "name", change it to "Sublime", and then under "command", change it to "/opt/sublime_text/sublime_text %F". Then click on the icon to the left, and change it to "/opt/icons/sublime-text.png"

### To get the 'ping panel'

Right click on a blank space on the top panel and choose "Add to Panel". In the search bar, type "command", select "command" then click "add". The current time should populate on the top panel. Right click on it, and in the command section, paste in `/opt/vpnpanel.sh`, with an interval of "5" seconds. It should show "HTB VPN: Disconnected" unless you are on the vpn.

### To get the "processor" menu

Right click on a blank space on the top panel and search for "System monitor". Select it and add it. Right click on the little black box that appeared, select "preferences" and under "System monitor width", update it to "135" pixels, and updated the field below it to "100" milliseconds.

### 'Plank', the MacOS bar on the bottom

Start by deleting the bottom panel by `right clicking` and selecting `delete this panel`.

`sudo apt install plank -y`

Once Plank is installed, on the top bar, go to "System -> Preferences -> Personal -> Startup Application". Right hand side, select "Add" and fill in the values:

- Name: Plank
- Command: plank
- Delay: 0

Plank will now startup whenever you reboot your machine.

## For Kali Users

With the new 2020.3 version of Kali, they implemented a new shell for `zsh`. I wanted to get the HTB IP and server in the terminal prompt so I made some updates.

1. Clone or copy over the `vpnpanel.sh`, `vpnbash.sh`, and `vpnpanel.sh` over to your `/opt/*` directory.
2. Update the `vpnbash.sh` script to this:

```bash
#!/bin/bash
htbip=$(ip addr | grep tun0 | grep inet | grep 10. | tr -s " " | cut -d " " -f 3 | cut -d "/" -f 1)

if [[ $htbip == *"10."* ]]
then
   echo "[%B%F{%(#.red.blue)}$(/opt/vpnserver.sh)%b%F{%(#.blue.green)}]-[%B%F{%(#.red.blue)}$htbip%b%F{%(#.blue.green)}]-"
else
   echo ""
fi

```

3. (optional) If you haven't switched your kali terminal to zsh, do that with `chsh -s /usr/bin/zsh`. Then log out, log back in. You should have a cool looking prompt

4. Update the PS1 variable in `~/.zshrc` (using nano or your favorite editor) to `PROMPT=$'%F{%(#.blue.green)}┌──${debian_chroot:+($debian_chroot)──}$(/opt/vpnbash.sh)(%B%F{%(#.red.blue)}%n%(#.💀.㉿)%m%b%F{%(#.blue.green)})-[%B%F{reset}%(6~.%-1~/…/%4~.%5~)%b%F{%(#.blue.green)}]\n└─%B%(#.%F{red}#.%F{blue}$)%b%F{reset} '`

If you want to test it out before changing your .zshrc file, use `export PS1='%F{%(#.blue.green)}┌──${debian_chroot:+($debian_chroot)──}$(/opt/vpnbash.sh)(%B%F{%(#.red.blue)}%n%(#.💀.㉿)%m%b%F{%(#.blue.green)})-[%B%F{reset}%(6~.%-1~/…/%4~.%5~)%b%F{%(#.blue.green)}]
└─%B%(#.%F{red}#.%F{blue}$)%b%F{reset} '`

# Conclusion

This should be it for the setup! The actual pwnbox has some extra icons on the desktop such as a shortcut to "bloodhound", "burpsuite", and others. There's even a MacOS launcher bar on the bottom. I'm going to leave that up to you to add. 

I highly suggest adding VNC support if needed. I am currently running tigerVNC on my Parrot machine and it works great! 

Otherwise, that finishes that for this tutorial.
