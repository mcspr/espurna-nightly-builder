FROM bitnami/minideb:stretch as installer

FROM debian:buster-slim as ghr

COPY --from=installer /usr/sbin/install_packages /usr/sbin/install_packages
ARG GO_VERSION=1.11
ARG GO_SHA256=b3fcf280ff86558e0559e185b601c9eade0fd24c900b4c63cd14d1d38613e499
ADD "https://golang.org/dl/go${GO_VERSION}.linux-amd64.tar.gz" go.tar.gz
RUN echo "${GO_SHA256} go.tar.gz" | sha256sum -c -
RUN install_packages git ca-certificates g++ gcc libc6-dev make pkg-config && \
    tar -C /usr/local -xzf go.tar.gz && \
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

RUN install_packages python2-minimal python-setuptools ca-certificates git xz-utils wget gnupg apt-transport-https && \
    python2.7 -measy_install pip && \
    pip install virtualenv && \
    wget https://deb.nodesource.com/gpgkey/nodesource.gpg.key && \
    apt-key add nodesource.gpg.key && \
    rm nodesource.gpg.key && \
    echo "deb https://deb.nodesource.com/node_8.x buster main" > /etc/apt/sources.list.d/nodesource.list && \
    install_packages nodejs && \
    npm install -g npm && \
    apt-get purge --autoremove -q -y wget gnupg apt-transport-https

USER worker

CMD ["/bin/sh"]
