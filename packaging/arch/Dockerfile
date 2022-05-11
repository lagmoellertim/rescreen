FROM archlinux:base
RUN pacman -Sy --needed --noconfirm python3 python-wheel python-setuptools base-devel desktop-file-utils

COPY . /create_package
WORKDIR /create_package

RUN useradd builder -m
RUN echo "builder ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

ENTRYPOINT ["bash", "entrypoint.sh"]