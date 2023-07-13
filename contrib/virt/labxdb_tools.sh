#!/bin/bash

set -o errexit
set -o verbose

source /etc/os-release

echo "==> Install LabxDB-tools"

pip3 install --user --break-system-packages labxdb-tools

echo "==> Install LabxDB-tools dependencies"

if [ "$NAME" = "Arch Linux" ] ; then
    pacman -Sy --noconfirm zstd wget squashfs-tools
fi
if [ "$NAME" = "Debian GNU/Linux" ] || [ "$NAME" = "Ubuntu" ]; then
    apt-get update
    apt-get install -y zstd wget squashfs-tools
    apt-get clean
fi

echo "==> Install SRA tools"

wget --no-verbose https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/current/sratoolkit.current-ubuntu64.tar.gz
tar xvfz sratoolkit.current-ubuntu64.tar.gz
ls -l sratoolkit.*
cp sratoolkit.*-ubuntu64/bin/fastq-dump-orig* $HOME/.local/bin/fastq-dump

echo "==> Configuration LabxDB-tools"

mkdir /etc/hts
cat << EOF > /etc/hts/labxdb.json
{
    "labxdb_http_url": "http://127.0.0.1:8081/",
    "labxdb_http_path_seq": "seq/",
    "labxdb_http_login": "",
    "labxdb_http_password": ""
}
EOF

cat << EOF > $HOME/.bash_profile
[[ -f ~/.bashrc ]] && . ~/.bashrc
EOF

cat << EOF > $HOME/.bashrc
export PATH=$PATH:$HOME/.local/bin
export HTS_CONFIG_PATH="/etc/hts"
EOF
