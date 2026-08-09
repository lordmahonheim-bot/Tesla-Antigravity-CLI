# Topo Pédagogique : Le Framework Superpowers & /superpowers:writing-skills

## 1. Origine et Philosophie
Le framework **"Superpowers"** a été créé par l'ingénieur Jesse Vincent (alias *obra*) et l'équipe de *Prime Radiant*. Il s'adresse aux développeurs utilisant des agents IA (comme Claude Code, Cursor, ou Antigravity CLI). 

**Le problème résolu :** Les agents IA ont une tendance naturelle au "vibe coding" — ils se précipitent pour coder dès qu'ils reçoivent une instruction, sans planifier ni tester, générant ainsi du code fragile.
**La solution :** Superpowers impose une discipline d'ingénierie stricte à l'IA en structurant ses compétences (skills) via des principes empruntés au génie logiciel classique.

## 2. La Méta-Compétence : `/superpowers:writing-skills`
La commande `writing-skills` n'est pas une compétence métier (comme "déboguer" ou "créer un composant"). C'est une **méta-compétence** : elle permet à l'agent de s'auto-enseigner la création rigoureuse de nouvelles compétences.

### Le TDD appliqué à la cognition de l'IA
La mécanique de `writing-skills` transpose le **Test-Driven Development (TDD)** à la rédaction de prompts et de fichiers Markdown :
1. **RED (L'échec) :** On demande à l'agent d'exécuter une tâche sans la compétence. L'agent échoue ou hallucine. On identifie précisément ce manque cognitif.
2. **GREEN (La directive) :** On rédige un fichier Markdown strict (`SKILL.md`) imposant des règles qui corrigent spécifiquement les erreurs observées à l'étape 1.
3. **REFACTOR (L'optimisation) :** On affine le texte pour réduire le nombre de tokens (mots) tout en bouchant les éventuelles failles ou mauvaises interprétations de l'agent.

## 3. L'Anatomie Technique (La Règle d'Or)
Pour que la compétence soit lue et respectée par le LLM, Superpowers utilise une architecture hybride :
*   **Frontmatter YAML :** En-tête du fichier contenant les métadonnées (nom, version) et une courte description. C'est le *Skill Discovery Optimization* (SDO) qui permet à l'agent de savoir que la compétence existe.
*   **Corps Markdown :** Les instructions réelles, séparées en sections (`Overview`, `When to Use`, `Core Pattern`, `Common Mistakes`).

**🚨 LA RÈGLE D'OR : Le "Vide d'Information"**
Il est formellement interdit de résumer le workflow d'une compétence dans sa description YAML (ex: ne pas dire *"Ce skill lit le fichier, puis corrige le bug et lance les tests"*).
*Pourquoi ?* Si l'on résume la tâche, l'agent IA sera fainéant : il se contentera de lire ce résumé et tentera d'exécuter la tâche "à l'instinct", provoquant des hallucinations. En ne décrivant **que les symptômes de déclenchement** dans le YAML (ex: *"À utiliser en cas de problème de performance"*), on force techniquement l'agent à charger et lire l'intégralité du fichier Markdown pour savoir quoi faire.

## 4. Bénéfices Concrets pour l'Ingénieur
*   **Structuration non-destructive :** Permet d'encadrer l'IA dans un "bac à sable de réflexion" (brainstorming, planification socratique) avant qu'elle ne touche au code de production.
*   **Prédictibilité :** Transforme les comportements chaotiques émergents en routines d'exécution stables, vérifiables et versionnables.
*   **Auto-génération ciblée :** Autorise le développeur à demander à son agent de créer lui-même le squelette d'une nouvelle convention d'équipe (ex: checklist de revue de code) de manière structurée.
