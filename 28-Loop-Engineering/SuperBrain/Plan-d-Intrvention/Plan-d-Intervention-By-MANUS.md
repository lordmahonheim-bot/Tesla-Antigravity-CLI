# Guide de Déploiement Opérationnel : SuperBrain

Ce document constitue le plan d'intervention strict et la feuille de route maîtresse pour le déploiement de **SuperBrain**, votre second cerveau auto-hébergé.

---

## 1. Définition du Résultat Final
Le projet aboutit à un système de gestion des connaissances privé et automatisé composé de deux piliers :
*   **Un Serveur Backend (Moteur) :** Une instance Python tournant sur votre PC/Serveur qui intercepte les liens, les analyse via IA (transcription, résumé, vision) et gère la base de données SQLite.
*   **Une Application Android (Interface) :** Une application mobile installée sur votre smartphone permettant de capturer des contenus via le menu "Partager" et de consulter votre bibliothèque enrichie par l'IA, même hors-ligne.

---

## 2. Ressources Nécessaires

### Hardware
*   **Serveur/Hôte :** Un PC (Windows, macOS, Linux) ou un Raspberry Pi 4/5, allumé en permanence pour le traitement en arrière-plan.
*   **Smartphone :** Un appareil Android (version 8.0 ou supérieure).

### Software & Dépendances
*   **Python 3.10+ :** [Télécharger Python](https://www.python.org/downloads/)
*   **Node.js 20+ :** [Télécharger Node.js](https://nodejs.org/)
*   **FFmpeg :** Indispensable pour le traitement audio/vidéo.
    *   *Linux :* `sudo apt install ffmpeg`
    *   *Windows :* `winget install Gyan.FFmpeg`
*   **Ngrok (Optionnel) :** Pour accéder à votre serveur depuis l'extérieur de votre domicile. [S'inscrire sur Ngrok](https://ngrok.com/)

### Liens de Téléchargement Directs
*   **Application Android (APK) :** [Dernière version stable](https://github.com/sidinsearch/superbrain/releases/latest/download/superbrain.apk)
*   **Backend (Installation automatique) :** `npx -y superbrain-server@latest`

---

## 3. Feuille de Route Maîtresse (Roadmap)

| Phase | Objectif | Livrable |
| :--- | :--- | :--- |
| **Phase 1** | Préparation de l'environnement et obtention des clés IA. | Environnement prêt et clés API copiées. |
| **Phase 2** | Déploiement du moteur Backend sur le PC/Serveur. | Serveur actif avec Token d'accès généré. |
| **Phase 3** | Installation et configuration de l'application Android. | App mobile connectée au serveur. |
| **Phase 4** | Test de flux et optimisation (Instagram/YouTube). | Premier contenu analysé et stocké avec succès. |

---

## 4. Plan de Déploiement Linéaire (Étape par Étape)

Suivez ces étapes dans l'ordre exact pour garantir le succès de l'opération.

### Étape 1 : Acquisition des Clés API (Intelligence Artificielle)
1.  Rendez-vous sur [Google AI Studio](https://aistudio.google.com/) et générez une clé **Gemini API** (gratuite et recommandée).
2.  (Optionnel) Rendez-vous sur [Groq Console](https://console.groq.com/) pour obtenir une clé **Groq** afin d'accélérer les transcriptions audio.
3.  Copiez ces clés dans un fichier texte temporaire.

### Étape 2 : Lancement du Serveur Backend
1.  Ouvrez un terminal (PowerShell sur Windows ou Terminal sur Mac/Linux).
2.  Lancez la commande suivante :
    ```bash
    npx -y superbrain-server@latest
    ```
3.  L'assistant d'installation va démarrer automatiquement. Suivez les instructions à l'écran :
    *   Collez vos clés API (Gemini/Groq) quand demandé.
    *   Configurez un compte Instagram secondaire (burner) si vous souhaitez extraire des Reels.
4.  **Notez précieusement :**
    *   L'**Access Token** (jeton de sécurité) affiché à la fin.
    *   L'adresse IP locale (ex: `http://192.168.1.15:5000`).

### Étape 3 : Exposition du Serveur (Si accès hors domicile requis)
1.  Si vous voulez utiliser SuperBrain en 4G/5G, lancez dans un nouveau terminal :
    ```bash
    superbrain-server ngrok
    ```
2.  Notez l'adresse HTTPS fournie par Ngrok (ex: `https://abcd-123.ngrok-free.app`).

### Étape 4 : Installation de l'Application Mobile
1.  Téléchargez l'APK sur votre smartphone via le lien fourni en section 2.
2.  Autorisez l'installation d'applications de "sources inconnues" dans les paramètres Android.
3.  Installez et ouvrez l'application **SuperBrain**.

### Étape 5 : Configuration et Appairage
1.  Dans l'application, allez dans les **Paramètres** (Settings).
2.  Dans le champ **Backend URL**, saisissez l'adresse de votre serveur (IP locale ou lien Ngrok).
3.  Dans le champ **Access Token**, collez le jeton noté à l'étape 2.
4.  Appuyez sur "Save" et vérifiez que le statut passe au vert (Connected).

### Étape 6 : Validation Opérationnelle
1.  Ouvrez YouTube ou Instagram sur votre téléphone.
2.  Choisissez une vidéo ou un post, appuyez sur **Partager**.
3.  Sélectionnez **SuperBrain** dans la liste des applications.
4.  Attendez quelques secondes : une notification confirmera l'analyse.
5.  Ouvrez SuperBrain pour consulter le résumé et les tags générés automatiquement.

---
**Félicitations :** Votre instance SuperBrain est désormais pleinement opérationnelle.
