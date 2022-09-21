blue='\e[0;34'
cyan='\e[0;36m'
green='\e[0;34m'
okegreen='\033[92m'
lightgreen='\e[1;32m'
white='\e[1;37m'
red='\e[1;31m'
yellow='\e[1;33m'

kali=`cat /etc/os-release | grep Kali`
parrot=`cat /etc/os-release | grep Parrot`

echo -e "$yellow //$white Getting OS information "

if [[ $kali ]]
then
        echo -e "$cyan **$white OS : Kali Linux"
        rc='zshrc'
        configname='kali'
elif [[ $parrot ]]
then
        echo -e "$cyan **$white OS : Parrot OS"
        rc='bashrc'
        configname='parrot'
else
    echo -e "$red !!$white OS Not Supported, Exitting..."
    exit 
fi

echo -e "$yellow //$white Copying shell configuration"
cp ~/.$rc ~/.$rc.bak
cp $rc ~/.$rc
echo -e "$yellow //$white Copying scripts, sublime text, and bloodhound to /opt"
sudo cp -r opt /opt
echo -e "$yellow //$white Copying wallpapers, icons, and themes to /usr/share"
sudo cp -r usr /usr
echo -e "$yellow //$white Configuring openvpn"
sudo cp /opt/vpnbash_$configname.sh /opt/vpnbash.sh
echo -e "$yellow //$white Copying configs"
cp -r .config ~/.config