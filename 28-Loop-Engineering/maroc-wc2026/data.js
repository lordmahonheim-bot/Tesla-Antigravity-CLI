/* 
MODE D'EMPLOI : comment ajouter le prochain match ou un nouvel événement
Pour mettre à jour le prochain match, éditez l'objet `prochainMatch` ci-dessous.
Par exemple, pour le quart de finale, décommentez et adaptez :
  prochainMatch: {
    adversaire: "Vainqueur (Mexique/Argentine)",
    date: "2026-07-10T20:00:00",
    dateTexte: "vendredi 10 juillet 2026",
    competitionStage: "Quart de finale",
    aVenir: true
  }

Pour ajouter un événement à la timeline, ajoutez un objet dans le tableau `timeline`.
*/

// biome-ignore lint/correctness/noUnusedVariables: APP_DATA is accessed globally in app.js
const APP_DATA = {
  meta: { 
    majLe: "1er juillet 2026", 
    version: "1.0" 
  },
  equipe: { 
    nom: "Maroc", 
    surnom: "Les Lions de l'Atlas", 
    confederation: "CAF", 
    participation: "7e", 
    meilleurResultat: "4e place (Qatar 2022)", 
    classementFifa: "7e", 
    selectionneur: "Mohamed Ouahbi", 
    capitaine: "Achraf Hakimi",
    titre: "Champion d'Afrique en titre (CAN disputée au Maroc, sacre début 2026)"
  },
  prochainMatch: { 
    adversaire: "Canada", 
    date: "2026-07-04T16:00:00", // Heure arbitraire pour le compte à rebours
    dateTexte: "samedi 4 juillet 2026",
    stade: "à déterminer", 
    ville: "à déterminer", 
    competitionStage: "Huitième de finale", 
    aVenir: true 
  },
  timeline: [ 
    { 
      id: 1, 
      date: "5 sept. 2025", 
      type: "Qualification", 
      titre: "Premiers qualifiés !", 
      recit: "Victoire contre le Niger au stade Prince Moulay Abdellah (Rabat) ; le Maroc remporte le groupe E de la zone CAF et devient la première nation africaine qualifiée pour 2026.", 
      image: "images/qualif.jpg", 
      chiffreCle: "1ère", 
      labelChiffre: "nation qualifiée",
      score: null 
    },
    { 
      id: 2, 
      date: "5 déc. 2025", 
      type: "Tirage au sort", 
      titre: "Le Groupe C, aux États-Unis", 
      recit: "À Washington, le Maroc (chapeau 2) hérite du Groupe C avec le Brésil, l'Écosse et Haïti. Trois matchs sur la côte Est des USA : déplacements réduits, un avantage stratégique.", 
      image: "images/tirage.jpg", 
      chiffreCle: "Est",
      labelChiffre: "Côte américaine",
      score: null 
    },
    { 
      id: 3, 
      date: "13 juin 2026", 
      type: "Match", 
      titre: "Un nul de patron face au Brésil", 
      recit: "Entrée en lice de prestige au MetLife Stadium (New York/New Jersey). Ismael Saibari ouvre le score avant que le Brésil n'égalise. Un nul de patron contre le futur vainqueur du groupe.", 
      image: "images/bresil-maroc.jpg", 
      hommeDuMatch: "Ismael Saibari", 
      score: "Brésil 1 - 1 Maroc" 
    },
    { 
      id: 4, 
      date: "19 juin 2026", 
      type: "Match", 
      titre: "Victoire décisive dans la douleur", 
      recit: "Au Gillette Stadium (Boston), face à une équipe rugueuse, Ismael Saibari trouve encore le chemin des filets. Une victoire 1-0 précieuse dans un match fermé face à l'Écosse.", 
      image: "images/ecosse-maroc.jpg", 
      hommeDuMatch: "Ismael Saibari", 
      score: "Maroc 1 - 0 Écosse" 
    },
    { 
      id: 5, 
      date: "24 juin 2026", 
      type: "Match", 
      titre: "Renversement héroïque et qualification", 
      recit: "Au Mercedes-Benz Stadium (Atlanta), menés deux fois (csc de Bounou sur talonnade de Joseph 10e, missile d'Isidor 43e), les Lions renversent tout en seconde période : Hakimi (39e), Saibari (45+1), Rahimi (78e), Gessime Yassine (89e). Qualification en 16es.", 
      image: "images/haiti-maroc.jpg", 
      hommeDuMatch: "Achraf Hakimi", 
      score: "Maroc 4 - 2 Haïti" 
    },
    { 
      id: 6, 
      date: "29 juin 2026", 
      type: "Match", 
      titre: "Le miracle de Monterrey", 
      recit: "En 16es de finale à l'Estadio BBVA (Monterrey, Mexique), Gakpo ouvre le score (72e) contre le cours du jeu. Issa Diop égalise de la tête au-dessus de Van Dijk (90+1) ! Séance de tirs au but irrespirable : arrêt décisif de Yassine Bounou puis tir vainqueur de Saibari.", 
      image: "images/paysbas-maroc.jpg", 
      hommeDuMatch: "Yassine Bounou", 
      score: "Pays-Bas 1 - 1 Maroc (2 - 3 t.a.b.)" 
    },
    { 
      id: 7, 
      date: "4 juillet 2026", 
      type: "À venir", 
      titre: "Le duel nord-américain : Canada", 
      recit: "Le Maroc défie le Canada (vainqueur de l'Afrique du Sud 1-0) en huitième de finale. Un match couperet pour écrire une nouvelle page de l'histoire.", 
      image: "images/canada-maroc.jpg", 
      aVenir: true 
    }
  ],
  groupeC: { 
    classement: [
      { rang: 1, equipe: "Brésil", pts: 7, diff: "+6" },
      { rang: 2, equipe: "Maroc", pts: 7, diff: "+3", stats: "2 victoires, 1 nul, 6 buts pour / 3 contre" },
      { rang: 3, equipe: "Écosse", pts: 3, diff: "-1" },
      { rang: 4, equipe: "Haïti", pts: 0, diff: "-8" }
    ], 
    resultats: [
      "Brésil 1-1 Maroc",
      "Écosse 2-1 Haïti",
      "Maroc 1-0 Écosse",
      "Brésil 4-0 Haïti",
      "Maroc 4-2 Haïti",
      "Brésil 2-0 Écosse"
    ] 
  },
  effectif: [ 
    { nom: "Yassine Bounou", poste: "Gardien", club: "Al-Hilal", faitMarquant: "Héros des t.a.b. face aux Pays-Bas." },
    { nom: "Munir Kajoui", poste: "Gardien", club: "Renaissance Berkane", faitMarquant: "" },
    { nom: "Ahmed Reda Tagnaouti", poste: "Gardien", club: "FAR Rabat", faitMarquant: "" },
    { nom: "Achraf Hakimi", poste: "Défenseur", club: "PSG", faitMarquant: "Capitaine, 1 but + 1 passe décisive contre Haïti, barre transversale contre les Pays-Bas." },
    { nom: "Noussair Mazraoui", poste: "Défenseur", club: "Manchester United", faitMarquant: "" },
    { nom: "Anass Salah-Eddine", poste: "Défenseur", club: "PSV", faitMarquant: "" },
    { nom: "Youssef Belammari", poste: "Défenseur", club: "Al Ahly", faitMarquant: "" },
    { nom: "Issa Diop", poste: "Défenseur", club: "Fulham", faitMarquant: "Buteur héroïque face aux Pays-Bas (90+1)." },
    { nom: "Chadi Riad", poste: "Défenseur", club: "Crystal Palace", faitMarquant: "" },
    { nom: "Zakaria El Ouahdi", poste: "Défenseur", club: "KRC Genk", faitMarquant: "" },
    { nom: "Redouane Halhal", poste: "Défenseur", club: "Malines", faitMarquant: "" },
    { nom: "Nayef Aguerd", poste: "Défenseur", club: "OM", faitMarquant: "" },
    { nom: "Neil El Aynaoui", poste: "Milieu", club: "AS Roma", faitMarquant: "" },
    { nom: "Azzedine Ounahi", poste: "Milieu", club: "Gérone", faitMarquant: "" },
    { nom: "Ismael Saibari", poste: "Milieu", club: "PSV", faitMarquant: "Révélation du tournoi, 3 buts en poules + t.a.b. vainqueur." },
    { nom: "Bilal El Khannouss", poste: "Milieu", club: "Stuttgart", faitMarquant: "" },
    { nom: "Samir El Mourabet", poste: "Milieu", club: "Strasbourg", faitMarquant: "" },
    { nom: "Sofyan Amrabat", poste: "Milieu", club: "Betis", faitMarquant: "" },
    { nom: "Ayyoub Bouaddi", poste: "Milieu", club: "Lille", faitMarquant: "" },
    { nom: "Brahim Diaz", poste: "Attaquant", club: "Real Madrid", faitMarquant: "" },
    { nom: "Ayoub El Kaabi", poste: "Attaquant", club: "Olympiakos", faitMarquant: "" },
    { nom: "Abde Ezzalzouli", poste: "Attaquant", club: "Betis", faitMarquant: "" },
    { nom: "Soufiane Rahimi", poste: "Attaquant", club: "Al-Aïn", faitMarquant: "Buteur décisif face à Haïti (78e)." },
    { nom: "Gessime Yassine", poste: "Attaquant", club: "Strasbourg", faitMarquant: "Buteur face à Haïti (89e)." },
    { nom: "Ayoube Amaimouni", poste: "Attaquant", club: "Eintracht Francfort", faitMarquant: "" },
    { nom: "Chemsdine Talbi", poste: "Attaquant", club: "Sunderland", faitMarquant: "" }
  ],
  stats: [
    { titre: "Ismael Saibari", info: "Record de buts", valeur: "3 buts", desc: "Premier Marocain à 3 buts dans une même phase finale (égale le total de carrière d'En-Nesyri), et premier Africain à marquer lors des 3 matchs de poule." },
    { titre: "Yassine Bounou", info: "L'ange gardien", valeur: "Arrêt décisif", desc: "Héros de la séance de tirs au but face aux Pays-Bas, rééditant son exploit de 2022 face à l'Espagne." },
    { titre: "Constance", info: "Histoire", valeur: "7e", desc: "7e participation du Maroc à la Coupe du Monde. Meilleur résultat historique : 4e en 2022." },
    { titre: "Achraf Hakimi", info: "Le capitaine", valeur: "1b, 1pd", desc: "1 but et 1 passe décisive contre Haïti, leader incontesté de la défense et du vestiaire." }
  ],
  heritage2022: {
    titre: "L'Héritage de 2022 : La voie royale",
    texte: "L'épopée du Qatar — une inoubliable 4e place et la première demi-finale africaine de l'histoire, jalonnée de victoires contre l'Espagne et le Portugal — a définitivement changé le statut des Lions de l'Atlas. En 2026, l'équipe ne se contente plus de participer : elle avance avec l'ambition et la confiance d'un grand d'Afrique et du monde."
  }
};
