# Feuille de route maîtresse — Déploiement de SuperBrain sur Android

## 0. Résultat final attendu

À la fin de cette procédure, le système doit fonctionner selon cette architecture :

```text
                    SMARTPHONE ANDROID
                           │
                    SuperBrain APK
                           │
                    Wi-Fi / réseau local
                           │
                           ▼
                 MACHINE SERVEUR LOCALE
                           │
                 SuperBrain Server
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
       SQLite          Moteur IA        Analyseurs
          │                │                │
          │          Gemini / Groq /       │
          │          OpenRouter /          │
          │          Ollama                │
          │                                │
          └──────────────┬─────────────────┘
                         ▼
                MÉMOIRE SUPERBRAIN
```

**Point d'arrivée opérationnel :**

1. L'application SuperBrain est installée sur le smartphone Android.
2. Le backend SuperBrain fonctionne sur une machine serveur contrôlée par l'utilisateur.
3. Le smartphone communique avec le backend via le réseau local.
4. Le smartphone peut partager une URL Instagram, YouTube ou Web vers SuperBrain.
5. Le backend récupère et analyse le contenu.
6. L'IA produit les métadonnées et analyses prévues.
7. Les données sont conservées dans le système de stockage local.
8. La recherche, les collections et les rappels fonctionnent.
9. Aucun port Internet public n'est nécessaire.
10. L'accès Instagram authentifié n'est configuré **qu'en cas de nécessité**.

Cette architecture correspond au fonctionnement documenté du projet : l'application Android est cliente du backend, lequel expose notamment une API FastAPI et une base locale.

---

# 1. Périmètre technique retenu

Pour éviter toute ambiguïté, **une seule méthode de déploiement est retenue** dans cette feuille de route.

### Méthode retenue

**Backend :**

```text
Linux
+
Node.js 20+
+
Python 3.10+
+
ffmpeg
+
superbrain-server via npm
```

**Client :**

```text
Android 8.0+
+
APK SuperBrain
```

**Réseau :**

```text
Smartphone
      │
      │ Wi-Fi LAN
      ▼
Serveur
```

### Méthodes volontairement exclues

Pour ce premier déploiement :

* Docker : non utilisé.
* ngrok : non utilisé.
* exposition Internet : non utilisée.
* installation Python manuelle du backend : non utilisée.
* installation sur Android via Termux : non utilisée.
* configuration Instagram authentifiée : non réalisée tant que le fonctionnement de base n'est pas validé.

Cette restriction est volontaire : **un plan d'intervention linéaire ne doit pas proposer cinq chemins concurrents.**

---

# 2. Architecture fonctionnelle finale

Le flux opérationnel sera :

```text
[1] URL
    │
    ▼
[2] Partage Android
    │
    ▼
[3] SuperBrain App
    │
    ▼
[4] Backend API
    │
    ▼
[5] Validation URL
    │
    ▼
[6] Extraction contenu
    │
    ▼
[7] Analyse
    │
    ├── texte
    ├── vision
    ├── audio
    ├── transcription
    └── musique
    │
    ▼
[8] Classification IA
    │
    ▼
[9] SQLite
    │
    ▼
[10] Synchronisation Android
    │
    ▼
[11] Recherche / Collection / Rappel
```

Le dépôt documente notamment les analyseurs texte, vision, audio, YouTube et Web ainsi que le stockage SQLite et la synchronisation offline-first.

---

# 3. Ressources Hardware

## 3.1 Smartphone Android

### Minimum documenté

* Android **8.0 / API 26 ou supérieur**.
* Connexion Wi-Fi.
* Espace libre suffisant pour l'application et les données locales.

Le release v2.0.0 indique Android 8.0+ comme prérequis.

### Recommandation opérationnelle

Je recommande :

* Android 11 ou supérieur ;
* au moins 4 Go de RAM ;
* au moins 5 Go d'espace libre ;
* Wi-Fi 5 GHz si disponible.

Les recommandations RAM/espace supplémentaires sont des recommandations opérationnelles, **pas des exigences publiées par SuperBrain**.

---

# 4. Hardware serveur

Le backend doit fonctionner sur une machine distincte.

### Minimum pratique

* CPU x86-64 ou ARM64 compatible Python/Node ;
* 4 Go RAM ;
* 10 Go d'espace libre ;
* réseau local ;
* Linux recommandé.

### Recommandé

* 8 Go RAM ou davantage ;
* SSD ;
* connexion Ethernet ou Wi-Fi stable ;
* GPU NVIDIA uniquement si l'on souhaite exploiter sérieusement certains traitements locaux.

Le projet n'impose pas de GPU pour son fonctionnement standard.

---

# 5. Ressources logicielles

## 5.1 SuperBrain

### Dépôt officiel

[https://github.com/sidinsearch/superbrain](https://github.com/sidinsearch/superbrain)

Le dépôt est public et sous AGPL v3.

---

## 5.2 APK Android

### Release officielle v2.0.0

[https://github.com/sidinsearch/superbrain/releases/tag/v2.0.0](https://github.com/sidinsearch/superbrain/releases/tag/v2.0.0)

### APK direct

[https://github.com/sidinsearch/superbrain/releases/download/v2.0.0/superbrain.apk](https://github.com/sidinsearch/superbrain/releases/download/v2.0.0/superbrain.apk)

Le release contient bien l'APK `superbrain.apk`.

**SHA-256 publié par GitHub pour cet APK :**

```text
6f337554157403bf08d2530c8fb673415d718b4d2604bcb83569e2e557e33659
```

---

## 5.3 Node.js

Le README actuel indique **Node.js 20+**.

### Téléchargement officiel

[https://nodejs.org/en/download](https://nodejs.org/en/download)

---

## 5.4 Python

Pré-requis du projet :

**Python 3.10+**.

### Téléchargement officiel

[https://www.python.org/downloads/](https://www.python.org/downloads/)

---

## 5.5 ffmpeg

Le projet l'utilise pour les traitements audio/vidéo.

### Site officiel

[https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

Sur Ubuntu :

```bash
sudo apt update
sudo apt install ffmpeg
```

---

## 5.6 Backend npm

Le projet fournit :

```text
superbrain-server
```

et documente :

```bash
npx -y superbrain-server@latest
```

comme méthode d'installation.

### npm

[https://www.npmjs.com/package/superbrain-server](https://www.npmjs.com/package/superbrain-server)

---

# 6. Fournisseurs IA

Le routeur SuperBrain documente quatre voies principales :

| Fournisseur | Fonction    |
| ----------- | ----------- |
| Groq        | IA distante |
| Gemini      | IA distante |
| OpenRouter  | IA distante |
| Ollama      | IA locale   |

### Gemini

[https://aistudio.google.com/](https://aistudio.google.com/)

### Groq

[https://console.groq.com/](https://console.groq.com/)

### OpenRouter

[https://openrouter.ai/](https://openrouter.ai/)

### Ollama

[https://ollama.com/](https://ollama.com/)

---

# 7. Principe de sécurité retenu

Avant toute installation :

### Interdiction de faire ceci

```text
Smartphone
    ↓
Internet
    ↓
ngrok
    ↓
SuperBrain
```

pour le premier déploiement.

Nous utiliserons :

```text
Smartphone
    ↓
Wi-Fi privé
    ↓
Serveur local
```

Le README propose effectivement ngrok pour l'accès extérieur, mais ce n'est **pas nécessaire** pour un déploiement local.

---

# 8. PHASE 0 — Préparation

## 8.1 Identifier les deux machines

Définir :

```text
SMARTPHONE = appareil Android
SERVER     = machine qui exécutera SuperBrain
```

Le serveur doit rester allumé pendant l'utilisation de SuperBrain.

---

## 8.2 Vérifier le réseau

Le smartphone et le serveur doivent être sur le même réseau local.

Exemple :

```text
Serveur : 192.168.1.20
Téléphone : 192.168.1.50
```

Le premier objectif réseau est simplement :

```text
Téléphone → Serveur
```

Aucun accès Internet entrant n'est nécessaire.

---

# 9. PHASE 1 — Préparer le serveur

## 9.1 Vérifier Node.js

Sur le serveur :

```bash
node --version
```

Le résultat doit être :

```text
v20.x.x
```

ou supérieur.

Puis :

```bash
npm --version
```

---

## 9.2 Vérifier Python

```bash
python3 --version
```

Résultat attendu :

```text
Python 3.10+
```

---

## 9.3 Vérifier ffmpeg

```bash
ffmpeg -version
```

Si la commande échoue :

```bash
sudo apt update
sudo apt install ffmpeg
```

Puis :

```bash
ffmpeg -version
```

---

# 10. PHASE 2 — Installer SuperBrain Server

Sur le serveur :

```bash
npx -y superbrain-server@latest
```

Le projet indique que cette commande :

1. télécharge le backend ;
2. crée l'environnement Python ;
3. installe les dépendances ;
4. lance l'assistant de configuration ;
5. démarre l'API ;
6. affiche le token d'accès.

### Point de contrôle

Ne poursuivre que lorsque le backend indique qu'il est démarré.

---

# 11. PHASE 3 — Configuration initiale du backend

L'assistant de configuration doit être exécuté.

### Configuration minimale

Configurer au minimum :

```text
Gemini
```

Le projet recommande Gemini comme premier fournisseur.

Les autres fournisseurs seront ajoutés ultérieurement uniquement si nécessaire.

---

# 12. PHASE 4 — Vérification du serveur

Une fois le serveur lancé :

```bash
curl http://localhost:5000/health
```

Le README documente cette vérification.

### Résultat attendu

Le endpoint doit répondre correctement.

### Si `/health` échoue

**STOP.**

Ne pas installer l'application Android tant que le backend n'est pas fonctionnel.

---

# 13. PHASE 5 — Identifier l'adresse IP du serveur

Sur Linux :

```bash
hostname -I
```

Exemple :

```text
192.168.1.20
```

Conserver cette adresse.

Elle sera nécessaire pour Android.

---

# 14. PHASE 6 — Obtenir le token SuperBrain

Le backend génère/conserve un Access Token.

Le projet utilise notamment :

```text
backend/token.txt
```

pour ce token.

Le token doit être conservé comme **secret**.

Ne pas :

* le publier ;
* l'intégrer dans Git ;
* l'envoyer dans une conversation publique ;
* l'inscrire dans une capture d'écran publique.

---

# 15. PHASE 7 — Télécharger l'application Android

Sur le smartphone :

### Ouvrir

[https://github.com/sidinsearch/superbrain/releases/tag/v2.0.0](https://github.com/sidinsearch/superbrain/releases/tag/v2.0.0)

Télécharger :

```text
superbrain.apk
```

Alternative directe :

[https://github.com/sidinsearch/superbrain/releases/download/v2.0.0/superbrain.apk](https://github.com/sidinsearch/superbrain/releases/download/v2.0.0/superbrain.apk)

Le fichier fait environ **92,6 Mo** selon les métadonnées de la release.

---

# 16. PHASE 8 — Vérifier l'APK

Avant installation, vérifier si possible son SHA-256.

Valeur officielle :

```text
6f337554157403bf08d2530c8fb673415d718b4d2604bcb83569e2e557e33659
```

Sur un ordinateur Linux :

```bash
sha256sum superbrain.apk
```

Le résultat doit être exactement :

```text
6f337554157403bf08d2530c8fb673415d718b4d2604bcb83569e2e557e33659
```

### Si différent

**STOP.**

Ne pas installer l'APK.

---

# 17. PHASE 9 — Installer l'APK Android

Transférer l'APK sur le smartphone.

Android peut demander l'autorisation d'installation depuis une source externe.

Autoriser temporairement cette installation si nécessaire.

Installer :

```text
SuperBrain
```

### Point de contrôle

L'application doit :

* s'installer ;
* se lancer ;
* afficher son interface.

---

# 18. PHASE 10 — Connecter Android au backend

Dans SuperBrain :

```text
Settings
```

Configurer :

### Server URL

```text
http://IP_DU_SERVEUR:5000
```

Exemple :

```text
http://192.168.1.20:5000
```

### Access Token

Entrer le token généré par le backend.

Le README indique explicitement cette procédure :

1. démarrer le backend ;
2. récupérer le token ;
3. renseigner l'URL du serveur ;
4. renseigner le token ;
5. vérifier `/health`.

---

# 19. PHASE 11 — Test de connexion

Depuis le smartphone :

```text
SuperBrain
    ↓
Settings
    ↓
Connection
```

Effectuer le test de connexion.

### Résultat attendu

```text
Android
   ↓
Wi-Fi
   ↓
192.168.x.x:5000
   ↓
SuperBrain API
   ↓
OK
```

### Si la connexion échoue

Vérifier dans cet ordre :

1. serveur démarré ;
2. smartphone sur le même Wi-Fi ;
3. adresse IP correcte ;
4. port `5000` accessible ;
5. token correct.

**Ne modifier qu'un élément à la fois.**

---

# 20. PHASE 12 — Premier test fonctionnel

Ne pas commencer par Instagram.

C'est une erreur de validation.

Le premier test doit être une **URL Web publique simple**.

Flux :

```text
Navigateur Android
       ↓
Partager
       ↓
SuperBrain
       ↓
Analyse
```

Le projet prévoit explicitement le partage d'URL depuis les applications Android.

---

# 21. PHASE 13 — Vérification du traitement IA

Après partage :

```text
URL
 ↓
Queue
 ↓
Extraction
 ↓
IA
 ↓
Résumé
 ↓
Tags
 ↓
Catégorie
```

Vérifier que le contenu apparaît dans la bibliothèque.

### Contrôles

* titre correct ;
* résumé présent ;
* catégorie présente ;
* tags présents ;
* contenu consultable ;
* recherche fonctionnelle.

---

# 22. PHASE 14 — Test YouTube

Une fois le test Web validé :

```text
YouTube
   ↓
Partager
   ↓
SuperBrain
```

Le projet prévoit un analyseur YouTube utilisant la compréhension native de Gemini.

### Objectif

Vérifier :

```text
URL YouTube
     ↓
SuperBrain
     ↓
Gemini
     ↓
Analyse
     ↓
Stockage
```

---

# 23. PHASE 15 — Test audio

Tester ensuite un contenu contenant une piste audio.

Le pipeline documenté comprend :

```text
Groq Whisper
      ↓
fallback
      ↓
OpenAI Whisper local
```

Vérifier qu'une transcription est générée lorsque le contenu s'y prête.

---

# 24. PHASE 16 — Test recherche

Dans SuperBrain :

```text
Search
```

Rechercher un mot présent dans :

* le titre ;
* le résumé ;
* les tags ;
* la transcription.

Le projet documente la recherche plein texte sur ces champs.

---

# 25. PHASE 17 — Test Collections

Créer au minimum :

```text
TEST
```

Puis affecter un contenu.

Vérifier :

```text
Library
   ↓
Collections
   ↓
TEST
   ↓
Contenu
```

---

# 26. PHASE 18 — Test Offline

C'est une étape essentielle.

Après avoir synchronisé plusieurs contenus :

1. couper temporairement le Wi-Fi du smartphone ;
2. ouvrir SuperBrain ;
3. consulter la bibliothèque ;
4. rechercher un contenu existant.

La v2.0 documente explicitement l'utilisation d'une base SQLite locale et le fonctionnement offline-first.

### Résultat attendu

Les données déjà synchronisées restent accessibles.

---

# 27. PHASE 19 — Test de resynchronisation

Réactiver le Wi-Fi.

Puis :

```text
SuperBrain
   ↓
Synchronisation
   ↓
Backend
```

Créer ensuite un nouveau contenu et vérifier son apparition.

---

# 28. PHASE 20 — Test Watch Later

Ajouter un contenu à :

```text
Watch Later
```

Vérifier que le système de notification fonctionne.

Le projet prévoit des notifications et des créneaux horaires spécifiques.

---

# 29. PHASE 21 — Instagram : uniquement maintenant

**Instagram doit être le dernier connecteur activé.**

Pourquoi ?

Parce qu'il constitue la partie la plus fragile de l'architecture.

Le backend utilise Instaloader et peut fonctionner avec une session Instagram authentifiée.

---

# 30. PHASE 22 — Premier test Instagram sans authentification

Commencer par une URL Instagram publique.

```text
Instagram
    ↓
Partager
    ↓
SuperBrain
```

### Objectif

Déterminer si l'accès anonyme fonctionne.

Le code prévoit explicitement un mode anonyme et avertit que certains contenus peuvent nécessiter une authentification.

---

# 31. PHASE 23 — Instagram authentifié

**Cette étape n'est exécutée que si l'étape précédente échoue pour des contenus légitimes que vous devez analyser.**

Le projet prévoit :

```text
INSTAGRAM_USERNAME
INSTAGRAM_PASSWORD
```

puis création d'une session Instaloader.

### Règle opérationnelle

Utiliser un compte Instagram dédié si cette fonction doit être activée de manière permanente.

Je déconseille d'utiliser immédiatement le compte Instagram personnel principal.

---

# 32. PHASE 24 — Ne pas utiliser le fallback `sessionid`

Le script fournit un mécanisme permettant de copier manuellement le cookie `sessionid` depuis le navigateur.

### Décision du plan maître

**Cette méthode est interdite dans le déploiement standard.**

Raison :

Un cookie de session authentifié est un secret extrêmement sensible.

Si ce cookie est compromis, le risque est nettement supérieur à celui d'un simple mot de passe exposé.

---

# 33. PHASE 25 — Vérification finale fonctionnelle

Le système doit maintenant réussir les tests suivants :

| Test                  | Résultat attendu              |
| --------------------- | ----------------------------- |
| Backend démarre       | PASS                          |
| `/health`             | PASS                          |
| Android → backend     | PASS                          |
| URL Web               | PASS                          |
| Analyse IA            | PASS                          |
| YouTube               | PASS                          |
| Recherche             | PASS                          |
| Collection            | PASS                          |
| Offline               | PASS                          |
| Resynchronisation     | PASS                          |
| Notifications         | PASS                          |
| Instagram public      | PASS ou limitation documentée |
| Instagram authentifié | seulement si nécessaire       |

---

# 34. PHASE 26 — Sécurisation finale

Avant utilisation réelle :

### 34.1 Ne pas exposer le port 5000 sur Internet

Pas de :

```text
ngrok
port forwarding
IP publique
```

dans la configuration initiale.

### 34.2 Protéger le token

Le token ne doit jamais être publié.

### 34.3 Protéger les clés IA

Les clés :

```text
GEMINI_API_KEY
GROQ_API_KEY
OPENROUTER_API_KEY
```

doivent rester dans les fichiers locaux prévus à cet effet.

Le dépôt exclut notamment les fichiers `.api_keys` du contrôle Git.

---

# 35. PHASE 27 — Sauvegarde

La donnée personnelle créée par SuperBrain doit être sauvegardée.

Le plan minimal :

```text
SuperBrain
     │
     ▼
Base SQLite
     │
     ▼
Sauvegarde périodique
     │
     ▼
Stockage secondaire
```

### Important

Le dépôt documente SQLite comme stockage principal mais ne fournit pas dans les sources examinées ici une stratégie complète de sauvegarde utilisateur.

Donc :

**la politique de sauvegarde doit être définie séparément.**

---

# 36. PHASE 28 — Critère de mise en production

SuperBrain ne passe en utilisation réelle que lorsque les conditions suivantes sont réunies :

```text
[✓] Backend stable
[✓] Android connecté
[✓] IA fonctionnelle
[✓] Recherche fonctionnelle
[✓] Offline fonctionnel
[✓] Synchronisation fonctionnelle
[✓] Notifications fonctionnelles
[✓] Secrets protégés
[✓] Aucun port Internet exposé
[✓] Sauvegarde définie
```

Si une condition critique est absente :

**PAS DE PASSAGE EN PRODUCTION.**

---

# 37. Feuille de route maîtresse condensée

```text
ÉTAPE 01
Définir serveur + smartphone
        ↓
ÉTAPE 02
Préparer réseau local
        ↓
ÉTAPE 03
Installer Node.js 20+
        ↓
ÉTAPE 04
Installer Python 3.10+
        ↓
ÉTAPE 05
Installer ffmpeg
        ↓
ÉTAPE 06
Installer SuperBrain Server
        ↓
ÉTAPE 07
Configurer Gemini
        ↓
ÉTAPE 08
Démarrer backend
        ↓
ÉTAPE 09
Valider /health
        ↓
ÉTAPE 10
Récupérer IP serveur
        ↓
ÉTAPE 11
Récupérer Access Token
        ↓
ÉTAPE 12
Télécharger APK
        ↓
ÉTAPE 13
Vérifier SHA-256
        ↓
ÉTAPE 14
Installer APK Android
        ↓
ÉTAPE 15
Configurer URL backend
        ↓
ÉTAPE 16
Configurer Access Token
        ↓
ÉTAPE 17
Valider connexion Android
        ↓
ÉTAPE 18
Tester Web
        ↓
ÉTAPE 19
Tester IA
        ↓
ÉTAPE 20
Tester YouTube
        ↓
ÉTAPE 21
Tester transcription
        ↓
ÉTAPE 22
Tester recherche
        ↓
ÉTAPE 23
Tester collections
        ↓
ÉTAPE 24
Tester Offline
        ↓
ÉTAPE 25
Tester synchronisation
        ↓
ÉTAPE 26
Tester notifications
        ↓
ÉTAPE 27
Tester Instagram public
        ↓
ÉTAPE 28
Instagram authentifié uniquement si nécessaire
        ↓
ÉTAPE 29
Sécuriser secrets + réseau
        ↓
ÉTAPE 30
Mettre en place sauvegarde
        ↓
ÉTAPE 31
Validation finale
        ↓
        ▼
       GO
        ↓
 SUPERBRAIN
 OPÉRATIONNEL
```

---

# 38. Architecture finale recommandée

Le résultat final doit rester volontairement simple :

```text
                 ┌───────────────────────┐
                 │     ANDROID PHONE     │
                 │                       │
                 │    SuperBrain APK     │
                 │                       │
                 │  SQLite local / cache │
                 └───────────┬───────────┘
                             │
                         Wi-Fi LAN
                             │
                             ▼
                 ┌───────────────────────┐
                 │       SERVEUR         │
                 │                       │
                 │  superbrain-server   │
                 │                       │
                 │       FastAPI         │
                 │          │            │
                 │       SQLite         │
                 │          │            │
                 │    ┌─────┴─────┐      │
                 │    │           │      │
                 │  Gemini      Ollama   │
                 │    │           │      │
                 │  Groq     OpenRouter  │
                 │                       │
                 └───────────────────────┘
```

---

# 39. Verdict stratégique

**Le déploiement Android de SuperBrain est réalisable, mais il faut conserver une distinction fondamentale : SuperBrain n'est pas une application Android autonome dans son architecture actuelle.**

Le smartphone est principalement le **client de capture, consultation et synchronisation**.

Le serveur est le **cerveau de traitement**.

Le projet documente explicitement cette séparation Android/backend.

Et c'est précisément la raison pour laquelle je recommande **de ne pas chercher à faire tourner immédiatement tout SuperBrain directement sur le smartphone**.

La trajectoire robuste est :

> **Android = interface + capture + mémoire locale**
> **Serveur = extraction + IA + orchestration + stockage maître**

Enfin, le projet est explicitement présenté comme une **beta précoce** dans sa release v2.0.0 ; il faut donc traiter cette installation comme un **déploiement contrôlé**, pas comme l'installation d'un produit mature et garanti.

**Sources primaires :**

* GitHub — SuperBrain : [https://github.com/sidinsearch/superbrain](https://github.com/sidinsearch/superbrain)
* README / architecture et installation :
* Release v2.0.0 / APK / SHA-256 :
* Model Router :
* API / authentification :
* Instagram Downloader :
* Instagram Login :
* Dépendances :
* Licence AGPL v3 :

