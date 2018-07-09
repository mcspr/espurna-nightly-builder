FROM bitnami/minideb:stretch as goodies

FROM debian:buster-slim

COPY --from=0 /usr/sbin/install_packages /usr/sbin/install_packages

ENV DEBIAN_FRONTEND noninteractive

RUN groupadd --gid 1000 worker && \
    useradd \
        --uid 1000 \
        --gid worker \
        --shell /bin/bash \
        --create-home worker

RUN install_packages python-minimal libpython2.7-stdlib ca-certificates git xz-utils wget gnupg apt-transport-https && \
    wget https://bootstrap.pypa.io/get-pip.py && \
    python2.7 get-pip.py && \
    pip install virtualenv && \
    rm get-pip.py && \
    wget https://deb.nodesource.com/gpgkey/nodesource.gpg.key && \
    apt-key add nodesource.gpg.key && \
    rm nodesource.gpg.key && \
    echo "deb https://deb.nodesource.com/node_8.x buster main" > /etc/apt/sources.list.d/nodesource.list && \
    install_packages nodejs && \
    npm install -g npm && \
    apt-get purge --autoremove -q -y wget gnupg apt-transport-https

USER worker

CMD ["/bin/sh"]
