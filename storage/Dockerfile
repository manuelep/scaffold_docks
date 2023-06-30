FROM postgis/postgis:14-master

COPY ./entrypoint.sh /docker-entrypoint-initdb.d/initdb.sh
RUN chmod +x /docker-entrypoint-initdb.d/initdb.sh
