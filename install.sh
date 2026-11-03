#!/bin/sh
set -eu

if [ "$(id -u)" -ne 0 ]; then
  echo "Execute com sudo: sudo ./install.sh" >&2
  exit 1
fi

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

if ! id dragoncode >/dev/null 2>&1; then
  useradd --system --home /nonexistent --shell /usr/sbin/nologin dragoncode
fi

install -d -o root -g root -m 0755 /opt/dragonwilds-join-code/web
install -d -o root -g root -m 0755 /usr/local/libexec
install -o root -g root -m 0755 "$PROJECT_DIR/app.py" /opt/dragonwilds-join-code/app.py
install -o root -g root -m 0644 "$PROJECT_DIR/web/index.html" /opt/dragonwilds-join-code/web/index.html
install -o root -g root -m 0644 "$PROJECT_DIR/web/styles.css" /opt/dragonwilds-join-code/web/styles.css
install -o root -g root -m 0755 "$PROJECT_DIR/bin/dragonwilds-join-code" /usr/local/libexec/dragonwilds-join-code
install -o root -g root -m 0440 "$PROJECT_DIR/deploy/dragonwilds-join-code.sudoers" /etc/sudoers.d/dragonwilds-join-code
install -o root -g root -m 0644 "$PROJECT_DIR/deploy/dragonwilds-join-code.service" /etc/systemd/system/dragonwilds-join-code.service

visudo -cf /etc/sudoers.d/dragonwilds-join-code >/dev/null
systemctl daemon-reload
systemctl enable --now dragonwilds-join-code.service

echo "Instalado em http://127.0.0.1:8787"
echo "Use um proxy HTTPS para disponibilizar a página publicamente."
