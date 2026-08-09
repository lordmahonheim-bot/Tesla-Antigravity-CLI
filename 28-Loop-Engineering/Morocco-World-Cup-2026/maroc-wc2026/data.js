/*
 * ═══════════════════════════════════════════════════════════════
 * data.js — Lions de l'Atlas : Parcours Mondial 2026
 * ═══════════════════════════════════════════════════════════════
 *
 * MODE D'EMPLOI :
 * ───────────────
 * Pour mettre à jour le prochain match :
 *   → Éditez l'objet `prochainMatch` ci-dessous.
 *
 * Pour ajouter un événement à la timeline :
 *   → Ajoutez un objet dans le tableau `timeline`.
 *
 * Le reste de l'application ne doit jamais être modifié.
 */

// biome-ignore lint/correctness/noUnusedVariables: APP_DATA est accédé globalement par app.js
const APP_DATA = {
	/* ── Métadonnées ── */
	meta: {
		majLe: "3 juillet 2026",
		version: "2.0",
	},

	/* ── Identité de l'équipe ── */
	equipe: {
		nom: "Maroc",
		surnom: "Les Lions de l'Atlas",
		confederation: "CAF",
		participation: "7e",
		meilleurResultat: "4e place (Qatar 2022)",
		classementFifa: "7e",
		selectionneur: "Mohamed Ouahbi",
		capitaine: "Achraf Hakimi",
		titre:
			"Champion d'Afrique en titre (CAN disputée au Maroc, sacre début 2026)",
	},

	/* ── Prochain match (à actualiser) ── */
	prochainMatch: {
		adversaire: "Canada",
		date: "2026-07-04T18:00:00",
		dateTexte: "vendredi 4 juillet 2026",
		stade: "NRG Stadium",
		ville: "Houston, Texas",
		competitionStage: "Huitième de finale",
		aVenir: true,
	},

	/* ── Timeline chronologique ── */
	timeline: [
		{
			id: 1,
			date: "5 sept. 2025",
			type: "Qualification",
			titre: "Premiers qualifiés !",
			recit:
				"Victoire contre le Niger au stade Prince Moulay Abdellah (Rabat) ; le Maroc remporte le groupe E de la zone CAF et devient la première nation africaine qualifiée pour 2026.",
			image: "images/qualif.svg",
			chiffreCle: "1ère",
			labelChiffre: "nation qualifiée",
			score: null,
		},
		{
			id: 2,
			date: "5 déc. 2025",
			type: "Tirage au sort",
			titre: "Le Groupe C, aux États-Unis",
			recit:
				"À Washington, le Maroc (chapeau 2) hérite du Groupe C avec le Brésil, l'Écosse et Haïti. Trois matchs sur la côte Est des USA : déplacements réduits, un avantage stratégique.",
			image: "images/tirage.svg",
			chiffreCle: "Est",
			labelChiffre: "Côte américaine",
			score: null,
		},
		{
			id: 3,
			date: "13 juin 2026",
			type: "Match",
			titre: "Un nul de patron face au Brésil",
			recit:
				"Entrée en lice de prestige au MetLife Stadium (New York/New Jersey). Ismael Saibari ouvre le score à la 21e minute d'une frappe chirurgicale. Vinícius Júnior égalise à la 32e. Un nul 1-1 de patron contre le futur vainqueur du groupe.",
			image: "images/bresil-maroc.svg",
			hommeDuMatch: "Ismael Saibari",
			score: "Brésil 1 - 1 Maroc",
			buteurs: [
				{ joueur: "Ismael Saibari", minute: "21'", equipe: "Maroc" },
				{ joueur: "Vinícius Júnior", minute: "32'", equipe: "Brésil" },
			],
			stade: "MetLife Stadium",
			ville: "New York / New Jersey",
		},
		{
			id: 4,
			date: "19 juin 2026",
			type: "Match",
			titre: "Victoire éclair face à l'Écosse",
			recit:
				"Au Gillette Stadium (Boston), Ismael Saibari frappe dès la 2e minute — un missile après 71 secondes de jeu. Le Maroc verrouille cette avance et s'impose 1-0 dans un match de caractère.",
			image: "images/ecosse-maroc.svg",
			hommeDuMatch: "Ismael Saibari",
			score: "Maroc 1 - 0 Écosse",
			buteurs: [{ joueur: "Ismael Saibari", minute: "2'", equipe: "Maroc" }],
			stade: "Gillette Stadium",
			ville: "Boston / Foxborough",
		},
		{
			id: 5,
			date: "24 juin 2026",
			type: "Match",
			titre: "Renversement héroïque face à Haïti",
			recit:
				"Au Mercedes-Benz Stadium (Atlanta). CSC de Bounou (10e) puis missile d'Isidor (43e) : 0-2 au tableau. Les Lions renversent tout : Hakimi (39e) avait réduit l'écart, Saibari égalise en fin de première mi-temps (45+1). Rahimi (78e) puis Gessime Yassine (89e) achèvent le festival. 4-2, qualification mathématique en poche.",
			image: "images/haiti-maroc.svg",
			hommeDuMatch: "Achraf Hakimi",
			score: "Maroc 4 - 2 Haïti",
			buteurs: [
				{ joueur: "Bounou (csc)", minute: "10'", equipe: "Haïti" },
				{ joueur: "Achraf Hakimi", minute: "39'", equipe: "Maroc" },
				{ joueur: "Wilson Isidor", minute: "43'", equipe: "Haïti" },
				{ joueur: "Ismael Saibari", minute: "45+1'", equipe: "Maroc" },
				{ joueur: "Soufiane Rahimi", minute: "78'", equipe: "Maroc" },
				{ joueur: "Gessime Yassine", minute: "89'", equipe: "Maroc" },
			],
			stade: "Mercedes-Benz Stadium",
			ville: "Atlanta, Géorgie",
		},
		{
			id: 6,
			date: "29 juin 2026",
			type: "Match",
			titre: "Le miracle de Monterrey",
			recit:
				"32e de finale à l'Estadio BBVA (Monterrey, Mexique). Gakpo ouvre le score à la 72e contre le cours du jeu. Au bord de l'élimination, Issa Diop s'élève au-dessus de Van Dijk pour égaliser de la tête au bout du temps additionnel (90+1). Séance de tirs au but irrespirable : Bounou repousse le tir de Summerville, Saibari transforme le tir décisif. Maroc 3-2 aux t.a.b.",
			image: "images/paysbas-maroc.svg",
			hommeDuMatch: "Yassine Bounou",
			score: "Pays-Bas 1 - 1 Maroc (2 - 3 t.a.b.)",
			buteurs: [
				{ joueur: "Cody Gakpo", minute: "72'", equipe: "Pays-Bas" },
				{ joueur: "Issa Diop", minute: "90+1'", equipe: "Maroc" },
			],
			penaltys: {
				maroc: ["El Aynaoui ✗", "Saibari ✓"],
				paysBas: [
					"Koopmeiners ✓",
					"Kluivert ✗",
					"Weghorst ✓",
					"Timber ✗",
					"Summerville ✗",
				],
				resultat: "Maroc 3 - 2 Pays-Bas",
			},
			actionsDecisives: [
				{
					joueur: "Issa Diop",
					action: "But égalisateur héroïque de la tête à la 90+1",
				},
				{
					joueur: "Yassine Bounou",
					action: "Arrêt décisif sur le tir de Summerville en séance de t.a.b.",
				},
				{
					joueur: "Ismael Saibari",
					action: "Tir au but vainqueur, sang-froid absolu",
				},
			],
			stade: "Estadio BBVA",
			ville: "Monterrey, Mexique",
		},
		{
			id: 7,
			date: "4 juillet 2026",
			type: "À venir",
			titre: "Huitième de finale : Canada",
			recit:
				"Le Maroc affronte le Canada au NRG Stadium (Houston, Texas). Un match couperet pour écrire une nouvelle page de l'histoire des Lions de l'Atlas.",
			image: "images/canada-maroc.svg",
			aVenir: true,
		},
	],

	/* ── Classement final Groupe C ── */
	groupeC: {
		classement: [
			{
				rang: 1,
				equipe: "Brésil",
				mj: 3,
				v: 2,
				n: 1,
				d: 0,
				bp: 7,
				bc: 1,
				diff: "+6",
				pts: 7,
			},
			{
				rang: 2,
				equipe: "Maroc",
				mj: 3,
				v: 2,
				n: 1,
				d: 0,
				bp: 6,
				bc: 3,
				diff: "+3",
				pts: 7,
			},
			{
				rang: 3,
				equipe: "Écosse",
				mj: 3,
				v: 1,
				n: 0,
				d: 2,
				bp: 1,
				bc: 4,
				diff: "-3",
				pts: 3,
			},
			{
				rang: 4,
				equipe: "Haïti",
				mj: 3,
				v: 0,
				n: 0,
				d: 3,
				bp: 2,
				bc: 8,
				diff: "-6",
				pts: 0,
			},
		],
		resultats: [
			"Brésil 1 - 1 Maroc",
			"Écosse 2 - 1 Haïti",
			"Maroc 1 - 0 Écosse",
			"Brésil 4 - 0 Haïti",
			"Maroc 4 - 2 Haïti",
			"Brésil 2 - 0 Écosse",
		],
	},

	/* ── Effectif ── */
	effectif: [
		{
			nom: "Yassine Bounou",
			poste: "Gardien",
			club: "Al-Hilal",
			numero: 1,
			faitMarquant:
				"Héros des t.a.b. face aux Pays-Bas : arrêt décisif sur Summerville.",
		},
		{
			nom: "Munir Kajoui",
			poste: "Gardien",
			club: "Renaissance Berkane",
			numero: 12,
			faitMarquant: "",
		},
		{
			nom: "Ahmed Reda Tagnaouti",
			poste: "Gardien",
			club: "FAR Rabat",
			numero: 23,
			faitMarquant: "",
		},
		{
			nom: "Achraf Hakimi",
			poste: "Défenseur",
			club: "PSG",
			numero: 2,
			faitMarquant:
				"Capitaine incontesté. 1 but contre Haïti (39e), leader défensif et du vestiaire.",
		},
		{
			nom: "Noussair Mazraoui",
			poste: "Défenseur",
			club: "Manchester United",
			numero: 3,
			faitMarquant: "",
		},
		{
			nom: "Anass Salah-Eddine",
			poste: "Défenseur",
			club: "PSV",
			numero: 5,
			faitMarquant: "",
		},
		{
			nom: "Youssef Belammari",
			poste: "Défenseur",
			club: "Al Ahly",
			numero: 4,
			faitMarquant: "",
		},
		{
			nom: "Issa Diop",
			poste: "Défenseur",
			club: "Fulham",
			numero: 6,
			faitMarquant:
				"Buteur héroïque de la tête face aux Pays-Bas (90+1), au-dessus de Van Dijk.",
		},
		{
			nom: "Chadi Riad",
			poste: "Défenseur",
			club: "Crystal Palace",
			numero: 13,
			faitMarquant: "",
		},
		{
			nom: "Zakaria El Ouahdi",
			poste: "Défenseur",
			club: "KRC Genk",
			numero: 15,
			faitMarquant: "",
		},
		{
			nom: "Nayef Aguerd",
			poste: "Défenseur",
			club: "OM",
			numero: 24,
			faitMarquant: "",
		},
		{
			nom: "Neil El Aynaoui",
			poste: "Milieu",
			club: "AS Roma",
			numero: 8,
			faitMarquant: "",
		},
		{
			nom: "Azzedine Ounahi",
			poste: "Milieu",
			club: "Gérone",
			numero: 10,
			faitMarquant: "",
		},
		{
			nom: "Ismael Saibari",
			poste: "Milieu",
			club: "PSV",
			numero: 11,
			faitMarquant:
				"Révélation du tournoi : 3 buts en phase de poules + tir au but vainqueur face aux Pays-Bas. Premier Africain à marquer lors de ses 3 matchs de poule.",
		},
		{
			nom: "Bilal El Khannouss",
			poste: "Milieu",
			club: "Stuttgart",
			numero: 14,
			faitMarquant: "",
		},
		{
			nom: "Sofyan Amrabat",
			poste: "Milieu",
			club: "Betis",
			numero: 16,
			faitMarquant: "",
		},
		{
			nom: "Ayyoub Bouaddi",
			poste: "Milieu",
			club: "Lille",
			numero: 17,
			faitMarquant: "",
		},
		{
			nom: "Brahim Diaz",
			poste: "Attaquant",
			club: "Real Madrid",
			numero: 7,
			faitMarquant: "",
		},
		{
			nom: "Ayoub El Kaabi",
			poste: "Attaquant",
			club: "Olympiakos",
			numero: 9,
			faitMarquant: "",
		},
		{
			nom: "Abde Ezzalzouli",
			poste: "Attaquant",
			club: "Betis",
			numero: 18,
			faitMarquant: "",
		},
		{
			nom: "Soufiane Rahimi",
			poste: "Attaquant",
			club: "Al-Aïn",
			numero: 19,
			faitMarquant: "Buteur décisif face à Haïti (78e).",
		},
		{
			nom: "Gessime Yassine",
			poste: "Attaquant",
			club: "Strasbourg",
			numero: 20,
			faitMarquant: "Buteur face à Haïti (89e), scelle le renversement.",
		},
		{
			nom: "Ayoube Amaimouni",
			poste: "Attaquant",
			club: "Eintracht Francfort",
			numero: 21,
			faitMarquant: "",
		},
		{
			nom: "Chemsdine Talbi",
			poste: "Attaquant",
			club: "Sunderland",
			numero: 22,
			faitMarquant: "",
		},
	],

	/* ── Statistiques clés ── */
	stats: [
		{
			titre: "Ismael Saibari",
			info: "Soulier d'or potentiel",
			valeur: "3 buts",
			desc: "Premier Africain à marquer lors des 3 matchs de poule d'une même Coupe du Monde. T.a.b. vainqueur face aux Pays-Bas.",
		},
		{
			titre: "Yassine Bounou",
			info: "L'ange gardien",
			valeur: "Arrêt décisif",
			desc: "Héros de la séance de tirs au but face aux Pays-Bas, rééditant son exploit de 2022 face à l'Espagne.",
		},
		{
			titre: "Constance historique",
			info: "7e participation",
			valeur: "7e",
			desc: "7e participation du Maroc à la Coupe du Monde. Meilleur résultat historique : 4e en 2022.",
		},
		{
			titre: "Achraf Hakimi",
			info: "Le capitaine",
			valeur: "1b + 1pd",
			desc: "1 but et 1 passe décisive contre Haïti. Leader de la défense et âme du vestiaire.",
		},
	],

	/* ── Héritage du Qatar 2022 ── */
	heritage2022: {
		titre: "L'Héritage de 2022 : La voie royale",
		texte:
			"L'épopée du Qatar — une inoubliable 4e place et la première demi-finale africaine de l'histoire, jalonnée de victoires contre l'Espagne et le Portugal — a définitivement changé le statut des Lions de l'Atlas. En 2026, l'équipe ne se contente plus de participer : elle avance avec l'ambition et la confiance d'un grand d'Afrique et du monde.",
	},
};
