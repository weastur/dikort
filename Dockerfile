FROM alpine:3.13.1 as builder

RUN apk update && \
    apk add \
        python3 \
        python3-dev \
        py-pip \
        gcc \
        musl-dev \
        libffi-dev \
        openssl-dev \
        cargo

ADD requirements.txt /mnt/
RUN pip3 install -Ur /mnt/requirements.txt

ADD requirements.dev.txt /mnt/
RUN pip3 install -Ur /mnt/requirements.dev.txt

ADD . /mnt/src
RUN cd /mnt/src && \
    python3 setup.py bdist_wheel

FROM alpine:3.13.1 as cmd

RUN apk add --no-cache python3 py-pip git git-lfs

COPY --from=builder /mnt/src/dist/*.whl /

RUN pip3 install /*.whl

CMD ["dikort"]
