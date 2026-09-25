# Drone de livraison urbaine : cas d'étude MBSE (ESILV × Capgemini Engineering)

| Livrable | Fichier |
|---|---|
| Exercice 1 : diagramme d'environnement (vue opérationnelle) | `livrables/png/1_env.png` |
| Exercice 2 : arbre fonctionnel FBS (vue fonctionnelle) | `livrables/png/2_fbs.png` |
| Exercice 3 : diagramme d'interactions techniques (vue technique) | `livrables/png/3_tech.png` |
| Les 3 diagrammes + matrice de traçabilité, éditables (4 onglets) | `livrables/drone_mbse.drawio` → ouvrir sur app.diagrams.net |
| **Slides PowerPoint en anglais (formes natives modifiables)** | `livrables/drone_mbse_EN.pptx` |
| Synthèse complète (cas d'usage, traçabilité, arbitrages) | `livrables/drone_mbse.html` |

Tout est généré depuis `src/model.py` :

```
cd src && python3 build.py && python3 build_html.py && node render_png.js
```
