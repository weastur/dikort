FROM alpine:3.13.1

RUN --mount=source=.,target=/dikort \
    cd /dikort / \
    && apk add --no-cache \
        python3 \
        py-pip \
        git \
    && pip3 install . \
    && apk del py-pip

CMD ["dikort"]
