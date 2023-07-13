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
    pacman -Sy --noconfirm nftables caddy
fi
if [ "$NAME" = "Debian GNU/Linux" ] || [ "$NAME" = "Ubuntu" ]; then
    apt-get update
    apt-get install -y nftables caddy
    apt-get clean
fi

cd /etc
mv nftables.conf nftables.conf.0
wget https://git.sr.ht/~vejnar/LabxDB/blob/main/contrib/virt/nftables.conf

systemctl enable --now nftables

echo "==> Install Caddy"

# Get Caddy config
cd /etc/caddy
wget --no-verbose https://git.sr.ht/~vejnar/LabxDB/blob/main/contrib/virt/caddy.json

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
systemctl enable --now caddy
