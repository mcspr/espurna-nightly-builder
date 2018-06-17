FROM bitnami/minideb:stretch

RUN DEBIAN_FRONTEND=noninteractive apt-get update -q && \
    apt-get install -q -y python2.7-minimal git wget gnupg apt-transport-https && \
    wget https://bootstrap.pypa.io/get-pip.py && \
    python2.7 get-pip.py && \
    pip install virtualenv && \
    rm get-pip.py && \
    wget https://deb.nodesource.com/gpgkey/nodesource.gpg.key && \
    apt-key add nodesource.gpg.key && \
    rm nodesource.gpg.key && \
    echo "deb https://deb.nodesource.com/node_8.x stretch main" > /etc/apt/sources.list.d/nodesource.list && \
    apt-get update -q && \
    apt-get install -y nodejs && \
    npm update -g npm && \
    apt-get purge --autoremove -q -y curl apt-transport-https gnupg && \
    apt-get clean

CMD ["/bin/sh"]
