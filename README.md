# Pwnbox

Want to replicate Hack the Box very own Pwnbox? Follow the guide below!

## Step 1 - Download the ISO/ova image

Visit the Parrotsec page and download the ISO or ova image, depending on what your environment calls for. I have an Unraid server at home which allows me to create VMs, so that's what I'm going to use as an example. This setup should work for any VM software setup.

- [Download OVA](https://download.parrot.sh/parrot/iso/4.9.1/Parrot-security-4.9.1_x64.iso)

Once you have downloaded the OS, install it and proceed to step 2.

## Step 2 - Setup your scripts in /opt

Pwnbox has some scripts inside folder `/opt` which you will need to create. Use `sudo` to create these files

### banner

```bash
Welcome to your Parrot Linux desktop!

Internet access is allowed, subject to the following:
1. This instance is not meant to perform assessments or interact with any live targets.
2. Pen-testing any target (with or without consent) outside of HTB labs is prohibited.

Remember! Do not store any personal or sensitive information in this box!
Its only purpose is to allow you to play in our labs.

Feel free to install any tools you prefer. PS: You have sudo :)

Note that once this instance is terminated, all data including tools you installed will be lost!

```

### banner.sh

```bash
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

```

### vpnbash.sh

```bash
#!/bin/bash
htbip=$(ip addr | grep tun0 | grep inet | grep 10. | tr -s " " | cut -d " " -f 3 | cut -d "/" -f 1)

if [[ $htbip == *"10."* ]]
then
   echo "$htbip"
else
   echo ""
fi
```

### vpnpanel.sh

```bash
#!/bin/bash
htbip=$(ip addr | grep tun0 | grep inet | grep 10. | tr -s " " | cut -d " " -f 3 | cut -d "/" -f 1)
lab=$(cat /etc/openvpn/*.conf | grep "remote " | cut -d " " -f 2 | cut -d "." -f 1 | cut -d "-" -f 2-)

if [[ $htbip == *"10."* ]]
then
   gwip=$(route -n | grep tun0 | grep UG | tr -s " " | cut -d " " -f 2)
   ping=$(ping -c 1 $gwip -W 1 | sed '$!d;s|.*/\([0-9.]*\)/.*|\1|' | cut -c1-4)
   echo "HTB VPN: $lab ($htbip) [$ping ms]"
else
   echo "HTB VPN: Disconnected"
fi
```

### vpnserver.sh

```bash
#!/bin/bash
cat /etc/openvpn/*.conf | grep "remote " | cut -d " " -f 2 | cut -d "." -f 1 | cut -d "-" -f 2-
```

### PS1 (terminal)

`export PS1='\[\033[1;32m\]\342\224\200$([[ $(/opt/vpnbash.sh) == *"10."* ]] && echo "[\[\033[1;34m\]$(/opt/vpnserver.sh)\[\033[1;32m\]]\342\224\200[\[\033[1;37m\]$(/opt/vpnbash.sh)\[\033[1;32m\]]\342\224\200")[\[\033[1;37m\]\u\[\033[01;32m\]@\[\033[01;34m\]\h\[\033[1;32m\]]\342\224\200[\[\033[1;37m\]\w\[\033[1;32m\]]\$\[\e[0m\]'`

If you want to make this permanent, edit your `bashrc` file. This is the `bashrc` file from pwnbox:

- `nano ~/.bashrc`

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
    PS1="\[\033[0;31m\]\342\224\214\342\224\200\$([[ \$? != 0 ]] && echo \"[\[\033[0;31m\]\342\234\227\[\033[0;37m\]]\342\224\200\")[$(if [[ ${EUID} == 1 ]]; then echo '\[\033[01;31m\]root\[\033[01;33m\]☺\[\033[01;96m\]\h'; else echo '\[\033[0;39m\]\u\[\033[01;33m\]☺\[\033[01;96m\]\h'; fi)\[\033[0;31m\]]\342\224\200[\[\033[0;32m\]\w\[\033[0;31m\]]\n\[\033[0;31m\]\342\224\224\342\224\200\342\224\200\342\225\274 \[\033[0m\]\[\e[01;33m\]\\$\[\e[0m\]"
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
Create folder in /opt called 'bloodhound'

- `sudo mkdir /opt/bloodhound`

Then create script `startBH.sh`

```bash
#!/bin/bash
NEOSTATUS=$(sudo neo4j status)
if [ "$NEOSTATUS" == "Neo4j is not running" ]; then
   echo "Database is not running. Starting..."
   sudo neo4j start
   sleep 10
   bloodhound
else
   echo "Database is already started."
   bloodhound
fi
```

