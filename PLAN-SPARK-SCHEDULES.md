# PLAN-SPARK-SCHEDULES — 6 déclencheurs prêts à coller

![Status](https://img.shields.io/badge/Status-PROPOSAL%20V1-orange) ![Plateforme](https://img.shields.io/badge/Plateforme-Gemini%20Spark-blue) ![Rattachement](https://img.shields.io/badge/Rattach%C3%A9-PLAN--QUOTIDIEN-purple)

| Paramètre | Valeur |
| :--- | :--- |
| **Version** | 1.0.0 · 2026-09-17 |
| **Objet** | Configurer la couche de déclenchement cloud du `PLAN-QUOTIDIEN.md` |
| **Complément de** | `PLAN-QUOTIDIEN.md` — Bloc B (Q4, Q5, Q7) et Bloc C (Q8) |
| **Charge** | ≈ 45 min pour les 6 schedules |
| **Source de référence** | Documentation officielle Google — *Create & manage schedules for tasks in Gemini Spark* |

---

## 0. La frontière à connaître avant de commencer

> **Gemini Spark s'exécute dans le cloud Google. Il ne peut pas lancer une commande sur MIDGARD.**

| Spark **peut** | Spark **ne peut pas** |
| :--- | :--- |
| Lire Gmail, Agenda, Drive, Docs | Exécuter `bash tools/quotidien_status.sh` |
| Rédiger, résumer, structurer, surveiller un sujet | Lire `$TESLA_ROOT` ou vos bases locales |
| Écrire dans un document Drive | Toucher `~/.tesla/` ou vos clés |
| Envoyer un email, préparer un brouillon | Modifier votre dépôt Git |

**Conséquence directe :** chaque schedule ci-dessous est conçu comme un **producteur d'entrées** vers votre système local. La tâche **Q7** du `PLAN-QUOTIDIEN.md` est ce qui transforme ces entrées cloud en **entrées gouvernées** de MIDGARD. Tant que Q7 n'est pas faite, ces schedules produisent des artefacts dans le cloud qui attendent — ce qui reste utile, mais n'est pas encore la boucle complète.

---

## 1. Prérequis — à vérifier avant de créer (5 min)

| # | Condition | Statut |
| :--- | :--- | :--- |
| 1 | Avoir **18 ans ou plus** | ☐ |
| 2 | Être connecté avec un **compte Google personnel** — *pas* un compte professionnel ou scolaire | ☐ |
| 3 | Détenir un abonnement **Google AI Pro ou Ultra** | ☐ |
| 4 | Avoir **Keep Activity activé** sur `myactivity.google.com` | ☐ |
| 5 | **Disponibilité géographique** : Gemini Spark n'est pas disponible dans l'EEE, au Nigéria, en Suisse ni au Royaume-Uni. **Le Maroc n'est pas concerné.** | ☐ |

**Limites opérationnelles à connaître :**

| Limite | Valeur | Conséquence pratique |
| :--- | :--- | :--- |
| Schedules actifs | **50 maximum** | Largement suffisant — 6 sont proposés ici |
| Tâches simultanées | **15 maximum** | Ne pas empiler les horaires |
| Limite d'usage compute | Variable | **Un schedule ne tournera pas** si votre quota est épuisé à l'heure prévue |
| Précision horaire | Approximative | Ne jamais confier une action critique au timing exact |
| Fuseau horaire | **Figé au lieu de création** | Créez ces schedules **depuis le Maroc**, pas en voyage |

> ⚠️ **Point d'attention propre au Maroc :** le fuseau est verrouillé à la création. Lors des périodes où le Maroc repasse en **UTC+0** (mois de Ramadan), vos schedules continueront de tourner sur le fuseau d'origine — donc avec un décalage apparent d'une heure. Le correctif officiel est de demander à Gemini : *« edit the schedule based on my new timezone »*.

---

## 2. Comment créer un schedule (procédure)

**Voie conversationnelle — recommandée pour vous, car elle accepte le texte tel quel :**

1. Aller sur `gemini.google.com`
2. Dans la barre latérale : **Switch to Spark**
3. Coller le **texte du schedule** (§3 ci-dessous) dans la zone de saisie
4. Cliquer **Submit**
5. Tester immédiatement : survoler le schedule → **More** → **Run now**
6. Vérifier la sortie produite **avant** de passer au schedule suivant

**Voie manuelle — uniquement pour les schedules horaires :**
Spark → **Schedules** → **Create manually** → renseigner *nom*, *fréquence*, *instructions* → **Create**.
*(Cette voie n'est pas disponible pour les moniteurs Gmail ou de sujets.)*

**Bonne pratique de validation (doctrine Vigilum Codex) :** ne jamais créer les 6 schedules d'affilée. **Créer → Run now → vérifier la preuve → valider → passer au suivant.** Un schedule non testé est une promesse, pas une preuve.

---

## 3. Les 6 schedules

---

### SPARK-01 — Brief du matin gouverné

| Champ | Valeur |
| :--- | :--- |
| **Type** | Horaire — quotidien |
| **Déclencheur** | **07h00** (heure locale du Maroc, au moment de la création) |
| **Raccroche** | `PLAN-QUOTIDIEN.md` → §11.2 *Control Dashboard* · alimente **Q4** et **Q7** |
| **Sortie** | Un document Drive « Brief — AAAA-MM-JJ » + un email à `abdellah.mouhtaj@gmail.com` |

**Texte à coller :**
```text
Chaque jour à 7h00, produis mon brief de gouvernance du jour.

Examine mon agenda, mes emails non lus des dernières 24 heures et mes fichiers
Drive modifiés récemment. Puis produis un document intitulé
« Brief — [date du jour] » contenant exactement ces quatre sections :

1. LES 3 PRIORITÉS — les trois actions qui, si elles seules sont faites
   aujourd'hui, rendent la journée utile. Justifie chaque choix en une phrase.
2. CE QUI PEUT ATTENDRE — les éléments qui semblent urgents mais qui ne le sont
   pas. Indique le risque encouru si on les reporte.
3. LES DÉCISIONS EN ATTENTE — toute demande qui attend une réponse de ma part
   depuis plus de 48 heures. Précise qui attend et depuis quand.
4. UNE QUESTION À ME POSER — la seule question dont la réponse changerait
   réellement le plan de la journée.

Règles : ne jamais inventer une information absente. Si une section ne contient
rien, écris « rien à signaler » plutôt que de remplir artificiellement.
Ton factuel, aucune flatterie. Enregistre le document dans Drive et
envoie-moi le lien par email avec le brief en corps de message.
```

---

### SPARK-02 — Journal de session quotidien

| Champ | Valeur |
| :--- | :--- |
| **Type** | Horaire — quotidien |
| **Déclencheur** | **19h00** |
| **Raccroche** | `PLAN-QUOTIDIEN.md` **Q5** (mémoire de session) et **Q7** (ingestion) |
| **Sortie** | Un document Drive **au format d'entrée figé**, prêt à être ingéré par MIDGARD |

**Texte à coller :**
```text
Chaque jour à 19h00, produis mon journal de session du jour.

Source : mes échanges Gemini du jour, mon agenda, mes emails envoyés et
mes fichiers Drive créés ou modifiés aujourd'hui.

Format de sortie STRICTEMENT respecté — c'est un format d'ingestion machine,
ne le modifie jamais sans que je te le demande :

date: AAAA-MM-JJ
sessions:
  - objet: <une phrase, 120 caractères maximum>
    categorie: <GOUVERNANCE | VEILLE | REDACTION | FORMATION | ADMINISTRATIF>
    resultat: <ce qui a été produit ou décidé, concret>
    preuve: <lien, nom de fichier ou référence vérifiable>
    suite: <action ouverte, ou "aucune">
decisions:
  - <décision prise aujourd'hui, ou "aucune">
ouvertures:
  - <question restée sans réponse, ou "aucune">

Règles absolues : n'inscris jamais de mot de passe, de clé, de jeton ou de
numéro de pièce d'identité — si tu en rencontres un, écris « [SECRET MASQUÉ] ».
Ne devine jamais un résultat : si tu n'as pas de preuve vérifiable,
inscris « preuve: non traçable ». Enregistre le document dans Drive dans un
dossier nommé « INGESTION-TESLA », nom de fichier
« journal-AAAA-MM-JJ.md », et signale-moi qu'il est prêt.
```

---

### SPARK-03 — Veille stratégique hebdomadaire

| Champ | Valeur |
| :--- | :--- |
| **Type** | Horaire — hebdomadaire |
| **Déclencheur** | **Lundi 08h30** |
| **Raccroche** | `PLAN-QUOTIDIEN.md` **Q4** · respecte `36-Veille-Strategique/Charte_Veille_Strategique.md` et `La grille de rédaction d'un rapport analytique.md` |
| **Sortie** | Un rapport structuré déposé dans « INGESTION-TESLA » |

**Texte à coller :**
```text
Chaque lundi à 8h30, produis mon rapport de veille stratégique de la semaine
écoulée.

Domaines à couvrir, dans cet ordre de priorité :
1. Gouvernance des agents IA : réglementation, normes, audits, incidents publics
   de dérive d'agents autonomes.
2. Protocoles et outillage : Model Context Protocol (MCP), orchestrations
   d'agents en CLI, traçabilité et preuve d'exécution.
3. Intelligence artificielle locale et souveraineté des données.
4. Résultats, retours d'expérience et échecs notables rendus publics.

Structure du rapport :
- SYNTHÈSE : 5 lignes maximum.
- SIGNAUX FORTS : 3 à 5 éléments, chacun avec source et date. Distingue
  explicitement le FAIT (vérifiable) de l'INTERPRÉTATION (ton analyse).
- SIGNAUX FAIBLES : ce qui commence à peine à apparaître et pourrait compter
  dans six mois.
- CONSÉQUENCE POUR VIGILUM CODEX : ce que cela change concrètement pour
  mon positionnement, mes méthodes ou mes outils. Une seule recommandation
  actionnable, pas une liste.
- CE QUE JE N'AI PAS PU VÉRIFIER : toute information incertaine ou à source
  unique. N'invente jamais une source ni une date.

Enregistre dans Drive / INGESTION-TESLA sous
« veille-AAAA-MM-JJ.md », et envoie-moi par email la synthèse de 5 lignes.
```

---

### SPARK-04 — Revue de parité hebdomadaire

| Champ | Valeur |
| :--- | :--- |
| **Type** | Horaire — hebdomadaire |
| **Déclencheur** | **Vendredi 17h00** |
| **Raccroche** | `PLAN-QUOTIDIEN.md` **Q2**, **Q3**, **Q11** · applique `PROTOCOLES/LOI-DE-PARITE-ABSOLUE.md` |
| **Sortie** | Un ordre de mission de contrôle, remis **à vous**, à coller dans l'agent local |

> **Précision doctrinale importante :** Spark ne peut pas exécuter l'audit de parité — il n'a pas accès à MIDGARD. Ce schedule est donc un **secrétaire de gouvernance**, pas un auditeur. Per `P2 — Producer ≠ Validator`, cela le rend même préférable : l'audit réel doit être exécuté par un acteur distinct de celui qui a produit les mutations.

**Texte à coller :**
```text
Chaque vendredi à 17h00, prépare ma revue de parité hebdomadaire.

Tu ne peux PAS exécuter de commande sur ma machine locale : ton rôle est de
me préparer l'ordre de mission de contrôle, pas de le réaliser.

Produis un document intitulé « Revue de parité — semaine du [date] » contenant :

1. LES 4 CONTRÔLES À EXÉCUTER, sous forme de commandes copiables :
   - Parité du registre et des références canoniques :
     bash tools/quotidien_status.sh
   - Baseline de gouvernance complète :
     bash tools/quotidien_status.sh --tests
   - Vérification des références mortes dans les fichiers justfile :
     grep -rn "\.service\|\.timer\|\.path" --include=justfile .
   - État Git et écart avec origin :
     git status --short && git log --oneline -5

2. LA TRAME DE PREUVE — un tableau à remplir par moi, avec une ligne par
   contrôle et trois colonnes : Commande / Sortie brute collée / Verdict PASS
   ou BLOCK. Rappelle en tête de tableau la règle « No Proof, No Pass » :
   une sortie vide ou un exit 0 ne constitue pas une preuve à eux seuls.

3. LES REGISTRES OUVERTS — à partir de ce que tu sais de mes échanges de la
   semaine : questions de gouvernance, décisions différées, engagements pris
   et non tenus. Si tu n'as rien de vérifiable, écris « registre non
   consultable » plutôt que de supposer.

4. UNE SEULE QUESTION À ME POSER pour la semaine suivante.

Ton sobre, aucune flatterie, aucune conclusion que je n'aie pas prouvée
moi-même. Enregistre dans Drive sous « revue-parite-AAAA-MM-JJ.md ».
```

---

### SPARK-05 — Moniteur Gmail : email actionnable

| Champ | Valeur |
| :--- | :--- |
| **Type** | **Moniteur Gmail** — déclenché par la réception d'un email correspondant à un filtre |
| **Déclencheur** | Réception d'un email qui demande une action de votre part |
| **Raccroche** | `PLAN-QUOTIDIEN.md` **Q8** · illustre l'exemple officiel Google (*« Whenever I receive an email from my manager with an action item… »*) |
| **Sortie** | Un brouillon de réponse **non envoyé** + un résumé de l'action attendue |

> ⚠️ **Règle de sécurité :** le brouillon n'est **jamais envoyé automatiquement**. Vous restez la signature. C'est la traduction opérationnelle de *« l'IA ne décide pas de sa propre réussite »*.

**Texte à coller :**
```text
Déclencheur : dès que je reçois un email qui me demande explicitement une action,
une réponse, une décision ou un document.

Important : ce n'est PAS un moniteur qui réagit à tous mes emails. Ne déclenche
que si l'email contient une demande claire qui m'est adressée. En cas de doute,
ne déclenche pas.

Pour chaque email concerné, prépare :
1. RÉSUMÉ DE LA DEMANDE — 2 lignes maximum, factuel.
2. QUI ATTEND QUOI — expéditeur, demande précise, échéance si elle est mentionnée
   (sinon écris « échéance non mentionnée »).
3. CE QU'IL ME MANQUE pour répondre — informations, décisions ou documents
   absents de ma part.
4. UN BROUILLON DE RÉPONSE prêt à relire, dans mon registre habituel :
   courtois, direct, sans engagement que je n'aie pas autorisé.
   N'ENVOIE JAMAIS ce brouillon : place-le en brouillon et attends ma validation.

Si l'email contient une donnée sensible, un secret, une clé ou un numéro de
compte, ne recopie rien de tout cela dans ton résumé — écris « [DONNÉE SENSIBLE] ».
Notifie-moi dans le fil Gemini, sans créer de tâche supplémentaire.
```

---

### SPARK-06 — Moniteur de sujet stratégique

| Champ | Valeur |
| :--- | :--- |
| **Type** | **Moniteur de sujet** — surveille actualités, finance, événements |
| **Déclencheur** | Apparition d'un événement significatif sur un sujet surveillé |
| **Raccroche** | `PLAN-QUOTIDIEN.md` **Q4** et **Q8** · correspond aux « Topic monitors » officiels de Spark |
| **Sortie** | Une alerte qualifiée, jamais un flux brut |

> ⚠️ **Limite officielle à respecter :** Google précise que les moniteurs **ne conviennent pas aux données à évolution rapide ni aux tâches critiques en temps réel**. Ce schedule sert donc à la **détection de signal**, pas à la réaction d'urgence.

**Texte à coller :**
```text
Surveille l'apparition d'événements significatifs sur ces sujets :
- gouvernance et réglementation des agents IA
- protocole MCP et orchestration d'agents en ligne de commande
- incidents publics de dérive d'agents autonomes
- exigences d'auditabilité et de traçabilité imposées aux systèmes d'IA

Quand un événement significatif apparaît, préviens-moi avec :
1. LE FAIT — ce qui s'est passé, en 3 lignes, avec la source et sa date.
2. LE NIVEAU DE FIABILITÉ — source primaire (document officiel, dépôt, décision)
   ou source secondaire (presse, reprise, rumeur). Sois explicite.
3. POURQUOI CELA COMPTE POUR MOI — lien direct avec mon positionnement de
   consultant en gouvernance d'opérations IA, ou écris « lien non établi »
   si tu n'en vois pas. N'invente jamais un lien pour remplir la case.
4. L'ACTION MINIMALE — une seule chose à faire, ou « aucune ».

Ne me préviens PAS pour les annonces mineures, les mises à jour de version
sans conséquence, ni les reformulations d'une information déjà connue.
Le silence est une réponse acceptable : mieux vaut ne rien dire que
diluer le signal.

Regroupe les alertes : une seule notification par jour maximum, sauf événement
majeur. Enregistre le cumul hebdomadaire dans Drive sous
« signaux-AAAA-MM-JJ.md ».
```

---

## 4. Tableau de synthèse

| ID | Nom | Type | Fréquence | Sortie | Tâche liée |
| :--- | :--- | :--- | :--- | :--- | :--- |
| SPARK-01 | Brief du matin gouverné | Horaire | Quotidien 07h00 | Doc Drive + email | Q4, Q7 |
| SPARK-02 | Journal de session quotidien | Horaire | Quotidien 19h00 | `journal-AAAA-MM-JJ.md` | Q5, Q7 |
| SPARK-03 | Veille stratégique hebdomadaire | Horaire | Lundi 08h30 | `veille-AAAA-MM-JJ.md` | Q4 |
| SPARK-04 | Revue de parité hebdomadaire | Horaire | Vendredi 17h00 | `revue-parite-AAAA-MM-JJ.md` | Q2, Q3, Q11 |
| SPARK-05 | Email actionnable | Moniteur Gmail | À réception | Brouillon non envoyé | Q8 |
| SPARK-06 | Sujet stratégique | Moniteur de sujet | À l'événement | `signaux-AAAA-MM-JJ.md` | Q4, Q8 |

**Ordre de mise en service recommandé** (un par jour, jamais six d'un coup) :
`SPARK-01` → vérifier 1 jour → `SPARK-02` → vérifier 1 jour → `SPARK-03` (attendre le lundi suivant) → `SPARK-04` (vendredi) → `SPARK-05` → `SPARK-06`.

---

## 5. Après création — discipline de gouvernance

**Ce que vous devez faire, systématiquement :**

1. **`Run now` avant de valider.** Un schedule non déclenché une fois n'est pas prouvé.
2. **Conserver une trace du premier cycle** dans `OUTPUTS/` (capture ou copie du document produit).
3. **Corriger par `Edit with Gemini`**, jamais en recréant le schedule : la documentation officielle recommande la modification dans le fil pour les déclencheurs non horaires.
4. **Surveiller le quota.** Si le quota compute est épuisé à l'heure prévue, **le schedule ne tourne pas** — et ne produit donc aucune trace. C'est un *silence*, pas un succès. À vérifier dans la revue de parité de `SPARK-04`.
5. **Ne jamais supprimer un fil de tâche Spark** pour « faire le ménage » : supprimer le fil supprime **tous les schedules** qu'il contient.
6. **Nommer explicitement** chaque schedule (jamais un titre générique) : le registre de vos automatisations doit être lisible d'un coup d'œil.

**Deux pièges à ne pas confondre :**

| Confusion fréquente | Réalité |
| :--- | :--- |
| *« Une tâche planifiée s'est exécutée »* | Vrai — mais une tâche qui s'exécute **sans produire de trace visible** n'est pas une preuve. Exigez toujours un artefact nommé. |
| *« Gemini Spark = Gemini Scheduled Actions »* | Faux — fonctionnalités distinctes. Ce document traite des **Schedules de Spark**, pas des *Scheduled actions* des conversations Gemini. |

---

## 6. Ce que ces schedules débloquent — et ce qui reste à faire

**Débloqué immédiatement, sans aucune ligne de code :**
- Un brief quotidien qui vous dit quoi faire, pas quoi lire.
- Une mémoire de session rédigée au format d'ingestion machine — **prête** pour MIDGARD.
- Une veille hebdomadaire structurée dans votre grille existante.
- Un rappel de gouvernance hebdomadaire qui vous remet vos propres règles sous les yeux.

**Reste à faire pour fermer la boucle (tâche Q7 du `PLAN-QUOTIDIEN.md`) :**
tant que le pont n'existe pas, les documents produits partent dans Drive et **attendent un geste de votre part**. L'option A de Q7 — *zone de dépôt Drive + ingestion locale validée* — transforme le dossier `INGESTION-TESLA` en porte d'entrée gouvernée, avec validation de conformité, scan de secrets, refus fail-closed et journal horodaté.

> **L'ordre compte.** Mettre les schedules en place **avant** Q7 est acceptable : cela crée un flux d'entrées réel à brancher. L'inverse — brancher un pont qui n'ingère rien — ne prouverait rien.

---

> **Formule de clôture**
> *Un déclencheur n'est pas une preuve. Un artefact nommé, horodaté et ingéré l'est.*
> **No Proof, No Parity, No Publish.**
