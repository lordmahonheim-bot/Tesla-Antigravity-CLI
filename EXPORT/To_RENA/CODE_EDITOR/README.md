# CODE_EDITOR — intégration Tesla, Gemini et MIDGARD

**Point d'entrée maintenu : parcours TERMINATOR, sans Chrome.**

1. [Guide d'exploitation corrigé](LIVRABLE_FINAL_AIStudio_Headless_Terminator.md)
2. [Audit, corrections et limites de validation](AUDIT_AIStudio_MIDGARD_2026-09-19.md)
3. [Configuration TERMINATOR indépendante](templates/terminator-headless.config)
4. [Bridge Python exécutable](../../../tools/tesla_ai.py)
5. [Passerelle SPARK en lecture seule](../../../58-Spark-MCP-Gateway/README.md)

Depuis la racine du dépôt :

```bash
python3 tools/tesla_ai.py doctor
python3 -m unittest discover -s tests -p test_tesla_ai.py -v
```

Le diagnostic et les tests du bridge fonctionnent sans clé, navigateur ni paquet
Python externe. Le client cloud exige ensuite un consentement explicite et une
clé locale ; il ne lance jamais le code produit.

Les anciens `NOEUD*` et livrables IDE/AI Studio restent conservés pour traçabilité,
avec avertissement d'obsolescence. Le prototype d'auto-exécution du bridge a été
retiré. Ne pas copier leurs commandes d'installation, réglages noyau ou exemples
AGY sans les confronter au guide corrigé et à l'environnement réel.
