FROM debian:stable

SHELL ["/bin/bash", "-c"]

RUN apt-get update && \
    apt-get install -y wget && \
    bash <(wget -qO- https://gitlab.com/vejnar/labxdb/-/raw/master/contrib/virt/labxdb_install.sh)

EXPOSE 8081

WORKDIR /root/labxdb

CMD /etc/init.d/postgresql start && \
    /root/labxdb/app.py --port=8081 --db_host=localhost --db_user=lab --db_password="labxdb" --db_name=postgres --db_conn=2
