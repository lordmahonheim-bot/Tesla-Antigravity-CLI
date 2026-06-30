#!/bin/bash
# alexandria_backup.sh - Sauvegarde non bloquante de la base Alexandria
# Cron : 0 3 * * * /home/lord-mahonheim/bifrost/tesla/tools/alexandria_backup.sh

DB_PATH="/home/lord-mahonheim/bifrost/tesla/Avalon/03-Resources/alexandria_brain.db"
BACKUP_DIR="/home/lord-mahonheim/bifrost/backups/alexandria"
DATE=$(date +%Y%m%d)

mkdir -p "$BACKUP_DIR"

# Verifier l'integrite avant backup
INTEGRITY=$(sqlite3 "$DB_PATH" "PRAGMA integrity_check;" 2>/dev/null)
if [ "$INTEGRITY" != "ok" ]; then
    echo "[CRITICAL] Base Alexandria corrompue ! Integrity check: $INTEGRITY"
    exit 1
fi

# Backup via VACUUM INTO (ne verrouille pas la base en lecture)
sqlite3 "$DB_PATH" "VACUUM INTO '$BACKUP_DIR/alexandria_$DATE.db';"

# Conserver les 7 derniers backups uniquement
ls -t "$BACKUP_DIR"/alexandria_*.db | tail -n +8 | xargs -r rm

echo "[OK] Backup Alexandria termine : alexandria_$DATE.db"
