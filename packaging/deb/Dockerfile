FROM ubuntu:21.04
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install python3 python3-pip desktop-file-utils -y

RUN useradd builduser -m
RUN passwd -d builduser
RUN printf 'builduser ALL=(ALL) ALL\n' | tee -a /etc/sudoers

USER builduser

COPY . /create_package
WORKDIR /create_package

ENTRYPOINT ["python3", "create_deb_package.py"]