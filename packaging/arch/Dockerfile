FROM archlinux:base

RUN pacman -Sy

RUN pacman -S --needed --noconfirm sudo python3 base-devel

RUN useradd builduser -m
RUN passwd -d builduser
RUN printf 'builduser ALL=(ALL) ALL\n' | tee -a /etc/sudoers
RUN su builduser

COPY . /create_package
WORKDIR /create_package
CMD sudo -su python3 create_arch_package.py