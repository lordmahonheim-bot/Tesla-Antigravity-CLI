# voice_tesla_solution_2026-07-17.md
# Documentation Technique Complète — Pipeline Vocal VOICE-TESLA (MIDGARD)
**Chantier** : VOICE-TESLA | **Mission** : N4 (tesla-master-code)
**Date** : 2026-07-17 | **Statut** : Livraison complète

---

## Résumé Exécutif

Le pipeline vocal VOICE-TESLA est une solution **100% locale, zéro-cloud, FOSS** permettant à Lord Mahonheim d'interagir avec Antigravity CLI (`agy`) par la voix sur MIDGARD (Linux, X11/Wayland). Il repose sur `whisper-cli` (whisper.cpp) pour la transcription STT locale et `tmux` pour l'injection de commandes dans agy, avec un gate de confirmation obligatoire contre toute injection non désirée.

---

## Architecture Globale

```
[Raccourci Clavier : Caps_Lock ou Super+V]
         │
         ▼
  voice-tesla.sh
         │
    ┌────┴────────────────────────────────────┐
    │                                         │
    ▼                                         ▼
Détection audio                        Détection tmux
pw-record / arecord / rec              cherche session "agy"
    │
    ▼
Enregistrement WAV (16kHz, mono)
    │
    ▼
Vérification silence (< 1 Ko → abandon)
    │
    ▼
whisper-cli
  --model ggml-base.bin
  --language fr
  --entropy-thold 2.6
  --no-timestamps
    │
    ▼
Benchmark latence (alerte si > 7s)
    │
    ▼
Gate de Confirmation [O/R/A]
    │ (si O)
    ▼
tmux send-keys -t SESSION -l "$TEXT"
tmux send-keys -t SESSION Enter
    │
    ▼
Logging JSONL + trap cleanup
```

---

## Livrables Produits

### Structure des fichiers

```
/home/lord-mahonheim/bifrost/tesla/OUTPUTS/voice-tesla/
├── voice-tesla.sh             # Script principal pipeline vocal
├── voice-health-check.sh      # Smoke test 6 sections
├── voice-tesla-install.sh     # Installateur + guide raccourcis
└── VOICE_POLICY.md            # Gouvernance, KPI, décommissionnement
/home/lord-mahonheim/bifrost/tesla/OUTPUTS/
└── voice_tesla_solution_2026-07-17.md  # Ce document
```

### Inventaire des fichiers

| Fichier | Lignes | Rôle |
|---------|--------|------|
| `voice-tesla.sh` | ~340 | Pipeline principal (PTT→STT→Gate→tmux) |
| `voice-health-check.sh` | ~220 | Smoke test 6 sections |
| `voice-tesla-install.sh` | ~220 | Installation + guide configuration |
| `VOICE_POLICY.md` | ~220 | Gouvernance, KPI, bonnes pratiques |

---

## Fonctionnalités Implémentées

### voice-tesla.sh

| Fonctionnalité | Implémentation | Condition Premortem |
|----------------|----------------|---------------------|
| Détection audio auto | `detect_audio_backend()` : PipeWire→ALSA→SoX | — |
| Détection session tmux | `detect_tmux_session()` : grepping "agy" | — |
| Enregistrement WAV | `record_audio()` avec indication visuelle `🎙` | — |
| Anti-hallucination | `--entropy-thold 2.6 --no-timestamps` | — |
| Vérification silence | `check_silence()` : < 1024 octets → abandon | — |
| **Gate de confirmation** | `confirmation_gate()` : [O/R/A] + timeout 30s | **#1 (RPN 378)** |
| Injection tmux | `inject_tmux()` : `send-keys -l` + `Enter` | — |
| Benchmark latence | Mesure ms + alerte si > 7s | **#3** |
| Nettoyage audio | `trap cleanup EXIT INT TERM` | **#2** |
| Logging JSONL | `append_log()` : timestamp, texte, latence, action | — |
| Mode `--dry-run` | Flag dédié, aucune injection réelle | — |
| Flag `--model` | tiny/base/small via `resolve_model_path()` | — |

### voice-health-check.sh — 6 Sections

1. **whisper-cli** — Version + accessibilité
2. **Modèles Whisper** — Scan multi-chemins, taille affichée
3. **Backend Audio** — PipeWire/ALSA/SoX + liste périphériques
4. **tmux & Session AGY** — Détection + liste panes
5. **Benchmark Latence** — Transcription fichier test silence
6. **Répertoire Log** — Existence + comptage entrées

### voice-tesla-install.sh — 6 Phases

1. **Dépendances** — whisper-cli, tmux, audio, sox, bc, pactl
2. **Structure** — Création `~/.local/share/voice-tesla/` + `~/.local/bin/`
3. **Scripts** — Liens symlink + raccourci `vt`
4. **Modèle Whisper** — Détection + instructions téléchargement
5. **Raccourci Clavier** — Guide i3/Sway/GNOME/KDE/xbindkeys
6. **Test Final** — Lancement voice-health-check.sh

---

## Guide de Démarrage Rapide

```bash
# 1. Aller dans le répertoire des scripts
cd ~/bifrost/tesla/OUTPUTS/voice-tesla/

# 2. Rendre les scripts exécutables
chmod +x voice-tesla.sh voice-health-check.sh voice-tesla-install.sh

# 3. Lancer l'installation
bash voice-tesla-install.sh

# 4. Vérifier la santé de l'environnement
bash voice-health-check.sh

# 5. Test à sec (sans injection)
bash voice-tesla.sh --dry-run

# 6. Lancement standard (5 secondes d'écoute)
bash voice-tesla.sh

# 7. Avec session tmux agy existante
tmux new-session -s agy 'agy'
bash voice-tesla.sh
```

---

## Prérequis MIDGARD

| Logiciel | Statut | Notes |
|----------|--------|-------|
| `whisper-cli` | ✅ Déjà installé | Confirmé par Curator N2 |
| `ggml-base.bin` | ✅ Déjà présent | 142 Mo, confirmé |
| `tmux` | À vérifier | `which tmux` |
| `pw-record` / `arecord` | À vérifier | `pactl info` |

---

## Paramètres Whisper Anti-Hallucination

```bash
whisper-cli \
    --model ~/.local/share/whisper/ggml-base.bin \
    --language fr \
    --entropy-thold 2.6 \   # Rejette segments ambigus (anti-hallucination)
    --no-timestamps \        # Sortie texte brut uniquement
    --output-txt \           # Fichier .txt généré si stdout vide
    --file /tmp/voice-tesla-XXXXXX.wav
```

**Note** : `--entropy-thold 2.6` est le paramètre clé. À 2.6, Whisper abandonne un segment s'il est trop incertain (entropie haute = hallucination probable). La valeur par défaut Whisper est 2.4 — nous sommes légèrement plus permissifs pour le français.

---

## Chemins Recherchés pour les Modèles

Le script tente ces emplacements dans l'ordre :

```
~/.local/share/whisper/ggml-{model}.bin           ← PRIORITAIRE
~/.local/share/whisper.cpp/models/ggml-{model}.bin
/usr/share/whisper/ggml-{model}.bin
/usr/local/share/whisper/ggml-{model}.bin
~/whisper.cpp/models/ggml-{model}.bin
/opt/whisper/models/ggml-{model}.bin
```

Puis fallback `find` dans `$HOME` et `/usr/`.

---

## Format du Journal JSONL

```json
{"ts":"2026-07-17T12:34:56Z","text":"analyse le fichier main.py","latency_ms":2341,"action":"INJECTED","model":"base","dry_run":false}
{"ts":"2026-07-17T12:40:12Z","text":"[silence]","latency_ms":0,"action":"SILENCE","model":"base","dry_run":false}
{"ts":"2026-07-17T12:45:33Z","text":"supprime tout","latency_ms":1987,"action":"CANCELLED","model":"base","dry_run":false}
```

---

## Points de Vigilance pour Mahonheim

> [!WARNING]
> **Wayland + raccourcis clavier** : Si le WM ne peut pas exécuter le script dans un terminal visible, wrappez-le avec un émulateur terminal : `kitty bash voice-tesla.sh` ou `alacritty -e bash voice-tesla.sh`.

> [!CAUTION]
> **Gate de confirmation** : Le timeout est fixé à **30 secondes**. Sans réponse, le script annule automatiquement l'injection. Ne jamais désactiver ce gate même pour "gagner du temps".

> [!NOTE]
> **Commandes `agy --execute`** : Cette option N'EXISTE PAS dans Antigravity CLI. Le seul mécanisme d'injection validé est `tmux send-keys` (confirmé par Curator N2). Le script utilise exclusivement cette méthode.

> [!TIP]
> **Latence élevée** : Si la médiane dépasse 7s, passez à `--model tiny`. La précision baisse légèrement mais la latence tombe à 1-3s, ce qui est beaucoup plus confortable au quotidien.

> [!IMPORTANT]
> **Première exécution** : Lancez `voice-health-check.sh` AVANT le premier usage réel. Cela identifie immédiatement tout problème de configuration (modèle manquant, audio absent, session tmux).

---

## KPI d'Adoption (Résumé)

- **Seuil d'adoption** : ≥ 5 injections réussies / semaine
- **Période d'observation** : 4 semaines consécutives
- **Critère de décommissionnement** : < 5/semaine × 4 semaines
- **Journal de référence** : `~/.local/share/voice-tesla/voice_log.jsonl`
- **Rapport** : Script bash dans `VOICE_POLICY.md §4.2`

---

## Références Techniques

| Ressource | URL |
|-----------|-----|
| whisper.cpp | https://github.com/ggerganov/whisper.cpp |
| Modèles GGML | https://huggingface.co/ggerganov/whisper.cpp |
| PipeWire | https://pipewire.org |
| tmux | https://github.com/tmux/tmux |

---

*Document généré par tesla-master-code — Mission N4 VOICE-TESLA — 2026-07-17*
