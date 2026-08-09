# Arcanis Taxonomy Brief

## Ségrégation Stricte: SGP vs SGC

- **SGP (Système de Gestion de Projets)** : Se concentre sur les livrables finaux, les composants stables et la vue d'ensemble du cycle de vie du produit (ex: les MVPs validés).
- **SGP (Projets)** est l'état statique et canonique.
- **SGC (Système de Gestion de Chantiers)** : Se concentre sur l'opérationnel, l'état transitoire, les tâches en cours, l'expérimentation et le workflow dynamique (ex: les boucles Loop Engineering).
- **SGC (Chantiers)** est l'environnement d'exécution dynamique.

## Validation de la Logique de Dépendance
La logique de dépendance est validée: les Chantiers (SGC) transforment les tâches en cours pour alimenter progressivement les Projets (SGP) une fois stabilisés. La boucle d'ingénierie (Loop Engineering) se déroule exclusivement dans le domaine SGC. Les résultats finaux (le code validé par MVP 44 et généré par MVP 16) sont ensuite mergés et archivés dans le domaine SGP.
