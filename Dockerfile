FROM debian:bullseye-20220801-slim@sha256:139a42fa3bde3e5bad6ae912aaaf2103565558a7a73afe6ce6ceed6e46a6e519

RUN apt-get update && apt-get install -y aptly gnupg2 python3 python3-apt && rm -rf /var/lib/apt/lists/*

VOLUME /var/lib/aptly-api

RUN useradd -r -s /bin/false -u 101 -d /var/lib/aptly-api aptly

USER 101
ENV GPG_TTY=/dev/tty

WORKDIR /var/lib/aptly-api
COPY remove-old-packages.py /remove-old-packages.py

CMD ["aptly","api","serve","-listen","unix:/tmp/aptly/aptly-api.sock","-no-lock"]
