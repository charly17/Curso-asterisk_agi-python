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

RUN mkdir /var/lib/asterisk/sounds/custom
WORKDIR /etc/asterisk
RUN apk add python3
CMD ["/usr/sbin/asterisk", "-d", "-f"]
