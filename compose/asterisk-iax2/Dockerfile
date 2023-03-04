FROM alpine:latest

RUN apk add --no-cache \
        bash \
        asterisk \
        asterisk-curl \
        asterisk-fax \
        asterisk-odbc \
        asterisk-sample-config \
        asterisk-sounds-en \
        asterisk-sounds-moh \
        unzip \
	util-linux \
	vim \
        && echo "asterisk -rvvvvvv" > /usr/sbin/a && chmod +x /usr/sbin/a \
	&& echo "! installation is finished !"

RUN rm -fr /var/lib/asterisk/sounds/es && mkdir /var/lib/asterisk/sounds/es
ADD https://www.asterisksounds.org/sites/asterisksounds.org/files/sounds/es-MX/download/asterisk-sounds-core-es-MX-1.11.11.zip  /var/lib/asterisk/sounds/es/core.zip
ADD https://www.asterisksounds.org/sites/asterisksounds.org/files/sounds/es-MX/download/asterisk-sounds-extra-es-MX-1.12.11.zip /var/lib/asterisk/sounds/es/extra.zip
RUN unzip /var/lib/asterisk/sounds/es/core.zip -d /var/lib/asterisk/sounds/es && rm -fr /var/lib/asterisk/sounds/es/LICENSE.txt
RUN rm -fr /var/lib/asterisk/sounds/es/extra.zip /var/lib/asterisk/sounds/es/extra.zip
RUN chown asterisk:asterisk -R /var/lib/asterisk/sounds/es/ /etc/asterisk /var/lib/asterisk/moh
RUN mkdir /var/lib/asterisk/sounds/custom
WORKDIR /etc/asterisk
RUN apk add python3
CMD ["/usr/sbin/asterisk", "-d", "-f"]
