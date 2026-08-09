# Plan d’intervention et de déploiement de SuperBrain sur Android

## Résultat final attendu

À l’issue du déploiement, l’utilisateur dispose d’un système fonctionnel composé de :

- un **smartphone Android** avec l’application SuperBrain installée ;
- un **serveur SuperBrain privé** exécuté sur un ordinateur personnel, un mini-serveur ou un VPS ;
- une connexion sécurisée entre l’application Android et ce serveur ;
- une base de données SQLite locale contenant les contenus sauvegardés ;
- l’analyse automatique de liens partagés depuis Android (pages web, vidéos YouTube, publications Instagram publiques selon les limites des plateformes) ;
- des fonctions de recherche, catégories, collections, transcription, rappels et synchronisation ;
- une configuration IA initiale utilisant Google Gemini, avec possibilité d’ajouter Groq, OpenRouter ou Ollama local ultérieurement.

> **Point technique déterminant :** SuperBrain ne peut pas fonctionner uniquement sur le smartphone. L’application Android est le client mobile ; le traitement et la base de données reposent sur un **backend Python** exécuté sur une machine distincte et accessible depuis le téléphone.

---

# A. Ressources nécessaires

## 1. Matériel

| Élément | Minimum recommandé | Usage |
|---|---:|---|
| Smartphone Android | Android 8.0 / API 26 ou version ultérieure ; 4 Go de RAM ; 500 Mo libres | Application SuperBrain, partage des liens, consultation |
| Ordinateur hôte du backend | 4 cœurs, 8 Go de RAM, 10 Go d’espace libre | Serveur SuperBrain, base SQLite, traitement des contenus |
| Réseau local | Wi-Fi stable commun au téléphone et à l’ordinateur | Connexion directe application ↔ backend |
| Connexion Internet | Recommandée | API IA cloud, analyse de liens, installation des dépendances |
| Stockage de sauvegarde | Disque externe ou espace chiffré | Copie de la base de données et de la configuration |

### Configuration recommandée

- **Smartphone :** Android 10 ou plus récent, 6 Go de RAM ou davantage.
- **Serveur local :** ordinateur fixe, portable laissé allumé, mini-PC ou Raspberry Pi 4/5.
- **Traitement IA local optionnel :** 16 Go de RAM minimum recommandés pour Ollama, davantage pour les modèles vision ou la transcription locale.

---

## 2. Logiciels et comptes

| Ressource | Usage | Lien direct |
|---|---|---|
| SuperBrain — code source | Référence, contrôle du code, dépannage | https://github.com/sidinsearch/superbrain |
| APK SuperBrain v2.0.0 | Installation de l’application Android | https://github.com/sidinsearch/superbrain/releases/download/v2.0.0/superbrain.apk |
| Node.js 20 LTS | Lancement simplifié du backend via npm/npx | https://nodejs.org/en/download |
| Python 3.10+ | Dépendance requise par le backend | https://www.python.org/downloads/ |
| FFmpeg | Extraction et traitement audio/vidéo | https://ffmpeg.org/download.html |
| Google AI Studio | Création d’une clé Gemini | https://aistudio.google.com/app/apikey |
| Console Groq — facultatif | Clé IA secondaire et transcription cloud | https://console.groq.com/keys |
| OpenRouter — facultatif | Fournisseur IA de secours | https://openrouter.ai/keys |
| Ollama — facultatif | Exécution locale des modèles IA | https://ollama.com/download |
| ngrok — facultatif | Accès sécurisé au serveur hors du Wi-Fi local | https://ngrok.com/download |
| Docker Desktop — facultatif | Déploiement conteneurisé du backend | https://www.docker.com/products/docker-desktop/ |

Les instructions officielles du projet indiquent notamment Python 3.10+, FFmpeg et Node.js 20+ pour la méthode npm recommandée. [Documentation SuperBrain](https://github.com/sidinsearch/superbrain#backend-setup-prerequisites)

---

## 3. Ressources d’accès et secrets à préparer

1. Une adresse e-mail pour créer ou utiliser un compte Google AI Studio.
2. Une **clé API Gemini**, à conserver secrète.
3. Un gestionnaire de mots de passe ou un coffre-fort chiffré pour stocker :
   - la clé Gemini ;
   - les éventuelles clés Groq et OpenRouter ;
   - le jeton d’accès SuperBrain généré par le serveur ;
   - les identifiants Instagram si cette fonction est activée.
4. Un compte Instagram **secondaire**, uniquement si l’import Instagram authentifié est nécessaire.

> Ne pas utiliser le compte Instagram principal pour l’automatisation. Le projet lui-même recommande un compte secondaire : il s’appuie sur des bibliothèques non officielles et peut provoquer des limites de requêtes, une invalidation de session ou une restriction de compte. [Avertissement du projet](https://github.com/sidinsearch/superbrain#%EF%B8%8F-security-advice)

---

# B. Plan d’intervention linéaire — déploiement initial

## 1. Choisir et préparer l’ordinateur serveur

1. Sélectionner l’ordinateur qui hébergera SuperBrain.
2. Vérifier qu’il dispose d’au moins 10 Go d’espace libre.
3. Vérifier qu’il est connecté au même réseau Wi-Fi que le smartphone Android.
4. Désactiver la veille automatique pendant les périodes d’utilisation de SuperBrain.
5. Mettre à jour le système d’exploitation.
6. Installer les correctifs de sécurité disponibles.
7. Créer un dossier dédié au projet, par exemple :
   - Windows : `C:\SuperBrain`
   - macOS/Linux : `~/superbrain`

**Condition de sortie :** l’ordinateur serveur est à jour, connecté au réseau et peut rester allumé pendant l’usage de l’application.

---

## 2. Installer Node.js

1. Télécharger Node.js LTS depuis :  
   https://nodejs.org/en/download
2. Installer Node.js avec les paramètres recommandés par défaut.
3. Ouvrir un terminal :
   - Windows : PowerShell ;
   - macOS : Terminal ;
   - Linux : Terminal.
4. Exécuter :

```bash
node --version
npm --version
```

5. Vérifier que Node.js est installé et que sa version majeure est au moins égale à 20.

**Condition de sortie :** les commandes `node --version` et `npm --version` renvoient une version valide.

---

## 3. Installer FFmpeg

### Sous Windows

1. Télécharger une build FFmpeg depuis :  
   https://www.gyan.dev/ffmpeg/builds/
2. Télécharger l’archive « full build ».
3. Extraire l’archive dans :

```text
C:\ffmpeg
```

4. Ajouter `C:\ffmpeg\bin` à la variable d’environnement système `Path`.
5. Fermer et rouvrir PowerShell.
6. Vérifier :

```powershell
ffmpeg -version
```

### Sous macOS

1. Installer Homebrew si nécessaire :  
   https://brew.sh/
2. Exécuter :

```bash
brew install ffmpeg
```

3. Vérifier :

```bash
ffmpeg -version
```

### Sous Ubuntu/Debian

1. Exécuter :

```bash
sudo apt update
sudo apt install -y ffmpeg
```

2. Vérifier :

```bash
ffmpeg -version
```

**Condition de sortie :** la commande `ffmpeg -version` retourne les informations de version.

---

## 4. Créer la clé API Google Gemini

1. Ouvrir :  
   https://aistudio.google.com/app/apikey
2. Se connecter avec le compte Google choisi pour le projet.
3. Créer une nouvelle clé API.
4. Copier immédiatement la clé.
5. Enregistrer cette clé dans le gestionnaire de mots de passe.
6. Ne jamais transmettre la clé par messagerie non chiffrée.
7. Ne jamais l’insérer dans une capture d’écran, un dépôt Git ou un document partagé.

**Condition de sortie :** une clé Gemini valide est disponible et stockée de manière sécurisée.

---

## 5. Lancer le backend SuperBrain

1. Ouvrir le terminal sur l’ordinateur serveur.
2. Exécuter la commande suivante :

```bash
npx -y superbrain-server@latest
```

3. Attendre le téléchargement du package et l’installation des dépendances.
4. L’assistant de configuration SuperBrain démarre.
5. Suivre les questions dans l’ordre.
6. Renseigner la clé Gemini lorsque le programme le demande.
7. Ne renseigner aucune clé Groq ou OpenRouter à cette étape si elles ne sont pas nécessaires.
8. Ne pas activer Ollama au cours du premier déploiement.
9. Ne pas renseigner de compte Instagram à cette étape.
10. Laisser le programme générer son **Access Token**.
11. Copier l’Access Token dans le gestionnaire de mots de passe.
12. Relever l’adresse réseau locale et le port du serveur, habituellement sous une forme proche de :

```text
http://192.168.x.x:5000
```

13. Laisser le terminal ouvert et le serveur en cours d’exécution.

Le lanceur npm est la méthode d’installation recommandée par le projet. Il télécharge le backend, crée l’environnement Python, installe les dépendances, lance l’assistant de configuration et affiche le jeton d’accès. [Instructions officielles](https://github.com/sidinsearch/superbrain#method-1-npm-one-line-setup-recommended)

**Condition de sortie :** le serveur est en cours d’exécution, une URL locale et un Access Token sont disponibles.

---

## 6. Vérifier le fonctionnement du backend

1. Sur l’ordinateur serveur, ouvrir un navigateur.
2. Saisir l’adresse suivante en remplaçant l’hôte si nécessaire :

```text
http://localhost:5000/health
```

3. Vérifier qu’une réponse de santé du serveur est renvoyée.
4. Ouvrir ensuite :

```text
http://localhost:5000/docs
```

5. Vérifier que la documentation interactive FastAPI est disponible.
6. Ne pas modifier les endpoints manuellement à ce stade.

**Condition de sortie :** les URL `/health` et `/docs` répondent depuis l’ordinateur serveur.

---

## 7. Identifier l’adresse IP locale de l’ordinateur serveur

### Sous Windows

1. Ouvrir PowerShell.
2. Exécuter :

```powershell
ipconfig
```

3. Relever l’adresse **IPv4** de l’adaptateur Wi-Fi, par exemple :

```text
192.168.1.25
```

### Sous macOS/Linux

1. Ouvrir Terminal.
2. Exécuter :

```bash
ip addr
```

ou :

```bash
hostname -I
```

3. Relever l’adresse IPv4 locale.

4. Construire l’URL du backend :

```text
http://ADRESSE-IP-LOCALE:5000
```

Exemple :

```text
http://192.168.1.25:5000
```

**Condition de sortie :** l’URL réseau locale complète du backend est connue.

---

## 8. Autoriser le backend dans le pare-feu local

### Sous Windows

1. Lors du premier lancement, Windows peut demander une autorisation réseau pour Python, Node.js ou Uvicorn.
2. Autoriser l’accès sur les **réseaux privés uniquement**.
3. Ne pas autoriser automatiquement les réseaux publics.
4. Si aucune demande n’apparaît :
   - ouvrir « Pare-feu Windows Defender avec fonctions avancées » ;
   - créer une règle entrante TCP ;
   - limiter la règle au port `5000` ;
   - limiter le profil au réseau privé.

### Sous macOS

1. Ouvrir les réglages de pare-feu.
2. Autoriser le programme hébergeant le serveur Python/Uvicorn si demandé.
3. Limiter l’accès au réseau local.

### Sous Linux avec UFW

1. Autoriser uniquement le sous-réseau local, par exemple :

```bash
sudo ufw allow from 192.168.1.0/24 to any port 5000 proto tcp
```

2. Ne pas exposer le port 5000 à Internet à ce stade.

**Condition de sortie :** le smartphone peut atteindre l’adresse `http://ADRESSE-IP-LOCALE:5000/health` depuis le réseau Wi-Fi local.

---

## 9. Installer l’application Android SuperBrain

1. Depuis le smartphone Android, ouvrir le lien de téléchargement officiel de la release :

   https://github.com/sidinsearch/superbrain/releases/download/v2.0.0/superbrain.apk

2. Télécharger le fichier `superbrain.apk`.
3. Lorsque Android le demande, autoriser temporairement l’installation d’applications provenant du navigateur ou du gestionnaire de fichiers utilisé.
4. Installer l’APK.
5. Après installation, retirer l’autorisation « installer des applis inconnues » du navigateur si elle n’est plus nécessaire.
6. Ouvrir SuperBrain.

La release `v2.0.0` est présentée par le projet comme une version bêta précoce. [Release SuperBrain v2.0.0](https://github.com/sidinsearch/superbrain/releases/tag/v2.0.0)

**Condition de sortie :** l’application SuperBrain est installée et s’ouvre correctement sur Android.

---

## 10. Configurer l’application Android

1. Ouvrir SuperBrain.
2. Accéder à **Settings / Paramètres**.
3. Dans le champ **Backend URL**, saisir l’URL réseau locale relevée précédemment, par exemple :

```text
http://192.168.1.25:5000
```

4. Dans le champ **Access Token**, coller le jeton généré au démarrage du backend.
5. Enregistrer la configuration.
6. Utiliser le test de connexion intégré, s’il est proposé.
7. Si aucun test n’est proposé, revenir à l’écran principal et vérifier l’absence d’erreur réseau.

**Condition de sortie :** l’application Android est authentifiée auprès du backend et communique avec lui.

---

## 11. Accorder uniquement les autorisations Android nécessaires

1. Autoriser les **notifications** :
   - nécessaire pour les rappels « Watch Later » et les notifications d’état.
2. Autoriser l’accès au partage de liens :
   - SuperBrain doit apparaître dans le menu Android « Partager ».
3. Ne pas accorder d’accès inutile aux fichiers, photos ou contacts si l’application ne le demande pas pour une fonction réellement utilisée.
4. Vérifier que les notifications SuperBrain sont activées dans les paramètres Android.
5. Désactiver l’optimisation agressive de batterie pour SuperBrain seulement si les rappels ou la synchronisation sont interrompus par Android.

**Condition de sortie :** l’application reçoit les notifications et apparaît comme cible de partage Android.

---

## 12. Réaliser le test fonctionnel initial

1. Ouvrir Chrome sur Android.
2. Choisir une page web publique simple, par exemple un article accessible sans connexion.
3. Ouvrir le menu **Partager**.
4. Sélectionner **SuperBrain**.
5. Attendre la confirmation d’enregistrement.
6. Ouvrir l’application SuperBrain.
7. Vérifier que le nouvel élément apparaît dans la bibliothèque.
8. Vérifier la présence des éléments suivants :
   - URL source ;
   - titre ;
   - résumé ;
   - catégorie ou mots-clés ;
   - statut de traitement.
9. Utiliser la recherche interne avec un mot présent dans le titre ou le résumé.
10. Créer une collection de test nommée :

```text
Validation initiale
```

11. Ajouter le contenu testé à cette collection.
12. Supprimer la collection et l’élément de test uniquement après validation complète.

**Condition de sortie :** une page web a été partagée depuis Android, analysée par le backend et retrouvée depuis l’application.

---

## 13. Tester YouTube

1. Ouvrir l’application YouTube ou une vidéo YouTube dans le navigateur.
2. Sélectionner une vidéo publique.
3. Utiliser **Partager**.
4. Sélectionner **SuperBrain**.
5. Attendre la fin du traitement.
6. Vérifier :
   - le titre ;
   - le résumé ;
   - les tags ;
   - la transcription, si disponible ;
   - l’ouverture correcte du lien original.
7. Ajouter la vidéo à une collection « À regarder ».

**Condition de sortie :** une vidéo YouTube est ajoutée et consultable dans SuperBrain.

---

## 14. Configurer les collections et la méthode de classement

1. Créer les collections initiales suivantes :

```text
À regarder
Lecture
Travail
Formation
Références
Recettes
À vérifier
```

2. Définir une règle unique pour chaque collection :
   - **À regarder** : vidéos à consulter ;
   - **Lecture** : articles longs ;
   - **Travail** : contenus directement liés à l’activité professionnelle ;
   - **Formation** : cours, tutoriels, ressources d’apprentissage ;
   - **Références** : contenu durable à conserver ;
   - **Recettes** : cuisine ;
   - **À vérifier** : contenus dont les informations doivent être contrôlées avant réutilisation.
3. Ne pas multiplier les collections pendant les deux premières semaines.
4. Utiliser les tags automatiques comme aide, mais corriger manuellement les catégories incorrectes.

**Condition de sortie :** la bibliothèque possède une structure de classement cohérente et limitée.

---

## 15. Activer les rappels « Watch Later »

1. Ajouter une vidéo importante dans la collection **À regarder**.
2. Vérifier que les notifications SuperBrain sont actives.
3. Vérifier qu’Android n’empêche pas l’application d’envoyer des notifications.
4. Attendre le premier rappel planifié.
5. Tester l’action « Mark as Watched » ou son équivalent dans la notification.
6. Vérifier que le contenu sort du flux de rappels lorsqu’il est marqué comme consulté.

**Condition de sortie :** les rappels Android fonctionnent et peuvent être clôturés.

---

## 16. Ajouter Instagram uniquement après validation du socle

1. Confirmer que les tests web et YouTube sont fonctionnels.
2. Créer ou choisir un **compte Instagram secondaire**.
3. Ne pas utiliser le compte Instagram personnel ou professionnel principal.
4. Dans le terminal du backend, suivre la procédure de connexion Instagram prévue par le projet :

```bash
cd superbrain/backend
python instagram/instagram_login.py
```

5. Saisir les identifiants du compte secondaire uniquement dans l’environnement local.
6. Réaliser la validation 2FA si elle est demandée.
7. Tester avec une publication publique non sensible.
8. Éviter les importations répétitives et rapides.
9. Ne pas automatiser une collecte massive.
10. Si Instagram affiche des limites, interrompre les tests et attendre avant de recommencer.

SuperBrain déclare utiliser Instaloader et Instagrapi pour Instagram. Les contenus publics peuvent être testés en mode non connecté, mais Instagram peut imposer des limitations ; l’authentification augmente les possibilités, sans supprimer les risques de restriction. [Documentation Instagram du projet](https://github.com/sidinsearch/superbrain#instagram-credentials)

**Condition de sortie :** les liens Instagram nécessaires sont traités avec un compte secondaire ou la fonction est volontairement laissée désactivée.

---

## 17. Mettre en place les sauvegardes

1. Identifier le répertoire de données généré par SuperBrain sur le serveur.
2. Localiser :
   - la base SQLite ;
   - les fichiers de configuration ;
   - les éventuels fichiers de sessions ;
   - le fichier contenant les clés API.
3. Créer un dossier de sauvegarde chiffré hors du répertoire du projet.
4. Mettre en place une sauvegarde quotidienne de la base SQLite.
5. Mettre en place une sauvegarde hebdomadaire de la configuration.
6. Ne pas synchroniser les fichiers de clés API ou de sessions Instagram dans un cloud non chiffré.
7. Tester une restauration sur une copie de test avant de considérer la sauvegarde comme valide.

**Condition de sortie :** une copie restaurable de la base de données et de la configuration existe.

---

# C. Exploitation quotidienne

## 18. Procédure de démarrage quotidien

1. Allumer l’ordinateur serveur ou vérifier qu’il est déjà actif.
2. Vérifier qu’il est connecté au réseau.
3. Ouvrir le terminal.
4. Lancer le backend :

```bash
superbrain-server
```

ou :

```bash
npx -y superbrain-server@latest
```

5. Vérifier l’état :

```bash
superbrain-server status
```

6. Ouvrir SuperBrain sur Android.
7. Vérifier que la bibliothèque se charge sans erreur réseau.
8. Partager les contenus souhaités depuis Android.

**Condition de sortie :** le backend et le smartphone sont connectés avant toute capture de contenu.

---

## 19. Procédure de traitement d’un contenu

1. Ouvrir le contenu dans l’application source.
2. Cliquer sur **Partager**.
3. Choisir **SuperBrain**.
4. Attendre la confirmation de sauvegarde.
5. Ouvrir SuperBrain.
6. Vérifier que l’analyse est terminée.
7. Corriger le titre, les tags ou la collection si nécessaire.
8. Placer le contenu dans une collection.
9. Pour toute information importante, ouvrir la source originale et vérifier les faits avant usage ou partage.

**Règle opérationnelle :** un résumé IA ne doit jamais être traité comme une source primaire ni comme une vérification factuelle.

---

## 20. Procédure de fin de journée

1. Vérifier la file d’analyse des contenus en attente.
2. Relancer les échecs de traitement depuis l’application si nécessaire.
3. Vérifier les éléments de la collection « À vérifier ».
4. Laisser le serveur actif si des analyses sont en attente.
5. Si le serveur doit être arrêté :
   - attendre la fin des traitements ;
   - arrêter le processus proprement avec `Ctrl+C` dans le terminal ;
   - ne pas forcer l’arrêt de l’ordinateur pendant une écriture en cours.

---

# D. Feuille de route maîtresse du projet

## Phase 0 — Cadrage et sécurité initiale

**Durée indicative : 0,5 à 1 jour**

1. Définir les objectifs : veille, apprentissage, archivage personnel, contenus à consulter.
2. Définir les catégories initiales.
3. Choisir le serveur hôte.
4. Créer les clés API.
5. Préparer le dispositif de sauvegarde.
6. Décider si Instagram est requis ou exclu.
7. Valider la règle : aucun contenu sensible ne sera transmis à une API cloud sans évaluation préalable.

**Livrable :** charte d’usage personnelle, liste de collections et inventaire des accès.

---

## Phase 1 — Déploiement minimal viable

**Durée indicative : 1 jour**

1. Installer Node.js et FFmpeg.
2. Lancer `superbrain-server`.
3. Configurer Gemini.
4. Installer l’APK Android.
5. Configurer l’URL du backend et l’Access Token.
6. Tester une page web.
7. Tester une vidéo YouTube.
8. Configurer les collections et les notifications.

**Critère de réussite :** les contenus web et YouTube sont sauvegardés, analysés et retrouvés depuis Android.

---

## Phase 2 — Stabilisation fonctionnelle

**Durée indicative : 1 à 2 semaines**

1. Utiliser SuperBrain avec un volume limité de contenus.
2. Évaluer la qualité des résumés et catégories.
3. Corriger les collections inutiles ou ambiguës.
4. Mesurer le taux d’échec des analyses.
5. Vérifier chaque jour l’accès au backend depuis le smartphone.
6. Contrôler les sauvegardes.
7. Mettre à jour les clés API si une fuite est suspectée.
8. Documenter les incidents : erreurs, liens non supportés, lenteurs, limitations IA.

**Critère de réussite :** le taux de réussite est acceptable pour les usages prioritaires et les données sont sauvegardées.

---

## Phase 3 — Extension contrôlée aux fournisseurs IA

**Durée indicative : semaine 3**

1. Conserver Gemini comme fournisseur principal initial.
2. Ajouter une clé Groq seulement si la transcription ou la rapidité doit être améliorée.
3. Ajouter OpenRouter seulement si un fournisseur de secours est nécessaire.
4. Tester un fournisseur à la fois.
5. Vérifier quelles données sont transmises à chaque service.
6. Documenter le coût, les limites, la vitesse et la qualité de chaque fournisseur.
7. Désactiver tout fournisseur inutile.

**Critère de réussite :** l’architecture IA possède un fournisseur principal et, si nécessaire, un seul mécanisme de secours maîtrisé.

---

## Phase 4 — IA locale et réduction de l’exposition des données

**Durée indicative : semaines 4 à 6**

1. Évaluer si l’ordinateur serveur est suffisamment puissant.
2. Télécharger Ollama :  
   https://ollama.com/download
3. Installer Ollama sur le serveur.
4. Télécharger le modèle recommandé par le projet, par exemple :

```bash
ollama pull qwen3-vl:4b
```

5. Vérifier le fonctionnement local du modèle.
6. Configurer SuperBrain pour utiliser Ollama comme solution locale ou de secours.
7. Comparer les résultats avec Gemini.
8. Définir les catégories de contenus obligatoirement traitées en local.
9. Désactiver les API cloud pour ces contenus si la confidentialité l’exige.

**Critère de réussite :** un scénario de traitement local est fonctionnel pour les contenus sensibles ou confidentiels.

---

## Phase 5 — Intégration Instagram contrôlée

**Durée indicative : à partir de la semaine 6**

1. Ne commencer qu’après stabilisation des usages web et YouTube.
2. Utiliser exclusivement un compte secondaire.
3. Commencer par quelques liens publics par jour.
4. Suivre les erreurs et limitations.
5. Interrompre immédiatement en cas de demande de vérification inhabituelle, blocage, restriction ou alerte Instagram.
6. Ne pas stocker ou redistribuer sans droit des contenus privés de tiers.
7. Maintenir une solution de repli : partage manuel du lien et conservation de l’URL seulement.

**Critère de réussite :** la fonction apporte une valeur réelle sans provoquer de comportement anormal sur le compte secondaire.

---

## Phase 6 — Accès hors domicile ou hors bureau

**Durée indicative : après validation locale complète**

1. Ne pas exposer directement le port `5000` sur Internet.
2. Préférer un tunnel HTTPS contrôlé ou un VPN.
3. Pour ngrok :
   - télécharger ngrok : https://ngrok.com/download ;
   - créer un compte ;
   - configurer l’authentification ;
   - lancer :

```bash
ngrok http 5000
```

4. Copier l’URL HTTPS générée dans les paramètres SuperBrain sur Android.
5. Conserver l’Access Token SuperBrain.
6. Vérifier que le tunnel est fermé lorsqu’il n’est pas utilisé.
7. Réévaluer régulièrement la nécessité de cet accès distant.

**Critère de réussite :** l’application est accessible hors réseau local sans ouverture permanente et non contrôlée du serveur personnel.

---

## Phase 7 — Maintenance continue

**Fréquence : hebdomadaire et mensuelle**

### Chaque semaine

1. Vérifier que le backend démarre.
2. Vérifier les erreurs d’analyse.
3. Vérifier les sauvegardes.
4. Vérifier les notifications Android.
5. Supprimer les contenus devenus inutiles.
6. Révoquer et recréer toute clé API soupçonnée d’exposition.

### Chaque mois

1. Vérifier les nouvelles releases SuperBrain :  
   https://github.com/sidinsearch/superbrain/releases
2. Lire les notes de version avant toute mise à jour.
3. Réaliser une sauvegarde complète avant mise à jour.
4. Mettre à jour le backend.
5. Tester une page web et une vidéo YouTube après mise à jour.
6. Mettre à jour l’APK uniquement après validation de compatibilité.
7. Vérifier les limites, tarifs et politiques des fournisseurs IA.
8. Évaluer les changements des règles ou restrictions d’Instagram.

### Tous les trois mois

1. Tester une restauration complète de sauvegarde.
2. Réexaminer les droits d’accès.
3. Révoquer les clés API non utilisées.
4. Vérifier que le compte Instagram secondaire est toujours distinct du compte principal.
5. Évaluer la pertinence de migrer vers un traitement IA plus local.

---

# E. Critères de réception finale

Le déploiement est considéré comme terminé lorsque les conditions suivantes sont toutes remplies :

1. L’application SuperBrain est installée sur Android.
2. Le backend fonctionne sur une machine maîtrisée par l’utilisateur.
3. L’application Android communique avec le backend via URL et Access Token.
4. Une page web est sauvegardée, analysée et retrouvable.
5. Une vidéo YouTube est sauvegardée, analysée et retrouvable.
6. Les collections et la recherche fonctionnent.
7. Les notifications « À regarder » fonctionnent.
8. La base de données est sauvegardée.
9. Les clés API ne sont pas stockées dans un dépôt public ou un document non sécurisé.
10. L’import Instagram est soit désactivé, soit configuré avec un compte secondaire et un usage limité.
11. Le port du backend n’est pas exposé publiquement sans tunnel HTTPS, VPN ou contrôle d’accès adapté.
12. Une procédure de mise à jour et de restauration a été validée.

Le dépôt et ses versions étant encore présentés comme une **bêta précoce**, ce plan doit être appliqué avec une logique de pilote contrôlé : validation locale, sauvegardes régulières, montée en charge progressive et absence de dépendance à SuperBrain pour une donnée critique unique.
