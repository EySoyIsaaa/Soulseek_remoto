#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/home/server/slskd/private-downloader"
VENV_DIR="$PROJECT_DIR/.venv"
SERVICE_FILE="/etc/systemd/system/private-downloader.service"
ENV_FILE="$PROJECT_DIR/.env"
USER_NAME="server"

cd "$PROJECT_DIR"
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r requirements.txt

if [[ ! -f "$ENV_FILE" ]]; then
  cat > "$ENV_FILE" <<EOF
PRIVATE_DOWNLOADER_TOKEN=cambia-este-token-largo
EOF
fi

sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Private Downloader FastAPI Service
After=network.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$PROJECT_DIR
EnvironmentFile=$ENV_FILE
ExecStart=$VENV_DIR/bin/uvicorn app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

chmod +x "$PROJECT_DIR/cleanup.sh"

(crontab -l 2>/dev/null | grep -v "cleanup.sh"; echo "*/5 * * * * $PROJECT_DIR/cleanup.sh") | crontab -

sudo systemctl daemon-reload
sudo systemctl enable private-downloader.service
sudo systemctl restart private-downloader.service

echo "Instalado. Edita $ENV_FILE para cambiar el token y luego: sudo systemctl restart private-downloader.service"
