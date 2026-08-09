# Avalon Refactor Plan : Spécifications Techniques et Mitigations

**Date :** 2026-07-20
**Auteur :** Tesla-Arcanis-360
**Cible :** Master-Code (pour implémentation Python)

Ce document fusionne les spécifications architecturales d'Avalon (TASLB), les mitigations de risques du rapport Premortem, et les directives de sécurité de manipulation de fichiers issues de Web-Raider. Il sert de cahier des charges technique définitif pour la réécriture des scripts d'ingestion Obsidian.

---

## 1. Directives de Manipulation Obsidian (Web-Raider & Premortem)

Pour éviter toute corruption de la base documentaire Obsidian lors de l'exécution des scripts :
1. **Manipulation YAML Sécurisée :** Le script doit utiliser la bibliothèque `python-frontmatter` pour lire et modifier le Frontmatter sans casser le contenu Markdown sous-jacent.
2. **Encodage Strict :** Tous les fichiers doivent être ouverts et sauvegardés avec `encoding="utf-8"`.
3. **Échappement des Wikilinks :** Tout lien interne Obsidian présent dans l'en-tête YAML doit **obligatoirement** être entouré de guillemets doubles. Exemple : `connections: ["[[Nom de la note]]"]`. Le non-respect corrompt le parseur d'Obsidian.
4. **Fichier `graph.json` :** La modification du fichier `.obsidian/graph.json` (pour la colorimétrie dynamique) ne doit s'opérer que si le fichier n'est pas verrouillé, et idéalement quand Obsidian est fermé.

## 2. Normes Topologiques et Métadonnées (Frontmatter)

Chaque nouveau nœud (entité, projet, concept) créé par le script doit se voir injecter ce bloc YAML standard :

```yaml
---
type: "entity | project | session_log | concept"
status: "active | archive | draft"
tags: 
  - "#vigilum-codex/[categorie]"
  - "#[domaine_technique]"
aliases: ["Nom_Alternatif", "Acronyme"]
date_created: "YYYY-MM-DD"
connections:
  - "[[Autre_Entite]]"
---
```
**Contraintes :**
- Aucune création de "nœuds vides" (placeholders). Un nœud n'est créé que s'il est alimenté par un contenu sémantique substantiel.
- La limite de profondeur (Depth Limit) du graphe pour la génération de contexte RAG est bridée à **Depth=2**.

## 3. Implémentation : `session_to_graph.py` (L'ETL)

Le script d'ingestion NLP doit corriger les failles critiques d'OOM et de pertes de données identifiées.

**Fonctions à implémenter :**
- **Découpage de Contexte (Chunking) :** Ne plus envoyer le contenu brut des transcripts en bloc vers Gemini. Le script doit "chunker" les textes lourds avant l'inférence pour éviter le dépassement de la fenêtre de tokens et les crashes mémoire (OOM).
- **Rate-Limiting (Backoff) :** L'itération sur la liste des fichiers à traiter doit inclure une temporisation (`time.sleep`) ou un backoff exponentiel pour esquiver l'erreur API `429 Too Many Requests`.
- **Fusion et Déduplication (Append Mode) :** Lors de l'extraction des nœuds :
  - Le script doit vérifier la présence d'alias dans les nœuds existants pour éviter les doublons (Anti-Semantic Bloat).
  - Si un fichier `Nom_Du_Sujet.md` existe déjà, **il ne doit jamais être écrasé**. Le script doit y faire un *Append* (fusion) en ajoutant une section du type `## Historique : [[Daily_Log_YYYY-MM-DD]]`.
- **Maillage :** Injecter des wikilinks natifs `[[...]]` dans les corps de texte pour chaque entité reconnue.

## 4. Implémentation : `generate_daily_log.py` (Le Journalier)

Le script de log quotidien a révélé des comportements destructeurs qui doivent être corrigés :
- **Mode d'Écriture Sécurisé :** Les logs journaliers (`Daily_Log_YYYY-MM-DD.md`) doivent être ouverts en mode Ajout (`'a'`) ou faire l'objet d'une mise à jour intelligente afin de préserver l'historique si l'ETL tourne plusieurs fois dans la même journée.
- **Reporting des Métriques (Tracking) :** Le comptage du script actuel est erroné (il compte l'historique complet). Il doit être modifié pour ne reporter **que le delta** exact (le nombre précis de nouveaux fichiers/transcripts ingérés *aujourd'hui*).

## 5. Résumé des Tâches pour Master-Code

1. Mettre à jour `requirements.txt` avec `python-frontmatter`.
2. Refactoriser `session_to_graph.py` : Ajouter Chunking, Rate-Limiting, et Fusion au lieu d'Écrasement.
3. Refactoriser `generate_daily_log.py` : Mode ajout (`a`) et correctif du delta tracker.
4. S'assurer que tous les scripts qui manipulent le Markdown forcent `utf-8` et valident la syntaxe stricte des guillemets sur les liens YAML.
