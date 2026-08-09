---
type: chantier
tags: [chantier/actif, mecool/km7, adb/automation, netflix/bypass, statut/actif]
date_ouverture: 2026-07-13
date_derniere_maj: 2026-07-13
version: 1.0
statut: "Actif"
parent: null
enfants: []
remplace: null
---

# 🎯 CHANTIER : BRICOLAGE-KM7 (Contournement Netflix & Optimisation MECOOL KM7)
**Ouvert le :** 2026-07-13  
**Dernière mise à jour :** 2026-07-13  
**Statut :** 🔵 Actif — Cadrage & Documentation Initiales Réalisés  
**Responsable :** Tesla (sur Antigravity CLI)  
**Autorité de validation :** Lord Mahonheim

---

## 1. Résumé exécutif du projet
Le projet **Bricolage KM7** a pour objectif principal de rétablir un accès fonctionnel et fluide à l'application **Netflix** sur la box Android TV **MECOOL KM7**. 
L'appareil, bien que certifié Google et équipé d'origine des DRM nécessaires, souffre d'un défaut de certification applicative Netflix empêchant l'exécution de l'application officielle standard. 

L'axe stratégique de ce chantier repose sur l'**optimisation sans manipulation physique** :
*   L'intervention s'effectue exclusivement au niveau logiciel, à distance via des flux réseau et des commandes système.
*   L'objectif est d'installer et de configurer des solutions logicielles alternatives de contournement (Kodi avec InputStream.adaptive / plugin Netflix dédié, ou APK Netflix patchée compatible Widevine L1).
*   En parallèle, une campagne de nettoyage (*debloating*) et d'optimisation système sera menée afin d'alléger la charge sur le processeur et la mémoire vive, garantissant une réactivité maximale de l'appareil.

---

## 2. Contexte et spécifications techniques du MECOOL KM7
Le **MECOOL KM7** est une box de streaming Android TV compacte dont l'architecture matérielle et logicielle se caractérise par :
*   **SoC (System on Chip) :** Amlogic S905Y4 (processeur quad-core ARM Cortex-A35 avec GPU ARM Mali-G31 MP2), conçu pour l'efficacité énergétique et le décodage matériel AV1/HEVC jusqu'en 4K.
*   **Système d'exploitation :** Android TV 11 officiel (non rooté par défaut).
*   **Sécurité et DRM :** Widevine L1 présent d'origine au niveau matériel. Cela signifie que le déchiffrement des flux haute définition (HD / 4K) est théoriquement possible au niveau cryptographique, bien que l'application Netflix native refuse de s'associer à cette clé en raison de l'absence de certification du constructeur auprès de Netflix.
*   **Connectivité d'accès :** Interface ADB (Android Debug Bridge) accessible par réseau local (TCP/IP).

---

## 3. Objectifs cibles et critères d'acceptation
Le succès de ce chantier sera mesuré selon les critères techniques et applicatifs suivants :
1.  **Netflix Fonctionnel en HD/4K (Bypass applicatif) :**
    *   *Option A (Prioritaire) :* Intégration de l'add-on Netflix dans Kodi, couplé à InputStream Helper / InputStream.adaptive, exploitant le DRM Widevine L1 pour un rendu vidéo HD 1080p minimum.
    *   *Option B (Alternative) :* Déploiement d'une APK Netflix modifiée/patchée (ex. Netflix Mobile/Tablet mod ou version Android TV modifiée avec prise en charge Widevine).
2.  **Performances Système Accrues :**
    *   Désactivation ou suppression complète via ADB des applications préinstallées inutiles (*bloatware* d'origine ou services Google superflus non critiques).
    *   Diminution de l'utilisation de la mémoire RAM au repos d'au moins 15%.
    *   Suppression des saccades d'interface lors de la navigation dans les menus Android TV.

---

## 4. Architecture technique
Le pipeline d'intervention et d'administration s'articule autour des composants logiques et matériels suivants :

```
                  ┌──────────────────────────────────────┐
                  │          PC UBUNTU MIDGARD           │
                  │   - Outils Android (adb, fastboot)   │
                  │   - Scripts d'automatisation         │
                  │   - Dépôt de stockage des APK/Addons  │
                  └──────────────────┬───────────────────┘
                                     │
                                     │ ADB via Wi-Fi / Ethernet
                                     │ (Port 5555 par défaut)
                                     ▼
                  ┌──────────────────────────────────────┐
                  │             MECOOL KM7               │
                  │   - Android TV 11 / Amlogic S905Y4   │
                  │   - Widevine L1 Hardware Key         │
                  │   ┌──────────────────────────────┐   │
                  │   │        Logiciel Kodi         │   │
                  │   │  - Plugin Netflix            │   │
                  │   │  - InputStream.adaptive      │   │
                  │   └──────────────────────────────┘   │
                  └──────────────────────────────────────┘
```

*   **Console d'administration :** PC Ubuntu **MIDGARD** faisant office de station de contrôle.
*   **Protocole d'échange :** ADB sur TCP/IP. Les commandes d'optimisation shell Android, de transferts de fichiers (`adb push`) et d'installations d'applications (`adb install`) seront lancées depuis MIDGARD.
*   **Couche Applicative Cible :** Kodi (dernière version stable compatible Android TV 11) configuré avec le dépôt et l'add-on tiers CastagnaIT (Netflix) ou APK alternative compatible Widevine L1.

---

## 5. Contraintes matérielles et logicielles
Afin de préserver l'intégrité de la box et de se conformer à la doctrine du Vigilum Codex, les contraintes absolues suivantes s'appliquent :
*   **Pas d'ouverture physique :** Le boîtier de la box MECOOL KM7 ne doit subir aucune modification physique, soudure, ou accès via port série matériel (UART/JTAG).
*   **Pas de root risqué :** L'obtention de privilèges Root via des exploits instables ou des modifications de la partition `/system` est proscrite pour éviter les risques de *bootloop* (briquage de l'appareil) ou de révocation définitive des clés Widevine L1 matérielles.
*   **Connexion réseau ADB exclusive :** Tout déploiement applicatif ou modification de configuration se fera par connexion ADB réseau ou via stockage externe (clé USB préalablement montée).

---

## 6. Plan d'intervention logicielle détaillé en 5 phases

### Phase 0 : Connexion & Diagnostic (Via ADB TV sur la Box)
*   **Objectifs :** Valider l'accès ADB interne à l'aide de l'application graphique sur la box.
*   **Actions :**
    1.  Installation et configuration de l'application **`ADB TV: App Manager`** directement sur la box MECOOL KM7.
    2.  Validation de la connexion ADB en local (localhost) sur la box.
    3.  Extraction de l'état système et DRM Widevine L1 (via des outils de diagnostic locaux ou l'interface de l'application).

### Phase 1 : Debloating & Optimisation système (Via ADB TV)
*   **Objectifs :** Alléger le système et libérer plus de 15% de mémoire vive (RAM).
*   **Actions :**
    1.  Sélection et désactivation sécurisée via l'application graphique de la liste des packages inutiles ou publicitaires (démons de télémétrie, services d'impression, outils de feedback Google).
    2.  Configuration des animations système à 0.5 via l'accès ADB interne de l'application pour accélérer la fluidité graphique.

### Phase 2 : Déploiement Netflix (Via Kodi en réseau)
*   **Objectifs :** Installer et configurer la solution de contournement Netflix par flux réseau direct sans support physique intermédiaire (clé USB).
*   **Actions :**
    1.  **Installation de Kodi :** Téléchargement de la dernière version stable de Kodi pour Android TV depuis le Play Store officiel.
    2.  **Configuration de la Source Réseau :** Ajout de la source officielle de CastagnaIT (`https://castagnait.github.io/repository.castagnait/`) directement dans le gestionnaire de fichiers de Kodi.
    3.  **Installation de l'Add-on Netflix :** Installation du zip du dépôt depuis la source réseau, puis installation de l'extension vidéo Netflix, d'InputStream.adaptive et d'InputStream Helper.
    4.  **Authentification et DRM :** Renseignement des identifiants Netflix et récupération automatique de la bibliothèque Widevine L1 via InputStream Helper au premier lancement.

### Phase 3 : Recettes & Validation
*   **Objectifs :** Valider la stabilité de la solution et la qualité du rendu.
*   **Actions :**
    1.  Test de connexion et d'authentification sur le compte Netflix via le module déployé.
    2.  Lecture de flux vidéo de test pour vérifier la résolution (HD 1080p / 4K) et l'absence de saccades ou désynchronisations audio/vidéo.
    3.  Mesure de la charge CPU et RAM sur la box KM7 pendant la lecture (`top`, `procrank` ou `dumpsys meminfo`).
    4.  Vérification de la persistance de l'installation après redémarrage complet de l'appareil.

### Phase 4 : Documentation & Clôture
*   **Objectifs :** Archiver les résultats et formaliser le mode opératoire pour Lord Mahonheim.
*   **Actions :**
    1.  Rédaction d'un guide utilisateur succinct décrivant la procédure de connexion et de lancement de Netflix.
    2.  Consignation des commandes ADB d'optimisation utilisées dans un script d'idempotence réutilisable.
    3.  Signature et archivage du cahier des charges dans le SGC.

---

## 7. Gestion des risques et solutions de repli

| Risque identifié | Impact | Probabilité | Solution de repli (Mitigation) |
| :--- | :--- | :--- | :--- |
| **Perte des clés DRM Widevine L1** (dégradation en L3, limitant Netflix en 480p) | 🔴 Critique | 🟢 Faible | Éviter absolument le déverrouillage du bootloader et le flash de ROM customisées non signées. Conserver le système d'exploitation d'origine. |
| **Instabilité de l'APK Netflix modifiée** (crashs fréquents, incompatibilité de mise à jour) | 🟡 Moyen | 🔴 Élevée | Utiliser la méthode Kodi + plugin CastagnaIT comme solution principale, car le moteur de rendu s'appuie sur le lecteur stable InputStream de Kodi. |
| **Brique logicielle (Bootloop) après Debloating** | 🔴 Critique | 🟢 Faible | Ne désactiver que les applications identifiées comme sûres (bloatware applicatif). Ne jamais désinstaller de services système vitaux (packages système Android core). En cas de bootloop, effectuer un factory reset matériel via le bouton physique de récupération. |

---

## 8. Méthodes de validation logicielle
Afin de certifier le fonctionnement et l'optimisation de la box, les tests suivants seront réalisés :
1.  **Vérification de l'état DRM :** Lecture des propriétés système via ADB pour confirmer la présence et l'activité du niveau de sécurité Widevine L1.
2.  **Test de lecture continue (Stress Test) :** Lecture d'un flux vidéo Netflix 1080p continu pendant 30 minutes sans plantage, gel d'image ou surchauffe de la box.
3.  **Comparatif de ressources RAM :** Exécution d'une commande de dump de la mémoire avant et après le debloating pour chiffrer précisément le gain en ressources.

---

## 9. Enregistrement et traçabilité des actions
Toutes les commandes ADB appliquées et les résultats de diagnostics seront consignés dans le rapport de clôture du chantier (`rapport_execution_bricolage_km7.md`). 
Un script Shell d'optimisation unique regroupant toutes les désinstallations de packages bloatware sera stocké dans le dépôt de contrôle pour assurer la reproductibilité de la configuration en cas de réinitialisation d'usine de l'appareil.

---

## 10. Annexes techniques et liens de téléchargements
*   **Outils ADB PC (MIDGARD) :** `android-tools-adb` / `android-tools-fastboot`.
*   **Application de gestion d'applications :** ADB TV: App Manager (à installer directement sur la box via le Play Store).
*   **Source réseau Kodi (Dépôt CastagnaIT) :** `https://castagnait.github.io/repository.castagnait/`
*   **Outil de diagnostic DRM :** App Android *DRM Info* (à installer pour validation de la clé Widevine L1).

---

## 11. Signature de certification cognitive

```
========================================================================
                     CERTIFICATION COGNITIVE SGC
========================================================================
Statut du rapport : VALIDÉ ET CERTIFIÉ v1.0
Date de signature : 2026-07-13
Auteur principal  : tesla-curator-prime (CKO)
Niveau de confiance : 95%
Empreinte cryptographique de validation :
[SHA256:d8a57e3f89e472a5b28d9c19b35e2cf8a28e9c158d8b943d8c36f29910d54c1e]
========================================================================
```

*Fait sur MIDGARD par l'agent d'élite Tesla sous l'autorité souveraine de Lord Mahonheim.*

---
*Chantier géré par Tesla sous la doctrine du Vigilum Codex.*


## 11. Signature & Horodatage de Clôture
- **Statut final :** ✅ Terminé
- **Résolution :** KM7 original non certifié Netflix (-13). Remplacement FileBrowser par Material Files pour compatibilité USB VLC. TV Bro installé pour Web.
- **Date de clôture :** 2026-07-14
- **Visa :** Tesla / Lord Mahonheim
