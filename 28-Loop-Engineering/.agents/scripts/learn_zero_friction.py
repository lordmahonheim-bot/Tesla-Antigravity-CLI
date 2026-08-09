import os

path = "/home/lord-mahonheim/bifrost/tesla/memory/GEMINI.md"
with open(path, "r") as f:
    content = f.read()

new_rule = """
18. **Réflexe d'Assimilation Canonique (Zero-Friction Mapping) :**
    À chaque fois que tu clôtures un chantier, que tu déploies un nouveau Skill, ou que tu crées un nouvel outil système, tu as l'obligation stricte d'exécuter ce protocole de façon autonome, avant de rendre la main à Lord Mahonheim. Tu n'as pas besoin de lui demander l'autorisation pour assimiler ta propre évolution.
    **Protocole d'Assimilation (Cartographie Chirurgicale) :**
    L'intégration doit être atomique et respecter le code génétique de chaque nouveauté. Applique silencieusement la grille suivante :
    - Si tu as créé un Organe Sensoriel ou un Moteur Cognitif (ex: Tesla-Eye) : Cible : `ENGINE.md` et `FORCE_TOOLING.md`. Action : Insérer un paragraphe d'instruction comportementale concis et forcer son utilisation via un corollaire strict.
    - Si tu as forgé un Sous-Agent, un Skill ou un Module Actif : Cible : `AGENTS.md` (Table de Délégation) et `TESLA.json` (Tableau modules.registered). Action : Ajouter une unique ligne de routage définissant la situation de déclenchement et sa destination.
    - Si tu as écrit un Outil d'Exécution ou un Script natif : Cible : `settings.json` (Bloc permissions). Action : Inscrire le script sur liste blanche avec les arguments exacts pour une exécution sans friction future.
    - Pour TOUTES les autres opérations (Fixes, Maintenance, Audits) : Cible : `liste_projets_antigravity_BASE.md` et `PROJECT_STATE.md`. Action : Archiver l'accomplissement sans polluer le Moteur de base.
    **Validation Finale Silencieuse :**
    Toute modification canonique s'effectue via un script Python ou une commande atomique pour préserver le formatage. Une fois terminé, tu confirmes simplement à Lord Mahonheim (en une phrase) que : "Le chantier est clos et la capacité a été nativement assimilée dans l'ADN canonique et synchronisée vers Avalon."
"""

if "Zero-Friction Mapping" not in content:
    with open(path, "a") as f:
        f.write(new_rule)
    print("Rule 18 appended to GEMINI.md")
else:
    print("Rule 18 already exists in GEMINI.md")
