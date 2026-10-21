#!/bin/bash
# Provisions the demo VM: installs uv, the project and the ML model, then
# runs the proxy as a systemd service. Safe to re-run with `vagrant provision`.
set -euo pipefail

APP_DIR=/opt/proxy
APP_USER=vagrant

# System packages
apt-get update -q
apt-get install -y -q curl ca-certificates rsync

# Install uv system-wide
if ! command -v uv >/dev/null; then
  curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh
fi

# Copy the code out of the shared folder, a native filesystem keeps the
# virtualenv and model working (VirtualBox shared folders break symlinks)
mkdir -p "$APP_DIR"
rsync -a --delete \
  --exclude .git --exclude .vagrant --exclude .venv \
  --exclude models --exclude test --exclude logs.txt \
  /vagrant/ "$APP_DIR"/
chown -R "$APP_USER:$APP_USER" "$APP_DIR"

# Install pinned dependencies (uv fetches Python 3.13) and download the model
sudo -u "$APP_USER" -H bash -c "cd $APP_DIR && uv sync --frozen"
sudo -u "$APP_USER" -H bash -c "cd $APP_DIR && uv run --no-sync python -c \
  'from lib.model import phishing_model; phishing_model.download_model()'"

# Run the proxy on boot
cat > /etc/systemd/system/phishing-proxy.service <<EOF
[Unit]
Description=Phishing Prevention Proxy
After=network-online.target
Wants=network-online.target

[Service]
User=$APP_USER
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/.venv/bin/mitmdump --listen-host 0.0.0.0 --listen-port 8080 -s lib/proxy_addon.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable phishing-proxy
systemctl restart phishing-proxy

echo "Proxy running at http://192.168.56.10:8080"
