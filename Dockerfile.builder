FROM centos:8.3.2011 as rpm_builder

RUN yum install -y \
        python3 \
        python3-devel \
        python3-pip \
        gcc \
        libffi-devel \
        openssl-devel

ADD requirements.txt /mnt/
RUN pip3 install -Ur /mnt/requirements.txt

ADD requirements.dev.txt /mnt/
RUN pip3 install -Ur /mnt/requirements.dev.txt

ADD . /mnt/src
RUN cd /mnt/src && \
    python3 setup.py bdist_rpm
