# 🛠️ Plan d'Intervention EXTRA : Résolution Lecture USB sur KM7

## 1. Goal Description & Contexte
L'objectif de ce plan est d'identifier et de résoudre la perte soudaine de la capacité de lecture vidéo depuis un périphérique de stockage USB sur le boîtier MECOOL KM7. 
Les symptômes (File Browser voit les fichiers mais ne peut pas déléguer l'ouverture ; VLC voit la clé mais les dossiers semblent vides) excluent un problème de codec vidéo ou de panne USB matérielle totale. 

Conformément à la synthèse des audits d'Apodex et RENA, le diagnostic converge vers une **régression des droits d'accès au stockage (Scoped Storage Android 11)** ou, plus probablement, **une désactivation accidentelle d'un fournisseur de médias/documents système lors du récent chantier de nettoyage (debloating)**.

Ce plan "EXTRA" adopte une approche chirurgicale : nous allons interroger le système via notre liaison ADB active (`192.168.11.107:5555`) pour prouver l'origine du blocage avant d'exécuter la moindre correction.

---

## 2. User Review Required
> [!WARNING]
> **Suspicion d'effet de bord du chantier précédent**
> L'une des hypothèses les plus fortes est que le script de nettoyage `km7_debloat.sh` exécuté précédemment a désactivé un package système tel que `DocumentsUI`, `ExternalStorageProvider` ou `MediaProvider`, ce qui explique parfaitement pourquoi VLC est devenu "aveugle" et File Browser incapable de transmettre l'Intention d'ouverture. Nous vérifierons cela en Priorité Absolue.

> [!CAUTION]
> **Interdiction d'action destructrice prématurée**
> Aucune réinitialisation de l'application VLC (`pm clear`), aucune réinstallation d'application et aucun reformatage de clé USB ne seront effectués tant que l'audit ADB non-destructif n'aura pas rendu son verdict.

---

## 3. Proposed Changes & Séquence Opérationnelle

### Phase 1 : Audit de l'Intégrité Système et du "Debloating"
Nous allons vérifier si un composant natif de gestion de fichiers a été désactivé à tort.
#### [NOUVELLES MESURES] Collecte d'état
1. **Recherche de composants de stockage désactivés :**
   Exécution de `adb shell pm list packages -d` filtré sur `documentsui`, `externalstorage`, `providers.media` et `providers.downloads`.
2. **Re-montage USB logiciel :**
   Exécution de `adb shell sm list-volumes all` et `adb shell ls -la /storage` pour confirmer que le noyau Android voit toujours la clé avec ses droits de lecture.

### Phase 2 : Audit des Permissions Applicatives (VLC & File Browser)
Nous allons vérifier que le Scoped Storage d'Android 11 n'a pas révoqué silencieusement les droits.
#### [NOUVELLES MESURES] Extraction des AppOps
1. Extraction des permissions de VLC : `adb shell dumpsys package org.videolan.vlc`.
2. Vérification de l'état `granted` ou `denied` sur `READ_EXTERNAL_STORAGE`.

### Phase 3 : Capture du Défaut en Direct (Logcat)
Si les permissions semblent normales, nous allons "filmer" le refus en interne.
#### [NOUVELLES MESURES] Logcat instrumenté
1. Déclenchement de la trace avec `adb logcat -c`.
2. L'utilisateur (ou l'agent via `monkey`) tente d'ouvrir le dossier vide dans VLC ou lance le film via File Browser.
3. Capture ciblée des mots-clés : `permission|denied|storage|SecurityException|EACCES|intent`.

### Phase 4 : Remédiation Graduelle
Une fois la preuve trouvée, j'appliquerai la solution correspondante dans cet ordre de priorité :
1. **Restauration Système** : Si un fournisseur système a été désactivé, exécution de `adb shell pm enable <nom_package>`.
2. **Forçage des Droits** : Si les AppOps ont sauté, restauration via ADB `pm grant org.videolan.vlc android.permission.READ_EXTERNAL_STORAGE` (ou demande via l'interface TV).
3. **Réinitialisation Locale** : Si le système est intègre mais que la base de VLC a corrompu son index USB, exécution d'un nettoyage de cache de VLC.

---

## 4. Verification Plan

### Automated Tests (ADB)
- Vérification que la liste des paquets désactivés ne contient aucun composant critique :
  `adb shell pm list packages -d | grep -E "documentsui|externalstorage|media"` (doit être vide ou ne contenir que des apps explicitement interdites).
- Lecture directe d'un fichier de test via le shell pour prouver que le noyau a l'accès :
  `adb shell ls -lah /storage/XXXX-XXXX/`

### Manual Verification
1. Vous devrez brancher la clé USB que vous utilisiez habituellement.
2. Si la Phase 3 est requise, je vous demanderai de tenter de lancer le film depuis File Browser pendant que je capture l'erreur de votre écran.
3. Vous constaterez le rétablissement de la lecture sans avoir eu à formater votre clé.
