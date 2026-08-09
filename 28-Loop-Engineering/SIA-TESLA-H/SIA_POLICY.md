# SIA-TESLA-H : Registre des Politiques Officielles (SIA_POLICY)

## 1. Doctrine d'Auto-Amélioration
Ce système opère sous la doctrine **Harness-Only**.
- **ARTICLE 1 :** L'auto-modification des poids des LLMs est proscrite. L'amélioration continue s'applique uniquement au "Harness" (prompts, workflows, memory, règles).
- **ARTICLE 2 :** L'Agent ne doit en aucun cas modifier un fichier CANONICAL de manière directe et furtive. La route canonique est : `RCA → PATCH_QUEUE → ARENA → GATE → CANONICAL`.
- **ARTICLE 3 :** Taux de patch appliqué hors-Gate = 0. C'est un invariant.

## 2. Token-Frugalité et Limites (Hard-Caps)
- Budget global de token de la mission : **540k tokens (E/S)**
- Cap par mission (tâche unique) : **10k - 15k tokens**, ou baseline +20%.
- Boucle courte (LSP) : **Max 3 retries**. Limite de temps: 5-10 min.
- Boucle longue : Limite de temps: 20-30 min. Max 1 patch principal + 1 alternatif. Max 3 générations SIA.

## 3. Garbage Collection et "Semantic Bloat"
- Les `SKILL.md` et autres documents critiques ne doivent pas dépasser **8k tokens** ou **150 lignes**.
- Croissance hebdomadaire d'un SKILL plafonnée à **+500 bytes** ou **+5%**.
- **Refactorisation obligatoire :** Interdiction pour le Meta-Agent d'ajouter du texte au bout d'un document. Il doit condenser et réécrire pour respecter les seuils de taille.

## 4. Fitness Multi-Signal (Score d'Évaluation)
L'évaluation des propositions de patch repose sur une pondération stricte :
- LSP/Pyright : 20%
- Tests (Unit & Smoke) : 25%
- Score Mission : 20%
- Sécurité : 15%
- Coût Tokens : 10%
- Temps : 5%
- Maintenabilité : 3%
- Confiance : 2%

**Règle d'Or de la Porte (Gate) :** Tout patch générant une régression de sécurité ou violant les limites budgétaires est REJETÉ IMMÉDIATEMENT, même si le code compile.
