# MVP 23 - Architecture Entr

## 1. Diagnostic
Le projet utilise `entr` pour l'orchestration des événements et le watching des fichiers dans le dépôt local (voir le `justfile`). L'objectif est d'isoler cette logique comme MVP d'orchestration.

## 2. Description
Ce projet contient le `justfile` de référence qui illustre la commande `watch` utilisant `entr` pour écouter les modifications des fichiers et déclencher le Capability Bus.

## 3. Preuve
- `justfile` inclus.
