FROM python:3.9.6-alpine3.13

RUN apk add --no-cache git \
    && pip3 install dikort==0.2.1

ENTRYPOINT ["dikort"]
