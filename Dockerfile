FROM bitnami/minideb:stretch as installer

FROM debian:buster-slim as ghr

COPY --from=installer /usr/sbin/install_packages /usr/sbin/install_packages
RUN install_packages git wget ca-certificates g++ gcc libc6-dev make pkg-config && \
    wget -O go.tgz "https://golang.org/dl/go1.10.3.linux-amd64.tar.gz" && \
    tar -C /usr/local -xzf go.tgz && \
    mkdir -p /go/src /go/bin && chmod -R 777 /go && \
    GOPATH=/go /usr/local/go/bin/go get -u github.com/tcnksm/ghr

FROM debian:buster-slim

ENV DEBIAN_FRONTEND noninteractive

COPY --from=ghr /go/bin/ghr /usr/sbin/ghr
COPY --from=installer /usr/sbin/install_packages /usr/sbin/install_packages

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
