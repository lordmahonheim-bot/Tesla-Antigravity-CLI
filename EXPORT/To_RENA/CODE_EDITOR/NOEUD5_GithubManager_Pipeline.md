> **ARCHIVE — remplacée pour le parcours sans Chrome (audit du 2026-09-19).**
> Les commandes, modèles, chiffres et certifications ci-dessous ne sont pas
> une procédure validée. Ne pas appliquer les changements système ni les
> exemples d’auto-exécution. Utiliser le [guide corrigé TERMINATOR](LIVRABLE_FINAL_AIStudio_Headless_Terminator.md).

# NŒUD 5 : Architecture du Pipeline Git & Rapatriement (Vigilum Codex)

## Objectif
Définir le flux de rapatriement du code depuis Google AI Studio (Cloud) vers le dépôt local de MIDGARD (`~/bifrost/tesla`), en assurant la traçabilité et le strict respect du Vigilum Codex.

## Architecture des Branches
L'architecture Git repose sur une structure temporelle et fonctionnelle :
- `main` : La branche principale, stable, déployable, et reflétant la version de production.
- `develop` : La branche d'intégration pour les nouvelles fonctionnalités avant passage sur `main`.
- `feature/ai-studio-*` : Branches éphémères dédiées au rapatriement du code généré depuis Google AI Studio.

## Flux de Rapatriement : Étapes Exactes

### 1. Préparation de l'environnement local
Avant chaque rapatriement, s'assurer que le dépôt local est à jour :
```bash
cd ~/bifrost/tesla
git checkout develop
git pull origin develop
```

### 2. Création de la branche de rapatriement
Créer une branche dédiée au prototype ou à la fonctionnalité issue du Cloud :
```bash
# Exemple pour un module d'interface
git checkout -b feature/ai-studio-[nom-fonctionnalite]
```

### 3. Intégration du Code (Cloud -> Local)
- Copier/télécharger les artefacts générés (scripts, modèles, configurations) depuis Google AI Studio.
- Placer les fichiers dans l'arborescence appropriée de `~/bifrost/tesla`.
- Ajouter les fichiers au suivi Git :
```bash
git add .
```

### 4. Application du Vigilum Codex (Conventional Commits)
Le Vigilum Codex impose l'utilisation de Conventional Commits pour garantir la lisibilité de l'historique et la génération automatique de changelogs.

Format de commit requis : `<type>[optional scope]: <description>`

Types autorisés :
- `feat` : Nouvelle fonctionnalité ou rapatriement de code IA majeur.
- `fix` : Correction de bug.
- `docs` : Mise à jour de la documentation.
- `refactor` : Restructuration du code sans ajout de fonctionnalité ni correction de bug.
- `chore` : Tâches de maintenance, mise à jour de dépendances.

Exemple de commit de rapatriement :
```bash
git commit -m "feat(cloud-sync): rapatriement du module depuis Google AI Studio"
```
*(Inclure des détails supplémentaires dans le corps du commit si nécessaire pour la traçabilité architecturale)*

### 5. Intégration Continue et Revue (Merge vers Develop)
Une fois le code validé localement :
```bash
git push origin feature/ai-studio-[nom-fonctionnalite]
```
- Créer une Merge/Pull Request de `feature/ai-studio-*` vers `develop`.
- Effectuer les revues de code et s'assurer que l'intégration fonctionne.
- Fusionner la PR et nettoyer la branche locale :
```bash
git checkout develop
git pull origin develop
git branch -d feature/ai-studio-[nom-fonctionnalite]
```

## Intégration dans le Plan d'Intervention Chronologique
Ce flux est conçu pour être une étape répétable (Nœud standard de rapatriement) dans la boucle itérative de développement avec l'IA. Chaque session de prototypage sur AI Studio déclenche ce pipeline de rapatriement, assurant que chaque incrément de valeur est capturé, versionné, et tracé conformément aux normes de gouvernance strictes de MIDGARD.
