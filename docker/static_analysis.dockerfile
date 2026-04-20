FROM alpine

WORKDIR /opt

RUN apk add --update-cache cmake \
 && setup-apkrepos -c \
 && apk add --update-cache cppcheck py3-pylint
