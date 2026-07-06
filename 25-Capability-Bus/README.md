# MVP 25 - Capability Bus

## 1. Diagnostic
Nécessité de moduler les capacités du système via un bus capable de charger et d'exécuter des plugins en fonction d'événements.

## 2. Description
Le Capability Bus permet d'exécuter les plugins (capabilities) répertoriés dans `registry.json`.

## 3. Preuve
- Contient le `capability_dispatcher.sh`, `capability_resolver.sh` et les fichiers de configuration de `tools/capability_bus/`.
