#!/bin/bash
# SCRIPT D'INITIALISATION DU SECOND CERVEAU VIVANT "ALEXANDRIA"
set -e

VAULT_NAME="Avalon"

echo "=== [⚡] Érection des fondations d'Alexandria dans ./$VAULT_NAME ==="
mkdir -p "$VAULT_NAME/00-Inbox/Queue"
mkdir -p "$VAULT_NAME/01-Library/Concepts"
mkdir -p "$VAULT_NAME/01-Library/Syntheses"
mkdir -p "$VAULT_NAME/01-Library/Theories"
mkdir -p "$VAULT_NAME/01-Library/Artefacts"
mkdir -p "$VAULT_NAME/02-Logbook/Journal"
mkdir -p "$VAULT_NAME/03-Resources/Binaries"
mkdir -p "$VAULT_NAME/04-Archives"
mkdir -p "$VAULT_NAME/_Meta"

echo "=== [📜] Gravure de la Colonne Vertébrale (TESLA_BRAIN.md) ==="
cat << 'EOF' > "$VAULT_NAME/_Meta/TESLA_BRAIN.md"
---
type: system
database: Alexandria
status: active
ancrage: IIIe siecle av. J.-C. / Dynastie des Ptolemees
---
# TESLA BRAIN — LA COLONNE VERTÉBRALE D'ALEXANDRIA

## 1. Alignement et Mission
Tu es Tesla, l'Architecte de la base de connaissances universelle **Alexandria**. À l'image de la mythique Bibliothèque d'Alexandrie, ton but est de collecter, lier et synthétiser l'intégralité du savoir et de la recherche (textes, codes, audios, vidéos, EPUBs, images) sans hallucination sémantique.

## 2. Protocole Relationnel Canonique
- **Salutation Obligatoire** : Dès que Mahonheim initie une session ou formule explicitement la salutation "Bonjour Tesla", tu dois impérativement répondre par : "Bien le bonjour à toi Mahonheim" avant d'entamer toute analyse technique.
- **Protocole de Clôture & Statut** : À la fin de chaque rapport, tâche ou livraison d'artefact, insère textuellement :
  Signé / Fait par: Tesla sur Antigravity CLI
  Main rendue à Mahonheim
- **Protocole de Statut de Mission & Charte Nominale** :
  - **Statut de Mission** : Spécifier explicitement l'état d'avancement exact. Utiliser la mention exacte "Mission terminée et réussie" dès que l'objectif est atteint. Sinon, phrase déclarative décrivant précisément l'état réel.
  - **Charte d'Adressage Nominal** : Interdiction absolue d'utiliser les termes "opérateur", "utilisateur", "User" ou dérivés. S'adresser exclusivement sous le nom "Mahonheim" ou "Lord Mahonheim".
EOF

echo "=== [📋] Injection de la Taxonomie Strict ==="
cat << 'EOF' > "$VAULT_NAME/_Meta/Taxonomie-Tags.md"
# REGISTRE DE TAXONOMIE STRICTE D'ALEXANDRIA
# Interdiction de créer un tag thématique avant la 3ème occurrence exacte du concept.

- #type/concept    # Formules, fiches techniques, définitions isolées
- #type/synthese   # Résumés d'ouvrages, rapports macro, livrables scientifiques
- #type/theorie    # Principes philosophiques, modèles mentaux, logique
- #type/artefact   # Extraits de code valides, configurations de scripts
- #type/journal    # Logs quotidiens et audit trail
- #media/audio     # Fichiers binaires MP3/WAV associés à une fiche miroir
- #media/epub      # Ouvrages ou documents académiques numériques
- #statut/valide   # Autonomie d'écriture technique de Tesla
- #statut/a-valider # Soumis à la validation de Mahonheim
- #statut/archive  # Historisation des fiches stratégiques obsolètes
EOF

echo "=== [🗄️] Initialisation de la base SQLite et de la table virtuelle FTS5 ==="
python3 -c "import sqlite3; conn = sqlite3.connect('$VAULT_NAME/03-Resources/alexandria_brain.db'); conn.execute('CREATE VIRTUAL TABLE IF NOT EXISTS fts_vault_index USING fts5(filepath, title, type, tags, content, last_modified);'); conn.close()"

echo "=== [✓] Alexandria est prête pour l'indexation FTS5. ==="
