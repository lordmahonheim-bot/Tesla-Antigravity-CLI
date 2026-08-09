# 🎯 PROMPT ULTIME — Manuel Interactif Cluedo (Page HTML Locale)

---

## CONSIGNE PRINCIPALE

Crée une **page HTML unique** (`manuel_cluedo.html`) entièrement autonome (HTML + CSS + JavaScript inline, zéro dépendance externe, ouvrable directement dans un navigateur en `file://`). Cette page est le **manuel d'instruction complet, détaillé et explicatif** du jeu de société **Cluedo — Le jeu des grands détectives** (Hasbro, Réf. F6420, © 2023 Hasbro, 2-6 joueurs, 8+).

**Tout doit être cliquable et interactif.** Aucun texte ne doit être un simple bloc statique. Chaque section, chaque personnage, chaque arme, chaque pièce, chaque règle doit être un élément interactif (accordéon, carte retournable, modal, onglet, tooltip, carrousel ou menu).

---

## LANGUE et TON

- Langue : **Français**.
- Ton : Immersif, narratif et mystérieux (l'utilisateur est un détective qui ouvre son dossier d'enquête), tout en restant pédagogique et limpide pour un joueur de 8 ans.

---

## DESIGN et ESTHÉTIQUE

### Palette de couleurs
- **Fond principal** : Bleu-marine très sombre (#1a1a2e ou similaire), évoquant la nuit du meurtre au manoir Tudor.
- **Accents** : Or antique (#c9a84c), bordeaux profond (#6b1d1d), blanc cassé (#f0ead6).
- **Cartes et Panneaux** : Fond ivoire/parchemin avec ombres portées douces (glassmorphism subtil ou effet papier vieilli).

### Typographie
- Titres : Police serif élégante (Google Fonts : `Playfair Display` ou `Cinzel`).
- Corps de texte : Sans-serif lisible (`Inter`, `Nunito` ou `Lato`).
- Taille de base : 16px minimum, responsive.

### Ambiance visuelle
- Header immersif avec le logo "Cluedo" stylisé en grand, un effet de brume/fumée CSS subtil en arrière-plan, et l'invitation de Mat Lenoir en encadré calligraphié.
- Icônes thématiques : 🔍 (loupe), 🗡️ (arme), 🏛️ (pièce), 🎭 (suspect), 🎲 (dé), 📋 (feuille de détective).
- Micro-animations CSS : hover glow doré sur les éléments cliquables, transitions fluides (300ms ease), effet de "révélation" (fondu-enchaîné) à l'ouverture des sections.

---

## STRUCTURE et CONTENU EXHAUSTIF (Sections interactives)

### SECTION 0 — COUVERTURE (Hero Section)
- Bannière plein écran avec titre **"CLUEDO"** en très grand, sous-titre **"Le jeu des grands détectives"** et le tagline **"L'un d'eux est coupable : personne n'est innocent."**
- En dessous, l'invitation encadrée de Mat Lenoir (style lettre ancienne avec bordure ornementale) :
  > *« M. Mat Lenoir demande de lui faire l'honneur de votre compagnie pour un dîner privé dans son manoir historique Tudor. Hors d'œuvres servis au coucher du soleil, dîner servi à 20 h. Votre présence est d'ores et déjà confirmée. »*
- Badges : `8+` | `2-6 joueurs` | `~45 min` | `Hasbro © 2023`
- **Bouton CTA** animé : "Ouvrir le dossier d'enquête ▼" qui fait défiler vers la section suivante avec un smooth scroll.

---

### SECTION 1 — LA NUIT DU MEURTRE (Contexte narratif — Accordéon dépliable)
Texte complet de l'histoire d'introduction, intégralement fidèle au livret original :

> *Six invités soigneusement sélectionnés arrivent au manoir Tudor, la demeure familiale de Mat Lenoir, dit le Macchabé, après avoir reçu une mystérieuse invitation. Pendant le dîner, Lenoir annonce son projet de construction d'un hôtel de luxe extravagant et démesuré, à l'endroit même d'un parc populaire de la ville. Tout le monde s'y oppose, mais Lenoir révèle ensuite qu'il a des informations pour tous les faire chanter et les forcer à l'aider. S'ils refusent, leurs secrets seront révélés. Peu de temps après, il s'excuse et les invités se dispersent pour digérer la nouvelle. Un cri retentit. Les invités découvrent Lenoir, assassiné.*

Phrase finale en gras doré : **"C'est maintenant à vous d'élucider le mystère."**

Sous cette section, afficher la question centrale en trois lignes décoratives :
- **QUI** a tué Mat Lenoir ?
- avec **QUELLE** arme ?
- et **OÙ** ?

---

### SECTION 2 — CONTENU DE LA BOÎTE (Grille interactive cliquable)

Afficher une grille de cartes/badges cliquables. Au clic, chaque élément affiche un tooltip ou un popup avec une description détaillée.

| Composant | Quantité | Détail au clic |
|---|---|---|
| Plateau de jeu | 1 | Plan du manoir Tudor vu de dessus, 9 pièces reliées par des couloirs, passages secrets entre coins opposés |
| Pions Personnage | 6 | Mlle Rose (rouge), Col. Moutarde (jaune), M. le Maire Olive (vert), Maître Pervenche (bleu), Prof. Violet (violet), Cheffe Leblanc (blanc) |
| Pions Arme | 6 | Chandelier, Clé anglaise, Corde, Barre de fer, Révolver, Poignard |
| Cartes Personnage | 6 | Une par suspect |
| Cartes Arme | 6 | Une par arme |
| Cartes Pièce | 9 | Une par pièce du manoir |
| Cartes Indice | 29 | Cartes narratives avec instructions (loupe au dos) |
| Étui confidentiel | 1 | Contient la solution du mystère (3 cartes) |
| Carnet de détective | 1 bloc | Feuilles de suivi pour noter les indices |
| Dés | 2 | Un dé classique 6 faces + un dé avec icône loupe (la loupe compte comme 1) |

---

### SECTION 3 — LES SUSPECTS (Carrousel ou grille de cartes retournables)

Chaque suspect est une **carte retournable au clic** (effet flip 3D CSS). Le recto montre le nom et la couleur du pion. Le verso révèle la biographie complète.

#### 3.1 — Mlle Rose (pion rouge)
> Bourgeoise, à première vue. En réalité, c'est une journaliste d'investigation particulièrement intelligente. Écrivant sous le pseudonyme de « Cyan », elle a fait mettre des mafieux en prison et a causé la ruine de héros locaux. Personne n'est à l'abri de sa plume, vu que personne ne sait qui elle est. À l'exception de Mat Lenoir, qui a justement besoin d'une bonne critique sur son nouvel hôtel.

#### 3.2 — Colonel Moutarde (pion jaune)
> Héros de guerre décoré, avec de nombreux récits de batailles passées et d'évasions miraculeuses. C'est un homme d'action qui a l'expérience nécessaire pour agir. En tant que membre respecté de l'armée, sa crédibilité pourrait facilement faire pencher l'opinion publique en faveur de Lenoir, surtout si cela signifie que personne ne découvre qu'en fait, il n'a jamais combattu pendant la bataille pour laquelle il a reçu sa médaille la plus prestigieuse.

#### 3.3 — M. le Maire Olive (pion vert)
> Le sympathique maire du Comté Coloris qui a toujours un bon mot à dire. Il se prépare pour sa réélection, mais cela ne l'inquiète pas : même ses adversaires ont du mal à le détester. Il n'y a qu'un seul point qui peut ternir son dossier impeccable : un don reçu d'une importante famille de criminels qui lui a permis de sauver sa campagne. Lenoir lui a assuré que personne ne le découvrirait... tant qu'il contribue à modifier la zone du parc où Lenoir a l'intention de faire construire son hôtel.

#### 3.4 — Maître Pervenche (pion bleu)
> Avocate tenace, elle sait exactement comment gérer une salle, que ce soit dans un tribunal ou non. Son succès lui a apporté un statut important qu'elle n'hésite pas à afficher. Lenoir sait que rien ne peut l'arrêter quand il s'agit de gagner un procès, pas même l'utilisation de faux témoins, un fait qu'il serait ravi de révéler si elle refuse de le représenter dans les négociations pour son hôtel.

#### 3.5 — Prof. Violet (pion violet)
> Un professeur d'antiquités extrêmement perspicace. Son incroyable attention aux détails l'aide à identifier les contrefaçons, et parfois même à en fabriquer. Seul Lenoir sait que sa contrefaçon la plus convaincante est le doctorat de Violet, trônant fièrement au-dessus de son bureau. Avec une bonne motivation, le professeur pourrait probablement fabriquer n'importe quelle contrefaçon, même un acte de propriété prouvant que Lenoir a des droits sur le parc où il a l'intention de construire son hôtel.

#### 3.6 — Cheffe Leblanc (pion blanc)
> Cheffe prometteuse et ambitieuse avec de nouvelles idées. Elle dirige les cuisines de Lenoir depuis des années, mais elle trouve que son menu peu original limite sa créativité et elle rêve d'ouvrir son propre restaurant. Son plan repose sur son talent, sa persévérance... et l'argent qu'elle a soutiré à Mat Lenoir, mais celui-ci le sait depuis le début. Deux choix s'offrent à elle : gérer ingratement le restaurant de l'hôtel de Lenoir, ou faire face aux accusations.

---

### SECTION 4 — LES ARMES (Grille de 6 éléments cliquables avec effet hover et modal)

Chaque arme est un élément visuel avec icône/emoji. Au clic ou hover, afficher le nom en grand avec un effet lumineux doré.

1. 🕯️ **Chandelier**
2. 🔧 **Clé anglaise**
3. 🪢 **Corde**
4. 🏏 **Barre de fer**
5. 🔫 **Révolver**
6. 🗡️ **Poignard**

---

### SECTION 5 — LES PIÈCES DU MANOIR (Plan interactif ou grille cliquable)

Les 9 pièces du manoir Tudor. Chaque pièce est cliquable et affiche une description ou sa position sur le plateau. Mentionner les **passages secrets** (entre pièces situées dans les coins diagonalement opposés du plateau).

1. 🛋️ **Salon**
2. 🍳 **Cuisine**
3. 🎱 **Salle de billard**
4. 🌿 **Jardin d'hiver**
5. 🍽️ **Salle à manger**
6. 📚 **Bibliothèque**
7. 💼 **Bureau**
8. 🚪 **Entrée**
9. 🎉 **Salle de réception**

> **Passages secrets :** Certaines pièces situées aux coins du plateau sont reliées par des passages secrets. Si vous êtes dans l'une de ces pièces au début de votre tour, vous pouvez emprunter le passage secret pour vous déplacer directement dans la pièce reliée, sans lancer les dés.

---

### SECTION 6 — MISE EN PLACE (Stepper interactif / Timeline verticale cliquable)

Présenter les 8 étapes comme un **stepper vertical** (timeline) où chaque étape est un noeud cliquable qui se déplie pour révéler les instructions détaillées :

**Étape 1.** Placez les six pions sur leurs cases de couleur correspondantes du plateau de jeu. Tous les pions doivent s'y trouver, même s'il y a moins de 6 joueurs. Choisissez votre personnage.

**Étape 2.** Placez aléatoirement chaque arme dans une pièce différente.

**Étape 3.** Séparez les 29 cartes Indice des autres cartes. Mélangez la pile de cartes Indice et placez-la face cachée à côté du plateau.

**Étape 4.** Séparez les autres cartes en 3 piles : personnages, armes et pièces. Mélangez chaque pile et placez-la face cachée.

**Étape 5.** Prenez la carte du dessus de chaque pile et glissez-la discrètement dans l'étui confidentiel sans que personne ne la voie. Elle contient maintenant les trois cartes qui répondent aux questions : **QUI a tué Lenoir, OÙ le crime a-t-il été commis et avec QUELLE arme ?** C'est le mystère que vous allez devoir résoudre ! Placez l'étui au centre du plateau de jeu.

**Étape 6.** Mélangez les cartes Personnage, Arme et Pièce restantes, puis distribuez-les toutes aux joueurs. Peu importe si certains joueurs ont plus de cartes que d'autres.

**Étape 7.** Détachez une feuille du carnet de détective pour chaque joueur. Vous aurez aussi besoin d'un crayon (non inclus) pour chaque joueur.

**Étape 8.** Regardez vos cartes en secret et cochez les suspects, les armes et les pièces sur votre feuille. Aucun d'eux ne peut être dans l'étui confidentiel ! Gardez votre feuille et vos cartes secrètes.

> **Remarque :** pour jouer en Mode 2 joueurs, référez-vous à la section dédiée. Vous distribuerez les cartes différemment à ce moment de la partie.

---

### SECTION 7 — PLACE AU JEU / DÉROULEMENT D'UN TOUR (Onglets interactifs)

Utiliser un **système d'onglets** (tabs) pour les deux grandes actions d'un tour :

#### Onglet "Qui commence ?"
> Lancez un des dés à 6 faces pour déterminer qui commence.

#### Onglet "À votre tour"
> Lancez les dés. Vous pouvez ensuite exécuter au moins une action :

**Action 1 — Déplacez votre pion Personnage** (sous-accordéon avec toutes les règles de déplacement) :
- Vous pouvez vous déplacer au maximum du nombre de cases indiqué par le lancer de dés. (La loupe rouge compte comme un 1.) Si vous entrez dans une pièce, référez-vous à l'Action 2.
- Vous ne pouvez pas vous déplacer en diagonale, repasser deux fois sur la même case pendant un même tour ou traverser une case occupée par un autre pion (incluant les portes), ou vous y arrêter.
- Vous pouvez entrer dans une pièce pendant votre tour, mais il n'est pas nécessaire d'obtenir le nombre de cases exact. Vous devez entrer par une porte non bloquée.
- Si vous êtes déjà dans une pièce au début de votre tour : Vous n'êtes pas contraint de vous déplacer si vous voulez émettre une hypothèse (voir Action 2). S'il y a un passage secret, vous pouvez l'utiliser pour déplacer votre pion dans la pièce qui y est reliée.

**Encadré spécial "Cartes Indice" (icône loupe 🔍)** — avec bordure distinctive :
> Si vous avez obtenu l'icône de loupe, piochez une carte Indice, lisez-la à haute voix et suivez ses instructions. Remettez-la ensuite au-dessous de la pile.
> - Si vous obtenez deux icônes, vous ne piochez quand même qu'une carte.
> - Si une carte Personnage, Arme ou Pièce est révélée, cochez-la sur votre feuille.
> - Chaque fois que vous devez révéler une carte, remettez-la ensuite dans votre main.

**Action 2 — Émettez une hypothèse** (sous-accordéon) :
> Si vous entrez dans une pièce ou que vous êtes déjà dans une pièce, émettez une hypothèse décrivant qui a commis le crime, avec quelle arme et dans quelle pièce. Dites : « Est-ce **(un personnage)**, avec **(une arme)**, dans **(la pièce où vous êtes)** ».
>
> - Déplacez le pion suspect et l'arme dans la pièce. (Ils y resteront après votre tour. Plusieurs pions et armes peuvent se trouver dans une pièce en même temps.)
> - Le joueur situé à votre gauche vous montre **secrètement** une des cartes incluses dans votre hypothèse, s'il en a une. S'il en a plus d'une, il choisit celle qu'il vous montre.
> - S'il n'a pas de carte, le joueur suivant vous montre secrètement une carte incluse dans votre hypothèse. Et ainsi de suite, jusqu'à ce qu'un joueur vous montre une carte. Lorsqu'on vous montre une carte, votre hypothèse est écartée, et le jeu continue.
> - Personne n'a de carte ? Ce n'est pas un problème.
>
> **Cochez la carte qu'on vous a montrée** sur votre feuille de détective. Vous savez qu'elle n'est pas dans l'étui.

**Encadré "Victoire possible"** :
> Vous pensez avoir résolu le meurtre ? Vous pouvez porter une accusation juste après avoir émis une hypothèse. Voir la section COMMENT GAGNER.

> Si personne ne vous montre de carte, votre hypothèse est probablement la bonne ! C'est tout. C'est maintenant au tour du joueur situé à votre gauche.

---

### SECTION 8 — COMMENT GAGNER / VICTOIRE (Section avec effet dramatique)

Afficher avec un fond contrasté (rouge sombre / or) et une animation d'apparition :

> Dès que vous pensez avoir résolu le mystère, portez une accusation ! Vous ne pouvez porter qu'**une seule accusation par partie**. Vous devez le faire pendant votre tour, même après avoir émis une hypothèse. Vous devez être dans une pièce, mais il n'est pas nécessaire que ce soit celle que vous allez nommer.
>
> 1. Dites « J'accuse **(un personnage)**, avec **(une arme)**, dans **(une pièce)** ».
> 2. Regardez discrètement dans l'étui confidentiel. Les trois cartes que vous avez nommées y sont-elles ?
>
> **OUI !** Vous gagnez ! Félicitations, vous avez résolu le mystère !
>
> **NON !** Oups, vous vous êtes trompé ! Remettez les cartes dans l'étui sans que personne ne les voie. Vous ne pouvez plus jouer de tours, mais vous devez montrer des cartes lorsque les autres joueurs émettent des hypothèses ou nomment des cartes qu'ils souhaitent voir révélées. La partie continue jusqu'à ce que quelqu'un porte une accusation exacte. Si personne n'y parvient, le meurtrier échappe à la justice !

---

### SECTION 9 — MODE 2 JOUEURS OU PAR ÉQUIPE (Accordéon dépliable)

> Cette variante se joue comme une partie classique, à deux exceptions près :
>
> - **Mise en place :** Suivez les étapes 1 à 5. Ensuite, après avoir mélangé les cartes restantes, placez 4 cartes aléatoirement et face cachée dans 4 pièces de votre choix (pour une partie plus rapide, mettez-les dans les pièces des coins du plateau). Puis continuez la mise en place normalement.
> - **Place au jeu :** Si vous entrez dans une pièce qui contient une carte, regardez discrètement cette carte et cochez votre feuille, puis émettez votre hypothèse normalement.

---

### SECTION 10 — CONSEILS AUX DÉTECTIVES (Accordéon avec 3 sous-sections)

#### 10.1 — Cocher sa feuille
> Quand un joueur vous montre une carte, notez-la sur votre feuille dans la première colonne *ainsi que* dans la colonne sous les initiales du joueur. Savoir quel joueur possède quelles cartes vous aidera à élaborer une stratégie quand vous émettrez des hypothèses. Et vous pourriez également relever des indices lorsque d'autres joueurs émettront des hypothèses.

#### 10.2 — Processus d'élimination
> Les hypothèses aident à déterminer qui a commis le crime par processus d'élimination. À mesure que les joueurs révèlent des cartes, vous pouvez éliminer les possibilités pour déterminer quelles cartes Personnage, Arme et Pièce se trouvent dans l'étui.

#### 10.3 — Utiliser ses cartes
> Utilisez les cartes de votre main à votre avantage lorsque vous émettez des hypothèses. Si vous voulez déterminer si un joueur a une carte spécifique, nommez une ou deux de vos propres cartes.

Afficher un **exemple visuel interactif** de la feuille de détective remplie, basé sur l'exemple du livret original. À la fin de l'exemple, le verdict : **« Dans cet exemple, le Prof. Violet est le meurtrier ! »**

---

### SECTION 11 — LES CARTES INDICE (Section scrollable ou accordéon)

Présenter les 29 cartes Indice sous forme de **grille de mini-cartes cliquables** (style carte à jouer avec coins arrondis et fond ivoire). Au clic, chaque carte s'agrandit (modal) pour afficher son texte complet. Voici les cartes avec leur contenu exact :

1. **« Droit de se vanter »** — Pervenche ne joue que pour gagner, quel que soit le jeu. → *Le joueur qui possède la carte **Salle de billard** doit la montrer.*
2. **« DRIIING ! »** — Pourquoi Pervenche reçoit-elle un appel du travail à cette heure ? → *Le joueur qui possède la carte **Bureau** doit la montrer.*
3. **« Quelle étrange décoration ! »** — Une arme décorée de la sorte semble être tout à fait le style de Moutarde. → *Le joueur qui possède la carte **Révolver** doit la montrer.*
4. **« Un colonel en crise »** — Pour un homme qui a reçu une médaille de courage, Moutarde paraît terriblement anxieux. → *Le joueur qui possède la carte **Col. Moutarde** doit la montrer.*
5. **« Une avocate accusatrice »** — Les témoins trouvent peut-être Pervenche intimidante, mais son intensité ne fait que la rendre plus suspecte. → *Le joueur qui possède la carte **Maître Pervenche** doit la montrer.*
6. **« Un discours convaincant »** — Olive rassemble les invités et tente de prononcer quelques mots inspirants. → *Le joueur qui possède la carte **Entrée** doit la montrer.*
7. **« Une fuite répugnante »** — Rose se glisse dans la cuisine et marche dans une flaque d'eau, trempant l'ourlet de sa robe. → *Le joueur qui possède la carte **Clé anglaise** doit la montrer.*
8. **« Extrémités effilochées »** — Moutarde n'est pas paranoïaque, il sait que même les objets les plus inoffensifs peuvent être mortels. → *Le joueur qui possède la carte **Corde** doit la montrer.*
9. **« Rose a dit quoi ? »** — Elle en sait un peu sur tout le monde, et elle a des secrets à révéler. → *Tous les joueurs montrent secrètement une carte au joueur à leur gauche.*
10. **« Derrière les rideaux »** — Les draperies luxueuses se fondent parfaitement avec la robe de Rose et lui fournissent un endroit idéal pour écouter les conversations. → *Le joueur qui possède la carte **Salle de réception** doit la montrer.*
11. **« Contrefaçons fantastiques »** — Que Violet cherche-t-il si frénétiquement dans les titres de propriété de Lenoir ? → *Le joueur qui possède la carte **Prof. Violet** doit la montrer.*
12. **« Qu'est-ce que ça pourrait bien être ? »** — L'expertise de Violet en matière d'antiquités pourrait nous aider à le découvrir. → *Le joueur qui possède la carte **Chandelier** doit la montrer.*
13. **« Pièges politiques »** — Qui appelle sans cesse Olive, et pourquoi ses mains tremblent-elles à chaque fois qu'il prend la communication ? → *Le joueur qui possède la carte **M. le maire Olive** doit la montrer.*
14. **« Le soutien du maire »** — Olive est un homme du peuple et il est prêt à se porter garant de tous ses citoyens bien-aimés. → *Nommez un **personnage** que vous voulez éliminer.*
15. **« Dites m'en plus... »** — Rose a un talent inné pour inviter les gens à lui révéler leurs secrets les plus intimes. → *Choisissez le joueur qui a l'air le plus coupable : il doit révéler une carte de son choix.*
16. **« Dispersez-vous ! »** — Un cri retentit quelque part dans le manoir. → *Tous les joueurs se précipitent dans la pièce de leur choix.*
17. **« Qu'avons-nous donc ici ? »** — Moutarde est un expert en armes, il pourra peut-être nous éclairer. → *Nommez une **arme** que vous voulez éliminer.*
18. **« La découverte d'un rat de bibliothèque ! »** — Tandis que Violet sort un vieux tome de l'étagère, il entend un mystérieux craquement derrière le livre. → *Mettez cette carte dans la pièce de votre choix. Elle communique maintenant avec les autres passages secrets.*
19. **« Plomberie volée »** — Pervenche revient du rouge à lèvres devant les fenêtres du jardin d'hiver et se rend compte que le système d'arrosage fonctionne mal. → *Le joueur qui possède la carte **Barre de fer** doit la montrer.*
20. **« Le dîner est servi ! »** — Leblanc a passé beaucoup trop de temps sur ce repas pour qu'il soit jeté. → *Le joueur qui possède la carte **Salle à manger** doit la montrer.*
21. **« Deux outils révélateurs »** — Quelqu'un a vidé le coffre-fort de l'endroit en laissant derrière lui ses outils : une fourchette et un couteau. → *Le joueur qui possède la carte **Cheffe Leblanc** doit la montrer.*
22. **« GARDE-À-VOUS ! »** — Moutarde connaît l'importance d'une vigilance constante, et il ne tolérera aucune relâche. → *Le joueur qui possède la carte **Salon** doit la montrer.*
23. **« À la barre »** — Un interrogatoire de Pervenche peut faire craquer n'importe qui. → *Tous les joueurs révèlent une carte de leur main.*
24. **« Fonctionnaire »** — Olive est toujours aimable et serviable, et il est heureux d'aider là où il peut être utile. → *Nommez une **pièce** que vous voulez éliminer.*
25. **« Griffonnages suspects »** — Qu'est-ce que Rose pourrait bien écrire dans son étrange carnet ? → *Le joueur qui possède la carte **Mademoiselle Rose** doit la montrer.*
26. **« Un arôme paradisiaque »** — Quoi que Leblanc ait préparé dans sa cuisine, l'odeur est à tomber par terre. → *Le joueur qui possède la carte **Cuisine** doit la montrer.*
27. **« Une indulgence fantastique »** — Violet prétend faire des « recherches », mais les dragons sur la couverture de son livre n'ont rien d'académique... → *Le joueur qui possède la carte **Bibliothèque** doit la montrer.*
28. **« Un autre cuisinier dans la cuisine ? »** — Leblanc découvre un objet étrange dissimulé parmi ses couteaux de cuisine. → *Le joueur qui possède la carte **Poignard** doit la montrer.*
29. **« Plantes vénéneuses »** — Violet s'y connaît un peu en botanique et il se tient à l'écart des plantes de Lenoir. → *Le joueur qui possède la carte **Jardin d'hiver** doit la montrer.*

---

### SECTION 12 — FEUILLE DE DÉTECTIVE INTERACTIVE (Outil fonctionnel)

Intégrer une **réplique fonctionnelle et interactive** de la feuille de détective Cluedo. L'utilisateur doit pouvoir :
- Cliquer sur les cases pour cocher/décocher (✓ ou ✗).
- Entrer les initiales des joueurs en haut des colonnes.
- La grille doit contenir les 3 sections : **QUI ?** (6 suspects), **AVEC QUOI ?** (6 armes), **OÙ ?** (9 pièces).
- Bouton "Réinitialiser la feuille".
- Style visuel fidèle à la feuille originale (fond blanc, quadrillage net, logo Cluedo en haut).

---

### SECTION 13 — FAQ / SITUATIONS SPÉCIALES (Accordéon de questions fréquentes)

Compiler les cas limites et questions fréquentes en mini-accordéon :
- *Puis-je émettre une hypothèse sans être dans une pièce ?* → Non, vous devez être dans une pièce.
- *Puis-je nommer une pièce différente de celle où je me trouve ?* → Non, pour une hypothèse vous devez nommer la pièce où vous êtes. Pour une accusation, vous pouvez nommer n'importe quelle pièce.
- *Que se passe-t-il si mon pion est déplacé par l'hypothèse d'un autre joueur ?* → Vous êtes maintenant dans cette pièce. À votre prochain tour, vous pouvez y émettre une hypothèse ou la quitter.
- *Combien d'accusations puis-je porter ?* → Une seule par partie. Si vous vous trompez, vous êtes éliminé (mais vous continuez à montrer des cartes).
- *Peut-on bloquer une porte ?* → Oui, une case de porte occupée bloque le passage.

---

### FOOTER
- © 2023 Hasbro. Cluedo est une marque déposée de Hasbro. Réf. F6420.
- Mention : "Manuel numérique interactif — Usage personnel uniquement."
- Lien "Retour en haut" avec smooth scroll.

---

## SPÉCIFICATIONS TECHNIQUES

1. **Fichier unique** : Un seul fichier `manuel_cluedo.html` contenant tout le HTML, CSS et JavaScript inline.
2. **Zéro dépendance externe** : Pas de CDN, pas de framework JS. Seule exception autorisée : Google Fonts via `@import` CSS pour les polices.
3. **Responsive** : Doit s'afficher correctement sur mobile, tablette et desktop.
4. **Accessibilité** : Attributs `aria-*` sur les accordéons et onglets. Contraste WCAG AA minimum.
5. **Performance** : Animations CSS uniquement (pas de librairie JS d'animation).
6. **Interactivité minimale obligatoire** :
   - Accordéons dépliables pour chaque section majeure.
   - Cartes retournables (flip) pour les suspects.
   - Onglets pour les phases de jeu.
   - Stepper cliquable pour la mise en place.
   - Grille de cartes Indice avec modals au clic.
   - Feuille de détective fonctionnelle avec cases cochables.
   - Smooth scroll sur tous les liens internes.
   - Effet hover doré sur tous les éléments interactifs.
   - Menu de navigation latéral ou top-bar sticky avec ancres vers chaque section.

---

## CONTRAINTES IMPÉRATIVES

- **AUCUN placeholder** : Tout le contenu textuel ci-dessus doit être intégré tel quel.
- **AUCUNE image externe** : Utiliser exclusivement des emojis, des formes CSS ou des SVG inline pour les visuels.
- **FIDÉLITÉ AU LIVRET ORIGINAL** : Les textes des règles, biographies et cartes Indice sont des transcriptions exactes du livret officiel Hasbro F6420 (version française). Ne rien inventer, ne rien résumer, ne rien omettre.
