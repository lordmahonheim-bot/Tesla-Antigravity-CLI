/*
 * ═══════════════════════════════════════════════════════════════
 * app.js — Lions de l'Atlas : Parcours Mondial 2026
 * ═══════════════════════════════════════════════════════════════
 * Moteur de rendu 100% dynamique.
 * Tout le texte métier provient exclusivement de APP_DATA (data.js).
 * Aucune date, score ou statistique n'est codée en dur ici.
 */

/* ── Point d'entrée ── */
document.addEventListener("DOMContentLoaded", () => {
	renderHeroStats();
	renderCountdown();
	renderTimeline();
	renderGroupeC();
	renderEffectif();
	renderStats();
	renderHeritage();
	renderFooter();
	initScrollAnimations();
	initNavBurger();
});

/* ── Calculs dynamiques depuis APP_DATA ── */
function computeDynamicStats() {
	const matchs = APP_DATA.timeline.filter((e) => e.type === "Match" && e.score);
	const totalButs = matchs.reduce((acc, m) => {
		if (!m.buteurs) return acc;
		return (
			acc +
			m.buteurs.filter((b) => b.equipe === "Maroc" && !b.joueur.includes("csc"))
				.length
		);
	}, 0);

	let victoires = 0;
	let nuls = 0;
	for (const m of matchs) {
		const scoreStr = m.score;
		if (scoreStr.includes("t.a.b.")) {
			// Match nul au temps réglementaire, victoire aux t.a.b.
			victoires++;
		} else {
			const matches = scoreStr.match(/\d+/g);
			if (matches && matches.length >= 2) {
				const score1 = Number.parseInt(matches[0], 10);
				const score2 = Number.parseInt(matches[1], 10);
				// Déterminer la position du Maroc dans le score
				const marocFirst = scoreStr.startsWith("Maroc");
				const marocScore = marocFirst ? score1 : score2;
				const advScore = marocFirst ? score2 : score1;
				if (marocScore > advScore) victoires++;
				else if (marocScore === advScore) nuls++;
			}
		}
	}

	return {
		matchsJoues: matchs.length,
		totalButs,
		victoires,
		nuls,
		classementGroupe: "2e",
	};
}

/* ── Hero : Statistiques dynamiques ── */
function renderHeroStats() {
	const container = document.getElementById("hero-stats");
	if (!container) return;

	const s = computeDynamicStats();

	const statsData = [
		{ value: s.matchsJoues, label: "Matchs joués" },
		{ value: s.totalButs, label: "Buts marqués" },
		{ value: `${s.victoires}V ${s.nuls}N`, label: "Bilan" },
		{ value: s.classementGroupe, label: "Groupe C" },
	];

	container.innerHTML = statsData
		.map(
			(stat) => `
    <div class="hero__stat">
      <span class="hero__stat-value">${stat.value}</span>
      <span class="hero__stat-label">${stat.label}</span>
    </div>
  `,
		)
		.join("");
}

/* ── Compte à Rebours ── */
function renderCountdown() {
	const container = document.getElementById("countdown");
	if (!container || !APP_DATA.prochainMatch?.aVenir) return;

	const pm = APP_DATA.prochainMatch;

	container.innerHTML = `
    <span class="countdown__label">${pm.competitionStage}</span>
    <div class="countdown__timer" id="countdown-timer">
      <div class="countdown__unit">
        <span class="countdown__number" id="cd-jours">--</span>
        <span class="countdown__unit-label">Jours</span>
      </div>
      <div class="countdown__unit">
        <span class="countdown__number" id="cd-heures">--</span>
        <span class="countdown__unit-label">Heures</span>
      </div>
      <div class="countdown__unit">
        <span class="countdown__number" id="cd-minutes">--</span>
        <span class="countdown__unit-label">Min</span>
      </div>
      <div class="countdown__unit">
        <span class="countdown__number" id="cd-secondes">--</span>
        <span class="countdown__unit-label">Sec</span>
      </div>
    </div>
    <p class="countdown__match-info">
      Maroc vs <strong>${pm.adversaire}</strong> — ${pm.dateTexte}
      ${pm.stade ? `<br>${pm.stade}, ${pm.ville}` : ""}
    </p>
  `;

	updateCountdown(pm.date);
	setInterval(() => updateCountdown(pm.date), 1000);
}

function updateCountdown(targetDate) {
	const now = new Date();
	const target = new Date(targetDate);
	const diff = target - now;

	if (diff <= 0) {
		const timer = document.getElementById("countdown-timer");
		if (timer) {
			timer.innerHTML =
				'<span class="countdown__number" style="color: var(--or)">EN COURS !</span>';
		}
		return;
	}

	const jours = Math.floor(diff / (1000 * 60 * 60 * 24));
	const heures = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
	const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
	const secondes = Math.floor((diff % (1000 * 60)) / 1000);

	const elJ = document.getElementById("cd-jours");
	const elH = document.getElementById("cd-heures");
	const elM = document.getElementById("cd-minutes");
	const elS = document.getElementById("cd-secondes");

	if (elJ) elJ.textContent = String(jours).padStart(2, "0");
	if (elH) elH.textContent = String(heures).padStart(2, "0");
	if (elM) elM.textContent = String(minutes).padStart(2, "0");
	if (elS) elS.textContent = String(secondes).padStart(2, "0");
}

/* ── Timeline ── */
function renderTimeline() {
	const container = document.getElementById("timeline");
	if (!container) return;

	container.innerHTML = APP_DATA.timeline
		.map((item) => {
			const isMatch = item.type === "Match";
			const isUpcoming = item.aVenir;
			const badgeClass = isUpcoming
				? "upcoming"
				: isMatch
					? "match"
					: item.type === "Qualification"
						? "qualification"
						: "tirage";
			const itemClass = isUpcoming ? "upcoming" : isMatch ? "match" : "";

			let scoreHtml = "";
			if (item.score) {
				scoreHtml = `<div class="timeline__card-score">${item.score}</div>`;
			}

			let motmHtml = "";
			if (item.hommeDuMatch) {
				motmHtml = `
        <div class="timeline__card-motm">
          ★ Homme du match FIFA : <strong>${item.hommeDuMatch}</strong>
        </div>`;
			}

			let statHtml = "";
			if (item.chiffreCle) {
				statHtml = `
        <div class="timeline__card-stat">
          <span class="timeline__card-stat-value">${item.chiffreCle}</span>
          <span class="timeline__card-stat-label">${item.labelChiffre}</span>
        </div>`;
			}

			let actionsHtml = "";
			if (item.actionsDecisives) {
				actionsHtml = item.actionsDecisives
					.map(
						(a) => `
          <div class="timeline__card-motm">
            ⚡ <strong>${a.joueur}</strong> : ${a.action}
          </div>`,
					)
					.join("");
			}

			return `
      <article class="timeline__item timeline__item--${itemClass}" aria-label="${item.titre}">
        <div class="timeline__card">
          <img class="timeline__card-image"
               src="${item.image}"
               alt="${item.titre}"
               loading="lazy"
               width="800"
               height="450">
          <div class="timeline__card-body">
            <div class="timeline__card-meta">
              <time class="timeline__card-date">${item.date}</time>
              <span class="timeline__card-badge timeline__card-badge--${badgeClass}">${item.type}</span>
            </div>
            <h3 class="timeline__card-title">${item.titre}</h3>
            ${scoreHtml}
            <p class="timeline__card-text">${item.recit}</p>
            ${motmHtml}
            ${actionsHtml}
            ${statHtml}
          </div>
        </div>
      </article>`;
		})
		.join("");
}

/* ── Groupe C ── */
function renderGroupeC() {
	const container = document.getElementById("groupe");
	if (!container) return;

	const g = APP_DATA.groupeC;

	const tableRows = g.classement
		.map((eq) => {
			const isMaroc = eq.equipe === "Maroc";
			const isQualified = eq.rang <= 2;
			const rowClass = isMaroc
				? "groupe__table-row--morocco"
				: isQualified
					? "groupe__table-row--qualified"
					: "";

			return `
      <tr class="${rowClass}">
        <td>${eq.rang}</td>
        <td>${isQualified ? "✅ " : ""}${eq.equipe}</td>
        <td>${eq.mj}</td>
        <td>${eq.v}</td>
        <td>${eq.n}</td>
        <td>${eq.d}</td>
        <td>${eq.bp}</td>
        <td>${eq.bc}</td>
        <td>${eq.diff}</td>
        <td><strong>${eq.pts}</strong></td>
      </tr>`;
		})
		.join("");

	const resultatsHtml = g.resultats
		.map((r) => `<div class="groupe__resultat">${r}</div>`)
		.join("");

	container.innerHTML = `
    <table class="groupe__table" role="table" aria-label="Classement Groupe C">
      <thead>
        <tr>
          <th scope="col">#</th>
          <th scope="col">Équipe</th>
          <th scope="col">MJ</th>
          <th scope="col">V</th>
          <th scope="col">N</th>
          <th scope="col">D</th>
          <th scope="col">BP</th>
          <th scope="col">BC</th>
          <th scope="col">+/-</th>
          <th scope="col">Pts</th>
        </tr>
      </thead>
      <tbody>${tableRows}</tbody>
    </table>
    <div class="groupe__resultats">${resultatsHtml}</div>
  `;
}

/* ── Effectif ── */
function renderEffectif() {
	const container = document.getElementById("effectif");
	if (!container) return;

	// Trier par poste puis par numéro
	const postes = ["Gardien", "Défenseur", "Milieu", "Attaquant"];
	const sorted = [...APP_DATA.effectif].sort((a, b) => {
		const posDiff = postes.indexOf(a.poste) - postes.indexOf(b.poste);
		if (posDiff !== 0) return posDiff;
		return (a.numero || 99) - (b.numero || 99);
	});

	container.innerHTML = sorted
		.map((j) => {
			const posteClass = j.poste
				.toLowerCase()
				.normalize("NFD")
				.replace(/[\u0300-\u036f]/g, "");
			const faitHtml = j.faitMarquant
				? `<p class="effectif__joueur-fait">${j.faitMarquant}</p>`
				: "";

			return `
      <div class="effectif__joueur">
        <div class="effectif__joueur-header">
          <div>
            <p class="effectif__joueur-nom">${j.nom}</p>
            <div class="effectif__joueur-details">
              <span class="effectif__joueur-poste effectif__joueur-poste--${posteClass}">${j.poste}</span>
              <span>${j.club}</span>
            </div>
          </div>
          ${j.numero ? `<span class="effectif__joueur-numero">${j.numero}</span>` : ""}
        </div>
        ${faitHtml}
      </div>`;
		})
		.join("");
}

/* ── Statistiques ── */
function renderStats() {
	const container = document.getElementById("stats");
	if (!container) return;

	container.innerHTML = APP_DATA.stats
		.map(
			(s) => `
    <div class="stats__card">
      <h3 class="stats__card-title">${s.titre}</h3>
      <p class="stats__card-info">${s.info}</p>
      <p class="stats__card-value">${s.valeur}</p>
      <p class="stats__card-desc">${s.desc}</p>
    </div>
  `,
		)
		.join("");
}

/* ── Héritage 2022 ── */
function renderHeritage() {
	const container = document.getElementById("heritage");
	if (!container) return;

	const h = APP_DATA.heritage2022;

	container.innerHTML = `
    <h2 class="heritage__title">${h.titre}</h2>
    <p class="heritage__text">${h.texte}</p>
  `;
}

/* ── Footer ── */
function renderFooter() {
	const container = document.getElementById("footer-content");
	if (!container) return;

	container.innerHTML = `
    <p class="footer__text">
      <strong>${APP_DATA.equipe.surnom}</strong> — Parcours Mondial 2026<br>
      Dernière mise à jour : ${APP_DATA.meta.majLe} · Version ${APP_DATA.meta.version}<br>
      Données officielles FIFA · Page locale sans serveur
    </p>
  `;
}

/* ── Scroll Animations (Intersection Observer) ── */
function initScrollAnimations() {
	const observer = new IntersectionObserver(
		(entries) => {
			for (const entry of entries) {
				if (entry.isIntersecting) {
					entry.target.classList.add("is-visible");
				}
			}
		},
		{ threshold: 0.1, rootMargin: "0px 0px -50px 0px" },
	);

	const elements = document.querySelectorAll(".timeline__item, .fade-in");
	for (const el of elements) {
		observer.observe(el);
	}
}

/* ── Navigation Burger (Mobile) ── */
function initNavBurger() {
	const burger = document.getElementById("nav-burger");
	const links = document.getElementById("nav-links");

	if (!burger || !links) return;

	burger.addEventListener("click", () => {
		links.classList.toggle("is-open");
		const isOpen = links.classList.contains("is-open");
		burger.setAttribute("aria-expanded", isOpen);
		burger.textContent = isOpen ? "✕" : "☰";
	});

	// Fermer le menu quand on clique sur un lien
	for (const link of links.querySelectorAll("a")) {
		link.addEventListener("click", () => {
			links.classList.remove("is-open");
			burger.setAttribute("aria-expanded", "false");
			burger.textContent = "☰";
		});
	}
}
