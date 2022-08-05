FROM debian:bullseye-20220801-slim@sha256:139a42fa3bde3e5bad6ae912aaaf2103565558a7a73afe6ce6ceed6e46a6e519

RUN apt-get update && apt-get install -y aptly gnupg2 && rm -rf /var/lib/apt/lists/*

VOLUME /var/lib/aptly-api
USER 101
ENV GPG_TTY=/dev/tty

CMD ["aptly", "api", "serve", "listen"]