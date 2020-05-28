#!/bin/bash

set -o errexit
set -o verbose

source /etc/os-release

echo "==> Install LabxDB-Python"

# Set target
if [ -z "$TARGET" ]; then
    TARGET="/root/labxdb-python"
fi

cd $TARGET

if [ "$NAME" = "Arch Linux" ] ; then
    pacman -Sy --noconfirm zstd wget squashfs-tools
fi
if [ "$NAME" = "Debian GNU/Linux" ] || [ "$NAME" = "Ubuntu" ]; then
    apt-get update
    apt-get install -y zstd wget squashfs-tools
    apt-get clean
fi

cd $TARGET

# Get latest tag
if [ -z "$LABXDB_PYTHON_TAG" ]; then
    LABXDB_PYTHON_TAG=$(wget -qO- https://gitlab.com/api/v4/projects/19019522/repository/tags | cut -d '"' -f 4)
    echo "Found tag $LABXDB_PYTHON_TAG"
fi
wget --no-verbose "https://gitlab.com/vejnar/labxdb-python/-/archive/$LABXDB_PYTHON_TAG/labxdb-python-$LABXDB_PYTHON_TAG.tar.gz"
tar -x -z --strip-components=1 -f labxdb-python-$LABXDB_PYTHON_TAG.tar.gz

pip3 install --requirement requirements.txt --user .

echo "==> Install SRA tools"

wget --no-verbose https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/current/sratoolkit.current-ubuntu64.tar.gz
tar xvfz sratoolkit.current-ubuntu64.tar.gz
cp sratoolkit.*-ubuntu64/bin/fasterq-dump-orig* $HOME/.local/bin/fasterq-dump

echo "==> Configuration LabxDB-Python"

mkdir /etc/hts
cat << EOF > /etc/hts/labxdb.json
{
    "labxdb_http_url": "http://127.0.0.1:8081/",
    "labxdb_http_path_seq": "seq/",
    "labxdb_http_login": "",
    "labxdb_http_password": ""
}
EOF

cat << EOF > $TARGET/.bash_profile
[[ -f ~/.bashrc ]] && . ~/.bashrc
EOF

cat << EOF > $TARGET/.bashrc
export PATH=$PATH:$HOME/.local/bin
export HTS_CONFIG_PATH="/etc/hts"
EOF
