# Tesla SPARK MCP Gateway — lecture seule

Révision auditée le **2026-09-19**. Serveur ASGI Starlette produit par le SDK
Python MCP officiel **FastMCP 1.x**, servi par Uvicorn sur `/mcp` en Streamable
HTTP. Ce n'est pas un serveur FastAPI. Le transport est stateless avec réponses
JSON pour éviter l'accumulation de sessions sur MIDGARD.

## Périmètre

Trois outils seulement :

- `tesla_status` : état de ce processus ; ne certifie ni MIDGARD ni une connexion Google.
- `github_read_file` : fichier UTF-8 du dépôt Tesla, contenu non fiable à relire.
- `github_list_directory` : métadonnées d'un répertoire du dépôt Tesla.

**Aucun shell, accès arbitraire au disque local, écriture GitHub, génération Gemini
ou exécution AGY.** Le parcours Google AI Studio / Gemini dans TERMINATOR est
[documenté séparément](../EXPORT/To_RENA/CODE_EDITOR/LIVRABLE_FINAL_AIStudio_Headless_Terminator.md).
Ne pas charger `GEMINI_API_KEY` dans le processus passerelle.

## Installation et lancement

Depuis la racine du dépôt :

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r 58-Spark-MCP-Gateway/requirements.txt
.venv/bin/python -m unittest discover -s tests -v
```

Dans un panneau TERMINATOR dédié, diffusion clavier désactivée :

```bash
bash
set +x
read -r -s -p 'Jeton MCP partagé (32 caractères minimum) : ' TESLA_SPARK_MCP_TOKEN
printf '\n'
export TESLA_SPARK_MCP_TOKEN
.venv/bin/python 58-Spark-MCP-Gateway/58-Tesla-Spark-MCP-Gateway.py
# Après arrêt Ctrl+C :
unset TESLA_SPARK_MCP_TOKEN GITHUB_PERSONAL_ACCESS_TOKEN
exit
```

Utiliser un jeton aléatoire issu de votre gestionnaire de secrets (au moins 32
caractères ASCII imprimables, sans espace), pas une phrase de passe prévisible.
Le même jeton doit être configuré côté client dans son stockage sécurisé.
Pour GitHub, fournir au processus `GITHUB_PERSONAL_ACCESS_TOKEN` via votre
injection de secrets existante : jeton finement limité au seul dépôt et au droit
**Contents: read**. Sans celui-ci, le statut fonctionne mais les outils GitHub
renvoient une erreur explicite. Ne pas exposer de credentials dans des arguments
ou dans le dépôt. L'environnement n'est pas un coffre-fort.

### Configuration

| Variable | Défaut / règle |
|---|---|
| `TESLA_SPARK_MCP_HOST` | `127.0.0.1` ; ne pas ouvrir l'interface réseau sans besoin |
| `TESLA_SPARK_MCP_PORT` | `8080` ; de 1 à 65535 |
| `TESLA_SPARK_MCP_TOKEN` | Obligatoire par défaut, y compris sur loopback |
| `TESLA_SPARK_TUNNEL_HOST` | Vide ; sinon hostname DNS exact, sans schéma, chemin, port ou wildcard |
| `TESLA_SPARK_ALLOW_LOCAL_NO_AUTH` | `0` implicite ; `1` seulement pour développement loopback sans tunnel/proxy |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | Optionnel pour le statut, obligatoire pour les outils GitHub |

**Changement incompatible de sécurité :** un lancement sans jeton échoue
maintenant par défaut. L'exception sans authentification est explicite et refusée
si un hôte non-loopback ou un tunnel est configuré. Le programme ne peut pas
détecter un proxy externe inconnu : ne jamais utiliser cette exception derrière
un proxy, ni contourner le bind par des options Uvicorn externes. Préférer le
lancement direct du fichier ci-dessus.

## Exposition distante, uniquement si nécessaire

- Garder le backend loopback derrière le proxy/tunnel existant, avec HTTPS sur
  toute liaison non locale. Aucun tunnel n'est créé par ce dépôt.
- Déclarer le hostname exact dans `TESLA_SPARK_TUNNEL_HOST` et configurer le jeton
  **avant** d'exposer le backend. Ne jamais désactiver la protection DNS rebinding.
- Pour un environnement de preview exigeant un bind `0.0.0.0`, configurer ce bind,
  le hostname public exact dans `TESLA_SPARK_TUNNEL_HOST` et un jeton. Le hostname
  autorisé permet la preview ; aucun serveur n'est lancé automatiquement ici.
- Le proxy doit préserver l'en-tête `Authorization`, utiliser `/mcp` sans double
  préfixe et autoriser uniquement les clients voulus. Ne pas placer le jeton dans
  une URL. Ne pas journaliser les en-têtes d'authentification.
- Limiter les débits et connexions au proxy : l'authentification seule n'est pas
  une protection contre l'épuisement de ressources par un client autorisé.
- Pas de faux OAuth/DCR ; ce mode requiert un client compatible Bearer statique.
  Sa compatibilité avec votre client SPARK doit être vérifiée de bout en bout.

## Garanties vérifiées et limites

- Jeton comparé en temps constant ; absence/erreur → HTTP 401 avant dispatch MCP.
- Hôte inconnu → 421 ; origine inconnue → 403 ; protection rebinding active.
- `/mcp/sse` n'existe pas. Handshake, liste d'outils et appel `tesla_status` testés
  en ASGI local, sans connexion à Google ou à GitHub.
- Chemins relatifs validés et encodés ; pas de paramètres API injectables.
- GitHub : délai réseau 20 s par opération, réponse ≤ 2 Mio, pas de redirection,
  erreurs assainies, refus du binaire et des formats non pris en charge.
- Les répertoires GitHub sont limités par l'API Contents ; 1 000 entrées déclenchent
  `possibly_truncated`. Les liens symboliques peuvent être résolus par GitHub :
  ce service ne garantit pas l'identité physique du fichier d'origine.
- Versions directes fixées dans `requirements.txt`, mais dépendances transitives
  non verrouillées : tests requis après mise à jour, pas de reproductibilité totale.

Le [rapport historique](SPARK_MCP_Gateway_Integration_Report.md) ne constitue pas
une preuve de fonctionnement distant de cette révision. Aucun déploiement, droit
réel de jeton, tunnel, proxy ou connexion SPARK de production n'a été testé ici.
