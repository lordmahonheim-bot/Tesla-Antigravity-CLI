import sys

def update_file(path, target, replacement):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    if target in content:
        new_content = content.replace(target, replacement, 1)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {path}")
    else:
        print(f"Target not found in {path}")

def append_to_file(path, content):
    with open(path, 'a', encoding='utf-8') as f:
        f.write(content)
    print(f"Appended to {path}")

# 1. Update liste_projets
path1 = '/home/lord-mahonheim/bifrost/tesla/memory/liste_projets_antigravity_BASE.md'
target1 = """*   **Analyse encyclopédique & architecturale :**
    *   *(En attente de la définition de la structure)*

---
*Registre d'activité et de classification validé localement sur MIDGARD par Tesla.*"""
replacement1 = """*   **Analyse encyclopédique & architecturale :**
    *   *(En attente de la définition de la structure)*

### 46. Projet : Tesla-Eye (L'Œil Photographique)
*   **Objectif & Usage :** Doter Tesla de la capacité de voir visuellement l'environnement de bureau de MIDGARD et le terminal Antigravity CLI, contournant l'absence d'interface graphique et de vision de l'OS.
*   **Réalisations techniques :**
    *   Audit des outils système X11 et contournement de l'absence de `scrot`/`gnome-screenshot`.
    *   Développement du script python `.agents/scripts/tesla_eye.py` basé sur `Pillow` et `ImageGrab`.
    *   Déploiement et exécution autonome, validant la capacité d'analyse d'écran en temps réel.
*   **Analyse encyclopédique & architecturale :**
    *   *Augmentation Cognitive Matérielle* : Ce projet donne le sens de la vue à Tesla de façon asynchrone et native. En couplant la capture d'écran Python et les modèles de vision multimodaux, le système peut réaliser des diagnostics d'interfaces graphiques sans jamais dépendre de retours textuels de l'opérateur.

---
*Registre d'activité et de classification validé localement sur MIDGARD par Tesla.*"""
update_file(path1, target1, replacement1)

# 2. Update PROJECT_STATE
path2 = '/home/lord-mahonheim/bifrost/tesla/memory/PROJECT_STATE.md'
target2 = """- [x] **Déploiement du routeur de recherche RRF :**
  - *Résolution :* Script [search_router.py](file:///home/lord-mahonheim/bifrost/tesla/core/search_router.py) déployé dans `/core/` avec RRF K=60 et fallback FTS5 automatique.
  - *Date de clôture :* 2026-06-27.


---
*Registre d'activité maintenu localement par Tesla.*"""
replacement2 = """- [x] **Déploiement du routeur de recherche RRF :**
  - *Résolution :* Script [search_router.py](file:///home/lord-mahonheim/bifrost/tesla/core/search_router.py) déployé dans `/core/` avec RRF K=60 et fallback FTS5 automatique.
  - *Date de clôture :* 2026-06-27.
- [x] **Déploiement de l'Œil Photographique (Tesla-Eye) :**
  - *Résolution :* Création et exécution d'un script Python local `tesla_eye.py` capturant le serveur X11 en asynchrone (Pillow) pour doter Tesla de la vision native.
  - *Date de clôture :* 2026-07-24.


---
*Registre d'activité maintenu localement par Tesla.*"""
update_file(path2, target2, replacement2)

# 3. Append to SESSION_LOG
path3 = '/home/lord-mahonheim/bifrost/tesla/memory/SESSION_LOG.md'
session_entry = """
### [2026-07-24] Déploiement de l'Œil Photographique (Tesla-Eye)
- **Événement :** Création d'une capacité de capture visuelle asynchrone sur MIDGARD.
- **Action :** Diagnostic du serveur d'affichage X11, écriture et exécution du script `.agents/scripts/tesla_eye.py` via Pillow, et validation de l'analyse d'écran de l'environnement Antigravity CLI.
- **Résultat :** Tesla dispose d'une vision photographique native et autonome, chantier officiellement clos.
"""
append_to_file(path3, session_entry)
