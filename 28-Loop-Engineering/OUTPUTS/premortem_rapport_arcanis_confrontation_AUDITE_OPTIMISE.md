---
type: reference
tags: [securite/premortem, statut/valide]
source: "[[rapport_arcanis_confrontation_AUDITE_OPTIMISE.txt]]"
date: 2026-06-30
version: 1.0
---

# RAPPORT D'AUDIT PREMORTEM : INTEGRATION ANTIGRAVITY ET GOOGLE AGENTS CLI
**Date de l'audit :** 2026-06-30  
**Analyste :** premortem-analyst (Sous-Agent Tesla)  
**Destinataire :** Mahonheim (Abdellah MOUHTAJ)

---

## 1. Postulat de l'Échec Virtuel (T+3 Mois)

> [!WARNING]
> Nous sommes le **2026-09-30**. 
> Le plan technique d'intégration d'Antigravity CLI et de Google Agents CLI, déployé il y a trois mois sur la machine locale **MIDGARD**, s'est soldé par un **échec total et catastrophique**. 
> Les systèmes locaux sont corrompus ou hors-service : la base de données d'Alexandria est corrompue, les performances CPU sont saturées, les coûts en tokens ont explosé à la suite de boucles de traitement infinies, et les mécanismes de sécurité ont été contournés. L'agent est bloqué dans des boucles d'authentification OAuth interactives non gérables, et la confiance de Mahonheim est rompue.
> 
> Voici la reconstitution historique objective des causes et mécanismes de ce naufrage technique.

---

## 2. Reconstitution Narrative de la Catastrophe

* **Juillet 2026 — L'Illusion du Succès Initial :**  
  Le déploiement initial se déroule sans encombre. La commande unique `uvx google-agents-cli setup` installe proprement le CLI et les 7 compétences ADK. Le proxy RTK (Rust Token Killer) fonctionne parfaitement avec la compatibilité `--gemini`, affichant un taux de compression de 85% sur les logs et les barres de progression de build. Les tests d'évaluation déterministes (Niveau 1) locaux valident les configurations sans consommer de tokens API distants. MIDGARD (8 Go RAM, CPU-only) encaisse la charge de manière stable.

* **Début Août 2026 — Les Premières Fêlures Invisibles :**  
  Une mise à jour automatique mineure du noyau Linux de la machine hôte MIDGARD modifie la gestion des namespaces et des cgroups. Du jour au lendemain, l'isolation `nsjail` requise par Antigravity (`enableTerminalSandbox: true`) échoue silencieusement sur les commandes de fichiers. Face à l'impossibilité de travailler et à l'urgence opérationnelle, le mode sandbox est manuellement désactivé (`enableTerminalSandbox: false`). L'isolation système est rompue. Parallèlement, Google déploie une mise à jour mineure mais obligatoire du binaire propriétaire fermé d'Antigravity CLI (`agy`), modifiant le format de stockage de ses fichiers de configuration interne. Cette modification rend le proxy RTK muet : il ne parvient plus à s'interposer de manière dynamique. Sans lever d'erreur fatale, RTK cesse de compresser. Le flux de tokens brut revient à 100% de bruit de terminal sans que l'agent ou Mahonheim n'en soient immédiatement alertés.

* **Fin Août 2026 — La Dérive Sémantique et la Saturation Matérielle :**  
  Les tests d'évaluation déterministes locaux de Niveau 1, basés sur des règles strictes mais superficielles (JSON et typage), valident les commits. Toutefois, des régressions logiques et comportementales profondes s'installent dans les graph workflows d'ADK 2.0. N'ayant pas de garde-fous sémantiques continus, les agents tournent en boucle, répétant des tâches complexes. La consommation de tokens s'envole en raison de l'inactivité de RTK. Simultanément, plusieurs instances de sous-agents s'exécutent en parallèle, provoquant des accès concurrents intenses en écriture sur `alexandria_brain.db`. Le script `search_router.py` ne gérant pas les files d'attente d'écriture pour SQLite, des erreurs critiques de type `database is locked` surgissent, paralysant la recherche sémantique locale d'Alexandria.

* **Mi-Septembre 2026 — L'Effondrement du Système :**  
  Le 15 septembre, lors du build local d'un conteneur Docker destiné à un déploiement Cloud Run, la machine MIDGARD sature sa mémoire physique (8 Go RAM, sans swap configuré). Le système subit un gel matériel complet (kernel panic lié à un Out of Memory). L'arrêt brutal survient en pleine transaction SQLite sur la base d'indexation Alexandria, corrompant définitivement le fichier de base de données. Au redémarrage, l'agent tente de reconstruire l'index en boucle, consommant 100% du CPU de MIDGARD et bloquant toute intervention.

* **30 Septembre 2026 — Le Point de Non-Retour :**  
  Google déploie une mise à jour d'authentification OAuth interactive sur les serveurs distants d'Antigravity CLI. La variable statique `ANTIGRAVITY_TOKEN` est révoquée. L'agent Tesla, s'exécutant en arrière-plan sans terminal interactif graphique capable d'afficher la mire d'authentification Web, échoue en boucle sur l'authentification. Le système d'agent est totalement inopérant.

---

## 3. Analyse Tripartite des Risques (Gary Klein Model)

### A. L'Avocat du Diable (Causes Techniques & Factuelles)

* [ ] **Facteur 1 : Rupture d'isolation et dépendance noyau (nsjail) :**  
  L'activation d'isolation par `nsjail` dépend directement de la configuration des namespaces du noyau Linux de l'hôte MIDGARD. Les mises à jour système ont cassé `nsjail`, forçant la désactivation du sandbox et ouvrant la voie à la lecture de fichiers sensibles hors du workspace en cas d'intrusion.
* [ ] **Facteur 2 : Obsolescence et incompatibilité de RTK (Rust Token Killer) :**  
  L'intégration de RTK via un flag de compatibilité obsolète (`rtk init -g --gemini`) n'a pas résisté à la mise à jour structurelle du binaire fermé d'Antigravity CLI (`agy`), annulant la compression de logs de manière silencieuse et provoquant le gaspillage massif du budget de tokens.
* [ ] **Facteur 3 : Corruption de la base SQLite suite à un OOM (Out Of Memory) :**  
  L'absence de swap et le manque de limitations de ressources physiques pour les builds Docker locaux ont provoqué le gel de MIDGARD (8 Go RAM). Le crash en pleine écriture concurrentielle sur `alexandria_brain.db` a corrompu l'index FTS5, rendant le RAG local inexploitable.
* [ ] **Facteur 4 : Blocage de l'authentification asynchrone par OAuth interactif :**  
  L'absence de mécanisme de rafraîchissement automatique de token pour Antigravity CLI dans un contexte non interactif a causé un blocage complet du démon d'exécution dès que l'authentification statique a été révoquée par Google Cloud.

### B. L'Inspecteur des Angles Morts (Hypothèses Cachées non Validées)

* **Hypothèse non vérifiée 1 : L'invariabilité de la configuration d'Antigravity CLI (`agy`) :**  
  Nous avons supposé que parce qu'Antigravity CLI reprenait l'architecture de configuration de Gemini CLI, les outils tiers comme RTK resteraient compatibles à long terme. En réalité, le binaire closed-source d'Antigravity est mis à jour sans préavis par Google, modifiant ses schémas internes et brisant les intégrations locales non officielles.
* **Hypothèse non vérifiée 2 : La suffisance des tests déterministes (Niveau 1) :**  
  Nous avons pensé que les tests unitaires et d'assertions statiques sans token suffiraient à valider la sûreté du code des agents au quotidien. En réalité, le manque d'évaluations sémantiques continues (Niveau 2) a permis à des dérives de logique comportementale de s'installer, provoquant des boucles d'exécution consommatrices de tokens et de ressources CPU locales.
* **Hypothèse non vérifiée 3 : L'absence de conflits d'accès concurrents sur SQLite :**  
  Nous avons supposé que le volume de requêtes d'indexation locale ne nécessiterait pas de gestion de concurrence ou de verrous d'écriture spécifiques sur la base de données SQLite d'Alexandria. En réalité, l'exécution simultanée de plusieurs sous-agents a verrouillé la base de données, provoquant des crashs en cascade.
* **Hypothèse non vérifiée 4 : La stabilité de l'environnement hôte MIDGARD :**  
  Nous avons supposé que les ressources système locales (8 Go RAM, CPU-only) resteraient suffisantes sans besoin de quotas de ressources ou d'isolation de processus au niveau système (cgroups, limites docker, swap), ce qui s'est avéré faux lors des pics de build.

### C. La Vigie des Signaux Faibles (Indicateurs Précurseurs)

1. **Signal 1 : Latences d'initialisation de nsjail :**  
   Des délais croissants à chaque appel shell (passant de 50ms à plus de 1500ms sous charge), signalant que le noyau de MIDGARD peinait à allouer les namespaces et cgroups pour les micro-sandboxes.
2. **Signal 2 : Échecs intermittents d'écriture SQLite :**  
   L'apparition sporadique d'avertissements `database is locked` dans les journaux de recherche de `search_router.py` a été ignorée, alors qu'elle indiquait un goulot d'étranglement majeur sur les écritures concurrentes.
3. **Signal 3 : Dégradation du taux de compression de RTK :**  
   Une augmentation progressive du nombre de tokens consommés par commande bash simple (le taux de compression passant de 85% à 15% suite à des changements de format de sortie du CLI), signalant que l'intercepteur de RTK ne reconnaissait plus les patterns.
4. **Signal 4 : Pics d'utilisation RAM lors des builds locaux :**  
   Des alertes silencieuses du démon système (dmesg) signalant des processus tués par le OOM-killer ou des swaps temporaires agressifs sur le disque dur lors de l'exécution de `agents-cli deploy` localement.

---

## 4. Plan de Résilience & Checklist de Prévention

Pour éviter que ce scénario catastrophe ne se produise dans le monde réel, les contre-mesures obligatoires suivantes doivent être appliquées au plan initial :

| Risque Identifié | Action Préventive Obligatoire | Indicateur de Déclenchement (Seuil) |
| :--- | :--- | :--- |
| **Instabilité de nsjail** | Implémenter un script de fallback de sécurité vers une isolation Docker/Podman locale confinée en cas de défaillance de nsjail. | Échec d'une seule commande sous nsjail (code retour d'initialisation sandbox non nul). |
| **Silence de RTK (Désynchronisation)** | Intégrer un test d'assertion automatisé dans les scripts de pré-commit pour vérifier le taux effectif de compression de RTK sur un log de build test. | Taux de compression mesuré inférieur à 50% sur la commande de test. |
| **Corruption d'Alexandria SQLite** | Configurer SQLite en mode WAL (Write-Ahead Logging) pour améliorer les accès concurrents, et mettre en place une tâche cron de sauvegarde automatique (`VACUUM INTO`) quotidienne de `alexandria_brain.db`. | Nombre d'écritures concurrentes actives > 2 ou taille du fichier de base > 50 Mo. |
| **Saturation Mémoire (OOM)** | Configurer une partition swap de 4 Go minimum sur MIDGARD et imposer des limites d'utilisation mémoire strictes (cgroups) à 1 Go par agent et 2 Go par conteneur Docker de build. | Consommation RAM globale système atteignant 85% de la capacité physique. |
| **Révocation du jeton d'authentification** | Implémenter un wrapper d'authentification utilisant l'API d'authentification d'application Google Cloud (Service Account) avec fichier de clé JSON chiffré localement plutôt qu'une variable `ANTIGRAVITY_TOKEN` utilisateur. | Expiration imminente du jeton ou code d'erreur HTTP 401 sur les requêtes Antigravity. |
| **Dérives sémantiques d'agent** | Automatiser une boucle de test de Niveau 2 (sémantique avec LLM-as-a-Judge sur 10 cas représentatifs) sur une base hebdomadaire ou à chaque pré-release. | Baisse du score d'évaluation sémantique sous 80/100 lors des tests hebdomadaires. |

### Checklist de Sûreté Pré-Exécution :
- [ ] **Mesure 1 :** L'intégrité de la sandbox nsjail est vérifiée via une commande d'écriture test confinée avant de lancer un run d'agent.
- [ ] **Mesure 2 :** Un script de diagnostic (`rtk_diagnostic.sh`) est exécuté au démarrage pour valider que le proxy RTK intercepte et compresse correctement le flux standard de test.
- [ ] **Mesure 3 :** La base de données `alexandria_brain.db` est configurée en mode WAL (`PRAGMA journal_mode=WAL;`) et sa cohérence est validée (`PRAGMA integrity_check;`).
- [ ] **Mesure 4 :** Un swap de 4 Go est activé et vérifié via la commande `swapon --show`.
- [ ] **Mesure 5 :** Le service account GCP pour Antigravity dispose d'une clé JSON valide stockée dans un espace sécurisé non suivi par Git.

---
*Rapport généré et validé localement sur MIDGARD par Tesla.*

Signé / Fait par : Tesla sur Antigravity CLI
Main rendue à Mahonheim
