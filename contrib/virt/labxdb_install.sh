#!/bin/bash

set -o errexit
set -o verbose

source /etc/os-release

echo "==> Install LabxDB"

if [ -e "/run/systemd/system" ]; then
    echo "systemd detected"
    SYSTEMD=true
else
    SYSTEMD=false
fi

# Set target
if [ -z "$TARGET" ]; then
    TARGET="/root/labxdb"
fi

if [ "$NAME" = "Arch Linux" ] ; then
    pacman -Sy --noconfirm python python-pip python-aiohttp python-asyncpg postgresql libxml2
    pip3 install aiohttp-jinja2
fi
if [ "$NAME" = "Debian GNU/Linux" ] || [ "$NAME" = "Ubuntu" ]; then
    apt-get update
    apt-get install -y python3 python3-setuptools python3-pip python3-aiohttp python3-asyncpg python3-aiohttp-jinja2 postgresql libxml2-utils
    apt-get clean
fi

if [ ! -d "$TARGET" ]; then
    mkdir $TARGET
fi

cd $TARGET

get_labxdb_version() {
    echo $(wget -O - -q https://git.sr.ht/~vejnar/LabxDB/refs/rss.xml | \
    xmllint --xpath '//item[1]/title/text()' rss.xml - 2> /dev/null)
}

# Get latest tag
if [ -z "$LABXDB_TAG" ]; then
    LABXDB_TAG="$(get_labxdb_version)"
    echo "Found tag $LABXDB_TAG"
fi
wget --no-verbose "https://git.sr.ht/~vejnar/LabxDB/archive/${LABXDB_TAG}.tar.gz"
tar -x -z --strip-components=1 -f $LABXDB_TAG.tar.gz

if [ "$NAME" = "Arch Linux" ] ; then
    chage -E -1 -M -1 postgres
    su - postgres -c "initdb --locale en_US.UTF-8 -E UTF8 -D '/var/lib/postgres/data'"
    systemctl enable --now postgresql
fi
if [ "$NAME" = "Debian GNU/Linux" ] || [ "$NAME" = "Ubuntu" ] ; then
    fpg=$(ls -1 /etc/postgresql/*/main/pg_hba.conf | sort | head -1)
    sed -i.bak 's/^local \(.\+\) peer/local \1 trust/' $fpg
    if [ "$SYSTEMD" = true ]; then
        systemctl restart postgresql
    else
       /etc/init.d/postgresql restart
    fi
fi

psql -U postgres -c "CREATE ROLE lab WITH LOGIN ENCRYPTED PASSWORD 'labxdb';"

cd contrib/databases/sql

./tpl_sql.py -s -a schema,fish -u postgres create_antibody_tables.sql

./tpl_sql.py -s -a schema,mutant -u postgres create_mutant_tables.sql
psql -U postgres -c "\COPY mutant.gene FROM '../data/mutant_gene.csv' DELIMITER ',' CSV HEADER; SELECT setval('mutant.gene_gene_id_seq', max(gene_id)) FROM mutant.gene;"
psql -U postgres -c "\COPY mutant.allele FROM '../data/mutant_allele.csv' DELIMITER ',' CSV HEADER; SELECT setval('mutant.allele_allele_id_seq', max(allele_id)) FROM mutant.allele;"
psql -U postgres -c "\COPY mutant.option FROM '../data/mutant_option.csv' DELIMITER ',' CSV HEADER; SELECT setval('mutant.option_option_id_seq', max(option_id)) FROM mutant.option;"

./tpl_sql.py -s -a schema,fish -u postgres create_fish_tables.sql

./tpl_sql.py -s -a schema,oligo -u postgres create_oligo_tables.sql
psql -U postgres -c "\COPY oligo.item FROM '../data/oligo.csv' DELIMITER ',' CSV HEADER; SELECT setval('oligo.item_item_id_seq', max(item_id)) FROM oligo.item;"
psql -U postgres -c "\COPY oligo.option FROM '../data/oligo_option.csv' DELIMITER ',' CSV HEADER; SELECT setval('oligo.option_option_id_seq', max(option_id)) FROM oligo.option;"

./tpl_sql.py -s -a schema,purchase -u postgres create_order_tables.sql
psql -U postgres -c "\COPY purchase.item FROM '../data/order.csv' DELIMITER ',' CSV HEADER; SELECT setval('purchase.item_item_id_seq', max(item_id)) FROM purchase.item;"
psql -U postgres -c "\COPY purchase.option FROM '../data/order_option.csv' DELIMITER ',' CSV HEADER; SELECT setval('purchase.option_option_id_seq', max(option_id)) FROM purchase.option;"

./tpl_sql.py -s -a schema,plasmid -u postgres create_plasmid_tables.sql
psql -U postgres -c "\COPY plasmid.item FROM '../data/plasmid.csv' DELIMITER ',' CSV HEADER; SELECT setval('plasmid.item_item_id_seq', max(item_id)) FROM plasmid.item;"

./tpl_sql.py -s -a schema,seq -u postgres create_seq_tables.sql
psql -U postgres -c "\COPY seq.project FROM '../data/seq_project.csv' DELIMITER ',' CSV HEADER; SELECT setval('seq.project_project_id_seq', max(project_id)) FROM seq.project;"
psql -U postgres -c "\COPY seq.sample FROM '../data/seq_sample.csv' DELIMITER ',' CSV HEADER; SELECT setval('seq.sample_sample_id_seq', max(sample_id)) FROM seq.sample;"
psql -U postgres -c "\COPY seq.replicate FROM '../data/seq_replicate.csv' DELIMITER ',' CSV HEADER; SELECT setval('seq.replicate_replicate_id_seq', max(replicate_id)) FROM seq.replicate;"
psql -U postgres -c "\COPY seq.run FROM '../data/seq_run.csv' DELIMITER ',' CSV HEADER; SELECT setval('seq.run_run_id_seq', max(run_id)) FROM seq.run;"
psql -U postgres -c "\COPY seq.option FROM '../data/seq_option.csv' DELIMITER ',' CSV HEADER; SELECT setval('seq.option_option_id_seq', max(option_id)) FROM seq.option;"

# Only if systemd is installed
if [ "$SYSTEMD" = true ]; then
    cat << EOF > /etc/systemd/system/http_labxdb.service
[Unit]
Description=http LabxDB service
After=postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=/root/labxdb
ExecStart=/root/labxdb/app.py --port=8081 --db_host=localhost --db_user=lab --db_password="labxdb" --db_name=postgres --db_conn=2
Restart=always
StandardOutput=null
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    systemctl enable --now http_labxdb
fi
