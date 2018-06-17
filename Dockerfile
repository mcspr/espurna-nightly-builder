FROM python:2.7-stretch

RUN DEBIAN_FRONTEND=noninteractive apt-get update -q && \
    apt-get install -q -y curl apt-transport-https && \
    curl -sSO https://deb.nodesource.com/gpgkey/nodesource.gpg.key && \
    apt-key add nodesource.gpg.key && \
    echo "deb https://deb.nodesource.com/node_8.x stretch main" > /etc/apt/sources.list.d/nodesource.list && \
    apt-get update -q && \
    apt-get install -y nodejs

CMD ["/bin/bash"]
