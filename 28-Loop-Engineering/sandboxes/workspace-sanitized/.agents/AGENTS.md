# Règles de la Sandbox Jetable

## Périmètre
- Ces règles ne s'appliquent QUE dans /sandboxes/workspace-sanitized.

## Auto-validation
- Auto-validation (always-proceed) activée pour les commandes shell internes, l'installation de dépendances et le refactoring.

## Interdits stricts
- Interdiction de lire/écrire hors de la sandbox.
- Interdiction de toute tentative d'accès réseau (l'isolation reste le garde-fou).
- Aucune écriture de secret en clair dans les fichiers du projet.

## Sortie
- Tout rapatriement vers l'hôte passe obligatoirement par `tesla-sandbox sync` (scan + diff + signature humaine). L'agent ne contourne jamais ce passage.
