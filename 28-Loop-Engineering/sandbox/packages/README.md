# 📦 Dépôt Hors-Ligne — Semgrep & Dépendances

**Gardien :** Tesla (sur Antigravity CLI)  
**Date de constitution :** 2026-07-10  
**Doctrine :** Vigilum Codex — Sandbox Hermétique

---

## Contexte

Ce dossier constitue le **dépôt de packages Python hors-ligne** pour permettre l'installation
de Semgrep (outil SAST) et de toutes ses dépendances dans un environnement de sandbox **totalement
coupé d'Internet**.

Il fait partie de l'infrastructure de la boucle autonome de validation de code du chantier
**Loop Engineering** (chantier #009).

---

## Contenu

| Composant | Version | Type |
|---|---|---|
| **semgrep** | 1.157.0 | SAST — Analyse statique de sécurité |
| mcp | 1.23.3 | MCP Protocol |
| opentelemetry-sdk | 1.37.0 | Télémétrie |
| pydantic | 2.13.4 | Validation de données |
| rich | 15.0.0 | UI terminal |
| ruamel.yaml | 0.19.1 | Parser YAML |
| ... et ~60 dépendances | — | Toutes les dépendances transitives |

**Total :** 66 fichiers `.whl` / 71 Mo

---

## Utilisation

### Installation hors-ligne complète (depuis la sandbox)

```bash
pip install --no-index --find-links=/home/lord-mahonheim/bifrost/tesla/sandbox/packages/ semgrep
```

- `--no-index` : Interdit toute requête réseau vers PyPI
- `--find-links` : Redirige pip vers ce dépôt local

### Vérification d'intégrité (dry-run)

```bash
pip install --no-index --find-links=/home/lord-mahonheim/bifrost/tesla/sandbox/packages/ semgrep --dry-run
```

---

## Architecture & Compatibilité

| Paramètre | Valeur |
|---|---|
| OS | Linux (manylinux2014) |
| Architecture | x86_64 |
| Python | 3.12.x |
| Machine | MIDGARD |

---

## Mise à jour

Pour renouveler ce dépôt avec une version plus récente de Semgrep :

```bash
# Purger l'ancien dépôt
rm /home/lord-mahonheim/bifrost/tesla/sandbox/packages/*.whl

# Re-télécharger
.venv/bin/pip download semgrep --dest /home/lord-mahonheim/bifrost/tesla/sandbox/packages/
```

---
*Dépôt constitué par Tesla | Doctrine Vigilum Codex | Chantier Loop Engineering #009*
