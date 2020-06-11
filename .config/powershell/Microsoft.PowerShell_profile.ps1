function vpnStats
{
    $htbip = (/opt/vpnbash.sh)
    if ($htbip -like '*10.*') {
        $vpnserver = (/opt/vpnserver.sh)
        return "`e[32m[`e[34m$vpnserver`e[32m]─[`e[37m$htbip`e[32m]─"
    } else {
        return ""
    }
}

function prompt
{
    Write-Host ("`e[1;32m┌─" + (vpnStats) + "`e[32m[`e[37m" + [Environment]::UserName + "`e[32m@`e[34m" + (hostname) + "`e[32m]─[`e[37m" + (Get-Location) + "`e[32m]")
    Write-Host ("`e[32m└──╼ [`e[34mPS`e[32m]>") -nonewline
    return " "
}
