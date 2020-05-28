#!/bin/bash

set -o errexit
set -o verbose

source /etc/os-release

echo "==> Updating IP"

if [ -n "$DUCKDNS_DOMAIN" ]; then
    DOMAIN="$DUCKDNS_DOMAIN"
    wget -qO- "https://www.duckdns.org/update?domains=$DUCKDNS_DOMAIN&token=$DUCKDNS_TOCKEN&ip="
    sleep 40
fi

echo "==> Install Nftables"

if [ "$NAME" = "Arch Linux" ] ; then
    pacman -Sy --noconfirm nftables
fi
if [ "$NAME" = "Debian GNU/Linux" ] || [ "$NAME" = "Ubuntu" ]; then
    apt-get update
    apt-get install -y nftables
    apt-get clean
fi

cd /etc
mv nftables.conf nftables.conf.0
wget https://gitlab.com/vejnar/labxdb/-/raw/master/contrib/virt/nftables.conf

systemctl start nftables
systemctl enable nftables

echo "==> Install Caddy"

# Get latest executable
url=$(wget -qO- https://api.github.com/repos/caddyserver/caddy/releases/latest | grep browser_download_url | grep linux_amd64.tar.gz | cut -d '"' -f 4)
cd /tmp
wget --no-verbose -O caddy.tar.gz $url
tar xvfz caddy.tar.gz
mv caddy /usr/local/bin

# Get Caddy config
mkdir /etc/caddy
cd /etc/caddy
wget --no-verbose https://gitlab.com/vejnar/labxdb/-/raw/master/contrib/virt/caddy.json

if [ -n "$DOMAIN" ]; then
    sed -i "s/labxdb.duckdns.org/$DOMAIN/" /etc/caddy/caddy.json
fi
if [ -n "$ACME_EMAIL" ]; then
    sed -i "s/your-email@your-domain.org/$ACME_EMAIL/" /etc/caddy/caddy.json
fi
if [ "$ACME_STAGING" = "no" ]; then
    sed -i "s/acme-staging-v/acme-v/" /etc/caddy/caddy.json
fi

# Config systemd service
cat << EOF > /etc/systemd/system/caddy.service
[Unit]
Description=Caddy
After=network.target network-online.target nss-lookup.target

[Service]
Type=notify
Environment=XDG_DATA_HOME=/etc
Environment=XDG_CONFIG_HOME=/etc
ExecStart=/usr/local/bin/caddy run --config /etc/caddy/caddy.json
Restart=always
WatchdogSec=1s

[Install]
WantedBy=multi-user.target
EOF

systemctl start caddy
systemctl enable caddy
