
FROM ubuntu:22.04

ARG user=${user}

RUN apt update && \
    apt install -y git python3 python3-pip memcached && \
    service memcached restart && \
    groupadd -r $user && \
    useradd -m -r -g $user $user && \
    python3 -m pip install -U psycopg2-binary && \
    python3 -m pip install -U py4web

COPY requirements.txt .

RUN python3 -m pip install -U -r requirements.txt

USER $user

RUN cd /home/$user/ && py4web setup --yes apps

RUN chown $user -R /home/$user/apps
RUN chmod ug+rw -R /home/$user/apps

EXPOSE 8000

WORKDIR /home/$user/

CMD py4web run --password_file password.txt --host 0.0.0.0 --port 8000 apps
