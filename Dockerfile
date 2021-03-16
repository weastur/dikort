FROM python:3.9.2-alpine3.13

RUN apk add --no-cache git \
    && pip3 install dikort

ENTRYPOINT ["dikort"]
