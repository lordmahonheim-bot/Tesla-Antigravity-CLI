# VOICE_POLICY.md — Gouvernance du Pipeline Vocal VOICE-TESLA
**Version** : 1.0.0 | **Chantier** : VOICE-TESLA | **Date** : 2026-07-17
**Opérateur** : Lord Mahonheim (MIDGARD) | **Statut** : Actif

---

## 1. Architecture de la Solution

### 1.1 Schéma du Pipeline

```
[Raccourci Clavier]
      │
      ▼
[voice-tesla.sh]
      │
      ├─► [Détection Audio] ──► pw-record (PipeWire) OU arecord (ALSA) OU rec (SoX)
      │         │
      │         ▼
      │   [Fichier WAV tmp] ──► vérification taille (seuil 1 Ko)
      │         │
      │         ▼
      ├─► [whisper-cli] ──► modèle GGML local (ggml-base.bin)
      │         │
      │         ▼
      │   [Transcription FR] ──► entropy-thold 2.6 + no-timestamps
      │         │
      │         ▼
      ├─► [GATE DE CONFIRMATION] ──► OK / Rééditier / Annuler
      │         │ (OK seulement)
      │         ▼
      └─► [tmux send-keys] ──► Session agy
                │
                ▼
         [Logging JSONL] ──► ~/.local/share/voice-tesla/voice_log.jsonl
```

### 1.2 Composants Techniques

| Composant | Technologie | Rôle | Fallback |
|-----------|-------------|------|----------|
| Capture audio | pw-record (PipeWire) | Enregistrement WAV 16kHz mono | arecord → rec (SoX) |
| Transcription | whisper-cli (whisper.cpp) | STT local FR | Modèle tiny si base trop lent |
| Injection | tmux send-keys -l | Envoi commande à agy | Mode dry-run |
| Logging | JSONL | Traçabilité toutes invocations | Toujours actif |

### 1.3 Compatibilité

| Environnement | Statut | Notes |
|---------------|--------|-------|
| X11 | ✅ | Pleinement compatible |
| Wayland (natif) | ✅ | Via tmux uniquement (xdotool exclu) |
| i3wm / Sway | ✅ | bindsym natif |
| GNOME | ✅ | Custom shortcuts |
| KDE Plasma | ✅ | System Settings shortcuts |

---

## 2. Sécurité et Contraintes Opérationnelles

### 2.1 Invariants de Sécurité (Premortem)

> [!CAUTION]
> **RÈGLE ABSOLUE** : Aucune commande n'est injectée dans agy sans confirmation explicite de l'opérateur.

| Règle | Description | Implémentation |
|-------|-------------|----------------|
| **Gate de Confirmation** | Affichage du texte transcrit + choix OK/Rééditier/Annuler | `confirmation_gate()` avec timeout 30s |
| **Nettoyage audio** | Les fichiers WAV temporaires sont détruits à chaque fin d'exécution | `trap cleanup EXIT INT TERM` |
| **Détection silence** | Fichier < 1 Ko → abandon propre sans transcription | `check_silence()` |
| **Anti-hallucination** | `--entropy-thold 2.6` réduit les artefacts Whisper sur silence | Paramètre whisper-cli |
| **Zéro cloud** | Toute transcription est 100% locale | whisper-cli + modèle GGML local |
| **Zéro réseau** | Aucun appel réseau à aucun moment | Architecture FOSS offline |

### 2.2 Timeout et Limites

- **Confirmation gate** : timeout automatique 30s → Annulation
- **Durée d'enregistrement** : défaut 5s, max recommandé 30s
- **Fichiers temporaires** : préfixe `/tmp/voice-tesla-*`, durée de vie = session script

---

## 3. Performances et Modèles

### 3.1 Benchmarks Estimés (CPU, base installé)

| Modèle | RAM | Latence transcription | Précision FR | Recommandation |
|--------|-----|-----------------------|--------------|----------------|
| `tiny` | ~75 Mo | 1-3s | Bonne | Machines lentes (<4 cœurs) |
| `base` | ~142 Mo | 2-5s | Très bonne | **Défaut MIDGARD** |
| `small` | ~466 Mo | 5-10s | Excellente | Si base insuffisant |

**Latence pipeline totale estimée** : 2-5s (transcription) + 1s (enregistrement réponse) = **4-7s**

### 3.2 Seuil d'Alerte

Si la médiane de latence de transcription dépasse **7 secondes**, le script émet un avertissement automatique et recommande de passer au modèle `tiny`.

---

## 4. KPI d'Adoption (Condition Premortem #5)

### 4.1 Métriques de Suivi

Le journal `~/.local/share/voice-tesla/voice_log.jsonl` est la source de vérité des métriques.

**Format d'entrée :**
```json
{"ts":"2026-07-17T12:34:56Z","text":"commande transcrite","latency_ms":2341,"action":"INJECTED","model":"base","dry_run":false}
```

**Actions possibles :**
- `INJECTED` — Commande envoyée à agy avec succès
- `CANCELLED` — Refusé par l'opérateur au gate de confirmation
- `SILENCE` — Fichier audio trop petit, abandon propre
- `EMPTY` — Transcription vide
- `UNKNOWN` — Action imprévue

### 4.2 Script de Rapport Hebdomadaire

```bash
# Rapport KPI semaine N (à exécuter chaque lundi)
LOG="${HOME}/.local/share/voice-tesla/voice_log.jsonl"

echo "=== RAPPORT KPI VOICE-TESLA — $(date '+%Y-W%V') ==="
echo ""
echo "Invocations totales :"
wc -l < "$LOG"
echo ""
echo "Injections réussies :"
grep '"action":"INJECTED"' "$LOG" | wc -l
echo ""
echo "Annulations au gate :"
grep '"action":"CANCELLED"' "$LOG" | wc -l
echo ""
echo "Détections de silence :"
grep '"action":"SILENCE"' "$LOG" | wc -l
echo ""
echo "Latence moyenne (ms) :"
grep '"action":"INJECTED"' "$LOG" | \
  python3 -c "import sys,json; data=[json.loads(l) for l in sys.stdin]; \
  print(sum(d['latency_ms'] for d in data)//len(data) if data else 'N/A')"
echo ""
```

### 4.3 Seuil de Décommissionnement

> [!WARNING]
> **Règle de décommissionnement automatique** : Si le nombre d'invocations `INJECTED` est inférieur à **5 par semaine pendant 4 semaines consécutives**, le pipeline est considéré en abandon et doit être formellement désactivé.

**Procédure de vérification hebdomadaire :**

```bash
# Compter les injections de la semaine
WEEK_START=$(date -d 'last monday' '+%Y-%m-%d')
grep '"action":"INJECTED"' ~/.local/share/voice-tesla/voice_log.jsonl | \
  awk -F'"ts":"' '{print $2}' | cut -c1-10 | \
  awk -v w="$WEEK_START" '$1 >= w' | wc -l
```

---

## 5. Procédure de Décommissionnement

> [!IMPORTANT]
> Le décommissionnement est une décision formelle qui doit être documentée dans `Gestion-de-Chantiers/INDEX.md`.

### 5.1 Déclencheurs

- ☐ < 5 injections/semaine × 4 semaines consécutives (critère automatique)
- ☐ Latence médiane > 12s sur 30 jours
- ☐ Décision opérateur (Lord Mahonheim)
- ☐ Obsolescence de whisper.cpp

### 5.2 Étapes de Décommissionnement

```bash
# Étape 1 : Archiver le journal de logs
cp ~/.local/share/voice-tesla/voice_log.jsonl \
   ~/bifrost/tesla/OUTPUTS/voice-tesla/voice_log_ARCHIVE_$(date +%Y%m%d).jsonl

# Étape 2 : Supprimer les liens symboliques
rm -f ~/.local/bin/voice-tesla
rm -f ~/.local/bin/voice-health
rm -f ~/.local/bin/vt

# Étape 3 : Supprimer le raccourci clavier
# (Manuel selon WM : i3/Sway/GNOME/KDE — retirer le bindsym ou custom shortcut)

# Étape 4 : Optionnel — conserver les modèles whisper pour usage futur
# Les modèles GGML sont réutilisables pour d'autres projets STT

# Étape 5 : Mettre à jour INDEX.md
# Statut → 🔴 Archivé | Date d'archivage | Motif
```

### 5.3 Conservation des Données

| Ressource | Action | Justification |
|-----------|--------|---------------|
| `voice_log.jsonl` | Archiver | Traçabilité historique |
| Modèles GGML | Conserver | Réutilisables |
| Scripts `.sh` | Archiver dans OUTPUTS | Référence future |
| Raccourcis clavier | Supprimer | Libérer les touches |

---

## 6. Bonnes Pratiques d'Usage

### 6.1 Environnement Sonore

> [!TIP]
> La qualité de transcription dépend directement du rapport signal/bruit de l'environnement.

- **Idéal** : Environnement silencieux, microphone orienté vers la bouche, < 60 dB ambiant
- **Acceptable** : Bruit de fond uniforme (ventilation), < 70 dB
- **À éviter** : Musique, TV, voix multiples simultanées
- **Distance microphone** : 15-30 cm recommandés

### 6.2 Durée et Formulation

| Paramètre | Recommandation |
|-----------|----------------|
| Durée d'enregistrement | 3-8 secondes pour une commande simple |
| Formulation | Phrases directes, pas de hésitations prolongées |
| Langue | Français standard (paramètre `--language fr`) |
| Commandes dangereuses | Toujours vérifier au gate de confirmation |

### 6.3 Commandes Recommandées pour agy

```bash
# Usage type — à prononcer clairement :
"Montre-moi l'état du projet"
"Analyse le fichier voice-tesla.sh"
"Quel est le résumé de ma session"
"Crée un nouveau fichier nommé test.md"
"Lance le health check"
```

### 6.4 Gestion des Erreurs Courantes

| Symptôme | Cause probable | Solution |
|----------|----------------|----------|
| Transcription vide | Microphone non détecté | `pactl list sources short` pour vérifier |
| Hallucinations fréquentes | Bruit de fond | Augmenter `--entropy-thold` à 3.0 |
| Latence > 7s | Modèle trop lourd | Passer à `--model tiny` |
| Session tmux introuvable | Session fermée | `tmux new-session -s agy 'agy'` |
| Injection double | Race condition tmux | Ajouter `sleep 0.2` dans `inject_tmux()` |

---

## 7. Historique des Versions

| Version | Date | Auteur | Changements |
|---------|------|--------|-------------|
| 1.0.0 | 2026-07-17 | tesla-master-code | Version initiale — Pipeline complet MIDGARD |

---

## 8. Références

- **Chantier** : VOICE-TESLA (Gestion-de-Chantiers/)
- **Synthèse N1** : tesla-arcanis-360 (Deep Research chaîne optimale)
- **Synthèse N2** : tesla-curator-prime (Audit & correction erreurs)
- **Synthèse N3** : premortem (5 conditions GO + RPN critique)
- **whisper.cpp** : https://github.com/ggerganov/whisper.cpp
- **Modèles GGML** : https://huggingface.co/ggerganov/whisper.cpp
