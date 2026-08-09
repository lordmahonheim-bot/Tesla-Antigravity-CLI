# 🕵️ PROMPT ULTIME — Manuel d'instructions interactif du Cluedo « Qui a tué Mat Lenoir ? »

> **Ce que contient ce fichier :**
> 1. **Le Prompt ultime** (bloc à copier-coller) → la commande complète à donner à une IA génératrice de code (Claude, ChatGPT, Gemini, etc.)
> 2. **Annexe A — Fiche technique du jeu** (données vérifiées : suspects, armes, pièces, contenu, règles) → à coller en complément du prompt
> 3. **Annexe B — Contenu des 14 photos** (ce qu'elles montrent) → pour cibler l'analyse
> 4. **Annexe C — Règles brutes reconstituées** (texte de référence fidèle aux photos)

---

## 🚀 Comment utiliser ce prompt (30 secondes)

1. **Copie** le bloc « ═══ LE PROMPT ═══ » ci-dessous (il est autonome et contient toutes les données du jeu).
2. **Colle-le** dans ton IA préférée (mode « code » ou « agent ») **en joignant les 14 photos** (`1.jpeg` → `14.jpeg`).
3. **Récupère** le fichier `cluedo-manuel-interactif.html` généré et ouvre-le en double-cliquant : tout fonctionne hors ligne, tout est cliquable.
4. Si l'IA te demande des précisions : **colle aussi les Annexes A et B** — elles répondent à tout.

---

════════════════════════════════════════════════════════════════════════════════════

# ═══ LE PROMPT ═══
*(copie tout ce qui se trouve entre les deux lignes de ═══, y compris ce titre)*

# PROMPT ULTIME : Crée le manuel d'instructions interactif du jeu Cluedo « Qui a tué Mat Lenoir ? »

## 1. TON RÔLE
Tu es simultanément :
- un **rédacteur pédagogique expert** (tu sais expliquer une règle de jeu à un enfant de 8 ans comme à un adulte pressé, sans jargon, avec des exemples et des pièges à éviter) ;
- un **directeur artistique** spécialisé dans l'univers « détective / film noir » ;
- un **développeur front-end senior** (HTML5 / CSS3 / JavaScript vanilla) capable de produire une application monopage d'une qualité professionnelle, entièrement hors ligne, dans un seul fichier.

**Ta mission :** produire le **manuel d'instructions complet, détaillé et explicatif** de ce jeu Cluedo sous la forme d'une **page HTML locale interactive**, où **CHAQUE élément est cliquable et interactif** — rien ne doit être statique, aucun texte ne doit être un simple paragraphe mort : tout réagit (survol, clic, animation, ouverture, bascule…).

## 2. LE JEU CONCERNÉ (contexte vérifié — à recouper avec les photos)
Il s'agit de l'édition **Cluedo 2023 de Hasbro — « Qui a tué Mat Lenoir ? »**, sous-titrée **« Le Manoir Tudor »** (réf. F6420, © 2023 Hasbro). Victime : **M. Mat Lenoir, dit « le Macchabé »**, assassiné dans son manoir Tudor après avoir annoncé à ses invités un projet d'hôtel de luxe construit sur un parc public populaire, puis révélé qu'il possédait des informations compromettantes pour les faire chanter. La partie répond à 3 questions : **QUI ? AVEC QUOI ? OÙ ?**

### 2.1 Les 6 suspects (QUI ?) — couleurs officielles de l'édition française
| Suspect | Métier / histoire (résumé) | Couleur |
|---|---|---|
| **Mlle Rose** | Journaliste d'investigation, écrit sous le pseudonyme « Cyan » ; a fait mettre des mafieux en prison. | Rouge |
| **Colonel Moutarde** | Héros de guerre décoré… mais n'a en réalité jamais combattu la bataille de sa médaille. | Jaune |
| **M. le Maire Olive** | Maire sympathique du Comté Coloris, en campagne de réélection ; a reçu un don d'une famille criminelle. | Vert |
| **Maître Pervenche** | Avocate tenace, prête à tout pour gagner, y compris utiliser de faux témoins. | Bleu |
| **Prof. Violet** | Professeur d'antiquités perspicace ; identifie les contrefaçons… et en fabrique. | Violet |
| **Cheffe Leblanc** | Cheffe cuisinière réputée ; tout le monde adore ses plats. | Blanc |

### 2.2 Les 6 armes (AVEC QUOI ?)
**Chandelier** · **Poignard** · **Barre de fer** · **Révolver** · **Corde** · **Clé anglaise**

### 2.3 Les 9 pièces du manoir (OÙ ?)
**Salle de réception** · **Salle de billard** · **Jardin d'hiver** · **Salle à manger** · **Entrée** · **Cuisine** · **Bibliothèque** · **Salon** · **Bureau**
- **Passages secrets** (à confirmer sur la photo du plateau) : **Cuisine ↔ Bureau** et **Jardin d'hiver ↔ Salon**.
- Plan standard de l'édition (si la photo du plateau est illisible) : Bureau (coin haut-gauche), Entrée (haut-centre), Salon (coin haut-droit), Bibliothèque (gauche haute), Salle à manger (droite), Salle de billard (gauche basse), Jardin d'hiver (coin bas-gauche), Salle de réception (bas-centre), Cuisine (coin bas-droit). Couloirs en forme de croix au centre, **cases de départ colorées** devant certaines portes, **porte(s) d'entrée de chaque pièce** matérialisée(s).

### 2.4 Contenu de la boîte (50 cartes au total)
- 1 plateau de jeu · 6 pions Personnage (sculptés) · 6 pions Arme (métal doré) · 2 dés (1 dé classique à 6 faces + **1 dé spécial rouge avec icône(s) loupe**) · 1 **étui confidentiel** · 1 **carnet de détective** (feuilles à cocher) · 50 cartes = **6 cartes Personnage + 6 cartes Arme + 9 cartes Pièce + 29 cartes Indice**.
- 2 à 6 joueurs (mode classique 3-6 ; **variante 2 joueurs** prévue) · dès 8 ans · partie ≈ 45 min.

### 2.5 Les règles officielles (résumé fidèle — détail complet en section 5)
**Mise en place :** placer les 6 pions Personnage sur leurs cases de départ colorées (même si moins de joueurs) → chaque joueur choisit son personnage → placer chaque arme au hasard dans une pièce différente → écarter les 29 cartes Indice → trier les 21 autres cartes en 3 piles (Personnage / Arme / Pièce), glisser secrètement la carte du dessus de chaque pile dans **l'étui confidentiel** (la solution !), poser l'étui au centre du plateau, mélanger les cartes Indice en une pile face cachée à côté → mélanger et **distribuer toutes les cartes restantes** (déséquilibre possible) → donner une feuille du carnet de détective + un crayon (non inclus) à chaque joueur → chacun coche secrètement les cartes de sa main (elles ne peuvent pas être dans l'étui).

**À ton tour (2 dés) :**
1. **Déplacement** : jusqu'au nombre de cases indiqué (**la loupe rouge compte comme 1**). Interdit : diagonale, repasser deux fois sur la même case dans le même tour, traverser ou s'arrêter sur une case occupée par un autre pion (ni sur les portes). Entrer dans une pièce ne demande pas le nombre exact ; l'entrée se fait par une **porte non bloquée**. Déjà dans une pièce ? Pas obligé de bouger pour émettre une hypothèse ; un **passage secret** permet de passer directement dans la pièce reliée. **Loupe obtenue → pioche une carte Indice**, lis-la à voix haute, applique son effet, remets-la **sous** la pile (2 icônes loupe sur le dé = on ne pioche quand même qu'une seule carte).
2. **Hypothèse** (une fois dans une pièce) : « **[Personnage], avec [Arme], dans [la pièce où tu es]** ». Déplace le pion du suspect nommé ET le pion de l'arme dans cette pièce (ils y restent). Le joueur **à ta gauche** doit te montrer secrètement une de ces cartes s'il en a (il choisit laquelle) ; sinon le suivant, et ainsi de suite, jusqu'à ce qu'on te montre une carte. **Coche la carte montrée sur ta feuille** : elle n'est pas dans l'étui. Personne n'a de carte ? Ton hypothèse est probablement la bonne !
3. **Accusation** (facultative, une seule par partie, pendant ton tour, même juste après une hypothèse) : « **J'accuse [Personnage], avec [Arme], dans [Pièce]** ». Tu dois être dans une pièce, mais pas nécessairement celle nommée. Regarde **discrètement** l'étui : les 3 cartes y sont → **tu gagnes la partie !** Sinon → tu ne peux plus jouer de tours (mais tu continues de montrer tes cartes aux autres) ; la partie continue. Si personne n'accuse juste, le meurtrier s'échappe !

**Variante 2 joueurs :** après la mise en place classique (étapes 1-5), placer 4 cartes aléatoires face cachée dans 4 pièces (les coins du plateau pour une partie plus rapide) ; entrer dans une pièce contenant une carte → la regarder discrètement, cocher sa feuille, puis émettre son hypothèse normalement.

## 3. LES PHOTOS JOINTES SONT TA SOURCE DE VÉRITÉ
14 photos du jeu réel t'ont été fournies (plateau, règles, cartes, boîte). **Analyse-les toutes, méthodiquement**, avant d'écrire la moindre ligne de code :
- **Photos 5 à 8** : les pages du livret de règles (mise en place, tour de jeu, victoire, mode 2 joueurs, conseils) → **transcris fidèlement** chaque règle, dans l'ordre, sans rien omettre.
- **Photos 1 à 4** : les **29 cartes Indice** (recto/verso) → transcris **chacune** (titre, texte d'ambiance, effet exact). Effets observés : « Le joueur qui possède la carte X doit la montrer », « Tous les joueurs montrent secrètement une carte au joueur à leur gauche », « Nommez un personnage / une arme / une pièce que vous voulez éliminer », certaines cartes peuvent **ouvrir un passage secret** ou révéler des armes → vérifie et complète.
- **Photo 9** : les cartes Personnage / Arme / Pièce (illustrations + noms) → récupère les **visuels et noms exacts**.
- **Photo 10** : les biographies des suspects → utilise-les pour les portraits-texte.
- **Photo 11** : l'histoire du jeu + contenu de la boîte.
- **Photo 12** : le dos de la boîte (listes officielles, réf. F6420, © 2023 Hasbro).
- **Photo 13** : le **plateau de jeu** → reproduis son plan (positions des 9 pièces, couloirs, portes, cases de départ, passages secrets). Si l'angle rend la lecture difficile, utilise le plan standard de la section 2.3 et signale-le dans un commentaire.
- **Photo 14** : la boîte (visuel de couverture).

**Règle de priorité en cas de contradiction :** photo > données de la section 2 > connaissance standard du Cluedo classique. Tout point que tu ne peux pas vérifier doit être signalé par un commentaire `<!-- À VÉRIFIER : ... -->` dans le code, sans bloquer la génération.

## 4. LE LIVRABLE
Un **fichier unique** : `cluedo-manuel-interactif.html`
- **100 % autonome et hors ligne** : aucune ressource externe (pas de CDN, pas de police web, pas d'image externe, pas de framework) — tout est inline (CSS dans `<style>`, JS dans `<script>`, illustrations en **SVG inline** ou CSS). S'ouvre par simple double-clic, fonctionne sans Internet.
- **Entièrement en français** (langue, contenu, commentaires de code).
- **Responsive** : impeccable sur mobile, tablette et ordinateur.
- **Accessible** : sémantique HTML5, ARIA, navigation clavier complète.
- **Soigné** : c'est un objet dont on est fier — comme un beau carnet d'enquête interactif.

## 5. CONTENU OBLIGATOIRE DU MANUEL (aucune section ne peut manquer)
Organise la page en **sections navigables** (sidebar ou onglets) avec un fil conducteur narratif « vous êtes le détective ». Rédige **tous les textes toi-même** — jamais de « lorem ipsum », jamais de placeholder.

1. **Couverture immersive** : titre « CLUEDO — Qui a tué Mat Lenoir ? », ambiance manoir Tudor, bouton « Commencer l'enquête ».
2. **L'histoire** : la nuit du meurtre (invitation au manoir, annonce du projet d'hôtel, chantage, le cri, la découverte du corps) — présentée comme un rapport de police cliquable.
3. **Objectif du jeu + Aperçu en 30 secondes** : un résumé ultra-simple pour comprendre le principe avant de lire les détails.
4. **Contenu de la boîte** : inventaire interactif (chaque élément de la boîte est une carte cliquable avec son rôle).
5. **Les 6 suspects** : cartes cliquables à **effet flip 3D** (recto : portrait SVG + nom + couleur ; verso : métier, bio issue de la photo 10, mobile, anecdote). Chaque suspect a sa couleur de thème.
6. **Les 6 armes** : cartes cliquables avec **illustration SVG** de l'arme, son histoire, sa présence dans la boîte.
7. **Les 9 pièces + le plateau interactif** : un **plan SVG cliquable du manoir** — survol = surbrillance + infobulle ; clic = fiche complète de la pièce (description, couleur, portes, passage secret éventuel). Boutons de zoom, légende interactive, couches activables (portes / passages secrets / cases de départ).
8. **Les cartes Indice (29)** : explication du principe + **pile cliquable qui simule une pioche** (animation) + transcription des cartes réelles des photos 1-4, classées par type d'effet (révéler une carte / passer une carte à gauche / nommer et éliminer / ouvrir un passage secret / autre).
9. **Les dés** : le dé classique + le dé spécial à loupe — **lancer animé en 3D** au clic, avec explication de chaque face (« la loupe rouge compte comme 1 », « deux icônes = une seule carte Indice »).
10. **Mise en place — assistant interactif en 8 étapes** : stepper cliquable (précédent / suivant / saut direct), chaque étape illustrée et détaillée, **cases à cocher** qui cochant la progression, encadré « Variante 2 joueurs ».
11. **Le tour de jeu — stepper interactif en 4 phases** (Lancer les dés → Se déplacer → Émettre une hypothèse → Porter une accusation) : chaque phase cliquable ouvre ses règles complètes, ses exemples et ses pièges.
12. **Règles de déplacement détaillées** : schéma animé (diagonales interdites, cases occupées, portes, passages secrets), exemples chiffrés.
13. **L'hypothèse et la réfutation — démo interactive** : l'utilisateur choisit un suspect, une arme et une pièce → animation des pions sur le plateau → explication pas à pas de qui montre quoi (joueur de gauche, puis suivant…), avec simulation visuelle.
14. **L'accusation, la victoire et l'échec** : procédure complète, conséquences d'une fausse accusation, « le meurtrier échappe à la justice », fin de partie.
15. **Variante 2 joueurs / par équipe** : règles complètes + schéma.
16. **Le carnet de détective — simulateur interactif** : tableau QUI / AVEC QUOI / OÙ avec cases à cocher, colonnes par joueur, compteur de cartes éliminées, bouton réinitialiser — exactement comme la vraie feuille.
17. **Conseils aux détectives** : stratégie (cocher sa feuille, processus d'élimination, lire les hypothèses des autres, bluffer).
18. **Exemple de partie commenté** : un walkthrough scénarisé étape par étape (avec la solution de l'étui révélée à la fin), entièrement cliquable.
19. **Glossaire interactif** : étui confidentiel, hypothèse, réfutation, accusation, carte Indice, passage secret, case de départ… — **chaque terme est cliquable** (tooltip ou modal).
20. **FAQ en accordéons** : 12 à 20 questions fréquentes (ex. : « Peut-on entrer dans une pièce sans le nombre exact ? », « Que se passe-t-il si personne n'a la carte de mon hypothèse ? », « Peut-on accuser hors de son tour ? », « À quoi sert la loupe ? »…).
21. **Quiz du détective** : 12 à 15 questions à choix multiples avec feedback immédiat expliqué, score final, **confettis en cas de sans-faute**, bouton « rejouer ».
22. **Fiche mémo imprimable** : un récapitulatif d'une page (bouton « Imprimer / PDF ») avec les essentiels.
23. **Pied de page** : mention « Cluedo © 2023 Hasbro — manuel non officiel à but pédagogique ».

## 6. INTERACTIVITÉ — TOUT DOIT ÊTRE CLIQUABLE
Ceci est **l'exigence n°1**. Vérifie chaque point :
- [ ] Sommaire / sidebar avec défilement fluide et **section active surlignée** (scrollspy)
- [ ] **Barre de recherche** instantanée avec surlignage des résultats
- [ ] Onglets et sections **tous cliquables**, accordéons animés, modales au clic
- [ ] Cartes suspects / armes / pièces : **flip 3D au clic**, modal d'agrandissement, survol animé
- [ ] **Plateau SVG entièrement cliquable** (pièces, portes, passages secrets, cases de départ) avec infobulles
- [ ] **Dés cliquables avec animation de lancer** (cube 3D) et explication du résultat
- [ ] **Pile de cartes Indice cliquable** (simulation de pioche animée)
- [ ] Assistants pas-à-pas (mise en place, tour de jeu) : **steppers cliquables** avec progression
- [ ] Démo d'hypothèse : sélecteurs cliquables + animation des pions sur le plateau
- [ ] Carnet de détective : **cases à cocher cliquables**, compteurs mis à jour en direct
- [ ] Glossaire : **chaque terme cliquable** avec tooltip
- [ ] FAQ : **questions cliquables** (accordéons)
- [ ] Quiz : réponses cliquables avec feedback, score, confettis
- [ ] **Barre de progression globale** de lecture du manuel + cases « J'ai compris » par section, **sauvegardées en localStorage**
- [ ] **Bascule sombre / clair** (cliquable, mémorisée)
- [ ] Bouton « Retour en haut » ; raccourcis clavier (ex. `S` recherche, `D` sombre/clair, `?` aide)
- [ ] Sons optionnels (WebAudio, désactivables) : dé, clic, victoire
- [ ] Animations au défilement (IntersectionObserver) — **respectant `prefers-reduced-motion`**

## 7. DIRECTION ARTISTIQUE — univers « enquête de détective »
- Palette : **vert profond (table de jeu), bordeaux / rouge sang, or, ivoire, noir encre** ; couleurs des 6 suspects pour leurs cartes.
- Typographies **système** (hors ligne oblige) : serif élégante pour les titres (Georgia, « Times New Roman »), sans-serif lisible pour le texte (system-ui, Arial).
- Ambiance : papier ancien, filets dorés, ombres portées douces, micro-interactions (effets de survol, transitions 200-300 ms), icônes **SVG inline** (loupe, pions, armes, dé).
- Micro-texte d'ambiance : « Rapport confidentiel », « Classé X-32 », tampons « Vu par le détective » — avec sobriété.

## 8. EXIGENCES TECHNIQUES
- **Un seul fichier** `.html`, HTML5 sémantique (`<header>`, `<nav>`, `<main>`, `<section>`, `<details>`, etc.), CSS3 (variables, grid/flex, animations), **JavaScript vanilla (ES6+)** — aucun framework, aucune bibliothèque, aucune requête réseau.
- Accessibilité : rôles ARIA, `aria-expanded`, focus visible, navigation clavier complète, contrastes WCAG AA.
- Responsive : mobile-first, breakpoints ~640 / ~1024 px.
- **localStorage** : progression, thème, quiz, cases cochées ; bouton « Réinitialiser ma progression ».
- `@media print` : fiche mémo propre, sans sidebar.
- Code **commenté en français**, organisé (sections CSS et fonctions JS clairement nommées).

## 9. PÉDAGOGIE — comment expliquer
- Chaque règle suit le schéma : **« En clair » (1 phrase simple) → Le détail (la règle exacte) → Exemple concret → Piège classique »**.
- Encadrés récurrents : 🧭 **À retenir** · ⚠️ **Piège classique** · 🔎 **Astuce de détective**.
- Un exemple de partie fictive (Sarah joue Mlle Rose…) illustre les mécanismes ; les noms des exemples sont variés et inclusifs.
- Le ton est immersif mais clair : « Vous êtes détective, voici votre rapport. »

## 10. PROCESSUS DE TRAVAIL IMPOSÉ (suis cet ordre)
1. Analyse les 14 photos et établis la fiche du jeu (suspects, armes, pièces, cartes Indice, règles).
2. Recoupe avec la section 2 et signale les écarts éventuels.
3. Rédige **tout le contenu textuel** (chaque section, chaque exemple, chaque question de quiz).
4. Définis les tokens de design (couleurs, espacements, ombres, rayons).
5. Construis la structure HTML complète (toutes les sections).
6. Applique le CSS (thème clair + sombre, responsive, animations).
7. Implémente toute l'interactivité JS (clics, dés, plateau, quiz, localStorage…).
8. **Auto-test** : ouvre le fichier mentalement et vérifie la checklist du §6 point par point ; corrige ce qui manque.
9. Livre le code final complet.

## 11. DÉFINITION DE « FAIT » — checklist finale (à auto-valider avant de répondre)
- [ ] Toutes les sections du §5 sont présentes et **entièrement rédigées** (aucun placeholder)
- [ ] Les règles sont fidèles aux photos et au §2.5
- [ ] **Chaque élément cliquable l'est réellement** (les 22 points du §6)
- [ ] Le fichier fonctionne hors ligne, en double-clic, sans console d'erreur
- [ ] Thème sombre/clair, responsive, navigation clavier OK
- [ ] Quiz fonctionnel avec score ; progression sauvegardée
- [ ] Impression de la fiche mémo correcte

## 12. INTERDITS
- ❌ Aucune ressource externe (CDN, police web, image, framework, `fetch`)
- ❌ Aucun texte générique, aucun « lorem ipsum », aucun « … » laissé à compléter
- ❌ Aucune section vide, aucun bouton mort
- ❌ Pas d'anglais dans l'interface (le terme « Cluedo » et les noms propres exceptés)
- ❌ Ne propose pas « plusieurs options » : livre **le** fichier complet

## 13. FORMAT DE RÉPONSE
1. Un paragraphe (5 lignes max) : ce qui a été fait.
2. **Le code complet du fichier** dans un seul bloc ````html … ```` — intégrable tel quel, sans troncature.
3. Trois lignes d'utilisation : ouvrir le fichier, imprimer la fiche mémo, réinitialiser la progression.

════════════════════════════════════════════════════════════════════════════════════

---

## 📎 ANNEXE A — Fiche technique du jeu (à coller en plus si besoin)

```
JEU        : Cluedo — « Qui a tué Mat Lenoir ? » (Le Manoir Tudor)
ÉDITEUR    : Hasbro Gaming, © 2023 (réf. F6420)
JOUEURS    : 2 à 6 (classique 3-6 + variante 2 joueurs)
ÂGE        : 8+ | Durée : ~45 min
CONTENU    : plateau · 6 pions Personnage · 6 pions Arme · 2 dés
             (1 classique + 1 spécial loupe) · étui confidentiel ·
             carnet de détective · 50 cartes (6 perso. + 6 armes +
             9 pièces + 29 cartes Indice)

SUSPECTS (couleur)      ARMES                PIÈCES
Mlle Rose (rouge)       Chandelier           Salle de réception
Colonel Moutarde (jaune) Poignard            Salle de billard
M. le Maire Olive (vert) Barre de fer        Jardin d'hiver
Maître Pervenche (bleu)  Révolver            Salle à manger
Prof. Violet (violet)    Corde               Entrée
Cheffe Leblanc (blanc)   Clé anglaise        Cuisine
                                             Bibliothèque
                                             Salon
                                             Bureau

PASSAGES SECRETS : Cuisine ↔ Bureau · Jardin d'hiver ↔ Salon
VICTIME : M. Mat Lenoir, dit « le Macchabé » (manoir Tudor)
MÉCANIQUES CLÉS : hypothèse · réfutation (joueur de gauche) ·
accusation unique · étui confidentiel · carte Indice (loupe) ·
cases de départ colorées · entrée par porte non bloquée
```

## 📎 ANNEXE B — Ce que montrent les 14 photos (pour cibler l'analyse)

| Photo | Contenu détecté |
|---|---|
| 1–4 | Cartes Indice (titres, textes d'ambiance, effets : « Le joueur qui possède la carte X doit la montrer », « Tous les joueurs montrent secrètement une carte au joueur à leur gauche », « Nommez un personnage/une arme/une pièce que vous voulez éliminer ») |
| 5 | Page « Comment gagner » : accusation unique, « J'accuse… », étui, conséquences, mode 2 joueurs, conseils détectives |
| 6 | Page « Place au jeu » : tour de jeu complet (déplacement, loupe = 1 + carte Indice, hypothèse, réfutation à gauche, accusation) |
| 7 | Fin de la mise en place : distribution, carnet de détective, cocher ses cartes |
| 8 | Page « Mise en place » : 8 étapes (pions, choix personnage, armes, cartes Indice, étui, distribution) |
| 9 | Les cartes du jeu : suspects, armes (Chandelier, Clé anglaise, Barre de fer, Révolver…), pièces (Bureau…) |
| 10 | Biographies des 6 suspects (Rose/Cyan, Moutarde, Olive, Pervenche, Violet…) |
| 11 | Histoire « LA NUIT DU MEURTRE » + contenu de la boîte |
| 12 | Dos de boîte : listes officielles QUI/AVEC QUOI/OÙ + réf. F6420 © 2023 Hasbro |
| 13 | Photo du plateau de jeu (angle difficile : recouper avec le plan standard) |
| 14 | Couverture de la boîte (« Le jeu des grands détectives ») |

## 📎 ANNEXE C — Plan standard de l'édition (si la photo 13 est illisible)

```
┌──────────────┬──────────────┬──────────────┐
│   BUREAU     │    ENTRÉE    │    SALON     │   ← passages secrets :
│  (coin,      │              │  (coin,      │      Cuisine ↔ Bureau
│   passage)   │              │   passage)   │      Jardin d'hiver ↔ Salon
├──────────────┼──────────────┼──────────────┤
│ BIBLIOTHÈQUE │   COULOIRS   │ SALLE À      │
│              │  (croix,     │ MANGER       │
│              │  cases de    │              │
│              │  départ)     │              │
├──────────────┼──────────────┼──────────────┤
│ SALLE DE     │              │              │
│ BILLARD      │              │              │
├──────────────┼──────────────┼──────────────┤
│ JARDIN       │ SALLE DE     │   CUISINE    │
│ D'HIVER      │ RÉCEPTION    │  (coin,      │
│ (coin,       │              │   passage)   │
│  passage)    │              │              │
└──────────────┴──────────────┴──────────────┘
```

---

*Manuel non officiel — Cluedo et ses personnages sont des marques de Hasbro. Document rédigé pour un usage pédagogique et personnel.*
