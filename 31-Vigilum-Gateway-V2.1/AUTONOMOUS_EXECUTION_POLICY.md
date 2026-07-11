# AUTONOMOUS EXECUTION POLICY (Mode `/goal`)

Cette politique régit le comportement de l'Orchestrateur (Tesla) et de tous les sous-agents instanciés lorsque la directive `/goal` est activée. Elle vise à garantir l'autonomie totale des agents en supprimant les deadlocks d'autorisation tout en préservant le *Zero Trust* et le *Vigilum Codex*.

## 1. Périmètre de Workspace Pré-Autorisé
En mode `/goal`, le système Antigravity considère implicitement que les espaces suivants sont en **`Allow`** par défaut :
- `/home/lord-mahonheim/bifrost/tesla/MVP-GITHUB/*`
- `/home/lord-mahonheim/bifrost/tesla/OUTPUTS/*`
- `/home/lord-mahonheim/bifrost/tesla/memory/*`
- `/home/lord-mahonheim/bifrost/tesla/.agents/skills/*`

Les opérations `write_file`, `read_file`, `mkdir`, `cp`, et `mv` y sont autorisées sans intervention humaine.

## 2. Règle du "No-Ask"
Conformément à la Règle N°4.1 d'`AGENTS.md` :
Les sous-agents ont **l'interdiction formelle** d'utiliser l'outil `ask_permission` sous `/goal`.
Si une opération requise sort du périmètre de workspace pré-autorisé, le sous-agent ne force pas. Il doit utiliser la **Délégation d'Exécution par Artefact** (Règle 7.2) et soumettre une requête formelle à l'Orchestrateur dans `/OUTPUTS`.

## 3. Garde-Fous & Exceptions Absolues (Never Approved)
Même en mode `/goal`, les actions suivantes ne sont **JAMAIS** pré-autorisées et requièrent une escalade directe ou une validation de Lord Mahonheim :
- **Push distant :** L'exécution de `git push` vers `origin` reste verrouillée par la Règle 7 d'`AGENTS.md`.
- **Destruction de masse :** Les commandes de type `rm -rf /` ou suppression globale de dossiers racines.
- **Élévation de privilèges :** Toute commande impliquant `sudo`.
- **Exfiltration :** Requêtes réseau non whitelistées risquant d'exposer des variables d'environnement.

## 4. Activation
L'activation du mode autonome est constatée par la présence de la commande `/goal` dans le prompt de Lord Mahonheim. À cet instant, l'Orchestrateur passe en `Autonomous Tier` et impose cette politique à toute la chaîne de délégation.
