#!/bin/bash
# Source environment variables for ObsidianVault ops scripts
set -a
source /var/www/zerodrop/.env
set +a
exec /home/ubuntu/bot/venv/bin/python3 "$@"
