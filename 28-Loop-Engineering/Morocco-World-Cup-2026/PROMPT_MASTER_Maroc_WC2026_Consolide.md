# PROMPT MASTER --- Page HTML « Lions de l'Atlas : Parcours Mondial 2026 » (Version consolidée)

> À copier-coller tel quel dans Gemini (Antigravity).

## 1. RÔLE & MISSION

Tu es un développeur front-end senior, directeur artistique et
documentaliste web spécialisé dans les expériences sportives immersives.

Ta mission est de concevoir une **page web locale, autonome, sans
serveur**, retraçant le parcours du Maroc à la Coupe du Monde FIFA 2026
sous la forme d'une timeline interactive.

Avant toute génération de code, effectue une **recherche documentaire
complète** afin de : - vérifier les données sportives auprès des sources
officielles FIFA ; - vérifier les statistiques, les hommes du match et
les résultats ; - identifier les photographies réelles correspondant à
chaque highlight.

En cas de divergence entre ce prompt et les données officielles FIFA,
**les données FIFA prévalent**.

## 2. CONTEXTE

-   Fonctionnement 100 % local (`file://`)
-   Aucun serveur
-   Aucun build
-   JavaScript Vanilla ES6+
-   HTML5 + CSS3 modernes
-   Responsive
-   Accessible
-   Code commenté en français

## 3. ARBORESCENCE

maroc-wc2026/ - index.html - style.css - data.js - app.js - images/

Ne jamais utiliser fetch().

Toutes les données vivent dans :

const APP_DATA = { ... }

## 4. DIRECTION ARTISTIQUE

(Conserver la direction artistique Dark Premium × Maroc décrite dans la
version d'origine.)

## 5. STRUCTURE

Conserver les dix sections prévues.

Les statistiques du Hero doivent être calculées automatiquement à partir
de APP_DATA et ne jamais être codées en dur.

La timeline doit être totalement évolutive.

## 6. DONNÉES

Utiliser exclusivement les données officielles FIFA les plus récentes.

Hommes du match FIFA :

-   Brésil 1-1 Maroc → Ismael Saibari
-   Maroc 1-0 Écosse → Ismael Saibari
-   Maroc 4-2 Haïti → Achraf Hakimi
-   Pays-Bas 1-1 Maroc (3-2 TAB) → Yassine Bounou

Dans la timeline, mettre également en valeur les actions décisives (ex.
but égalisateur d'Issa Diop), même lorsque le joueur n'est pas
officiellement Homme du match.

## 7. IMAGES

Pour chaque highlight, joueur, membre du staff et section importante :

Rechercher sur Internet une photographie réelle pertinente.

Ne jamais générer d'image avec l'IA.

Ordre de priorité :

1.  FIFA
2.  FRMF
3.  Club
4.  Agence de presse reconnue

Télécharger les images autorisées dans :

images/

Nommer les fichiers de manière explicite.

Référencer toutes les images dans data.js.

Si aucune image exploitable n'est disponible :

Créer uniquement un placeholder SVG.

Interdictions :

-   aucune image IA
-   aucune illustration fictive
-   aucun CDN
-   aucune URL distante dans la version finale

## 8. MAINTENABILITÉ

Toute mise à jour du tournoi doit uniquement nécessiter :

-   modification de APP_DATA.prochainMatch
-   ajout d'un objet dans timeline
-   mise à jour des statistiques

Le reste de l'application ne doit jamais être modifié.

## 9. RÈGLES IMPORTANTES

Ne jamais écrire de texte métier directement dans app.js.

Tout doit provenir de APP_DATA.

Aucune date, score, statistique ou texte ne doit être codé en dur.

## 10. CRITÈRES D'ACCEPTATION

-   fonctionne par double-clic
-   aucune erreur console
-   aucune dépendance
-   responsive
-   timeline évolutive
-   hommes du match conformes à la FIFA
-   statistiques dynamiques
-   aucune image générée par IA
-   uniquement des photos réelles recherchées sur Internet ou des
    placeholders SVG
