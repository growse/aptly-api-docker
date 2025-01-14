FROM debian:bookworm-20250113-slim

RUN --mount=type=cache,target=/var/cache/apt apt-get update && apt-get install --no-install-recommends -y aptly gnupg2 python3 python3-apt python3-tqdm vim && rm -rf /var/lib/apt/lists/*

VOLUME /var/lib/aptly-api

RUN useradd -r -s /bin/false -u 101 -d /var/lib/aptly-api aptly
RUN ln -s /var/lib/aptly-api/.aptly.conf /etc/aptly.conf

ENV GPG_TTY=/dev/tty

WORKDIR /var/lib/aptly-api
COPY remove-old-packages.py /remove-old-packages.py
RUN chmod +x /remove-old-packages.py

USER 101

CMD ["aptly","api","serve","-listen","unix:/tmp/aptly/aptly-api.sock","-no-lock"]
