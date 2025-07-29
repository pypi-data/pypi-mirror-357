#!/bin/bash
# cron_launcher.sh – Lance runner.py tous les jours à 9h

# Absolu path vers le runner (ajustable)
SCRIPT_PATH="$(dirname "$(realpath "$0")")/affiliate_ai/runner.py"

# Log file (facultatif)
LOGFILE="$(dirname "$(realpath "$0")")/affiliate_ai/logs/cron.log"
mkdir -p "$(dirname "$LOGFILE")"

# Ajouter cette ligne à crontab (manuellement) :
# 0 9 * * * /bin/bash /chemin/vers/cron_launcher.sh >> /chemin/vers/cron.log 2>&1

echo "⏰ $(date) - Lancement IA automatique"
python3 "$SCRIPT_PATH"
