FROM alpine:3.7

RUN apk add --update --no-cache -q --progress \
    python2 \
    py2-pip \
    py2-virtualenv \
    nodejs && \
    npm update -g npm && \
    rm -rf ~/.npm/

CMD ["/bin/sh"]
