FROM ubuntu:21.04
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install python3 python3-pip desktop-file-utils -y

COPY . /create_package
WORKDIR /create_package

ENTRYPOINT ["bash", "entrypoint.sh"]