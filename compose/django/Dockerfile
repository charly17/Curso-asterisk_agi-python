FROM python:3.9-alpine

ARG APP_HOME=/opt/Fastagi

RUN apk add --no-cache bash && apk add --update --no-cache supervisor && \
  mkdir -p /var/log/supervisor && \
  mkdir -p /etc/supervisor/conf.d

RUN pip install supervisor

RUN pip3 install virtualenv && python -m virtualenv /opt/virtualenv

ENV PATH="/opt/virtualenv/bin:$PATH"

RUN mkdir ${APP_HOME}

WORKDIR ${APP_HOME}

COPY ./requirements.txt ./requirements.txt

RUN /opt/virtualenv/bin/pip3 install -r ./requirements.txt

COPY ./daemon/supervisor.conf /etc/supervisor.conf

CMD ["supervisord", "-c", "/etc/supervisor.conf"]