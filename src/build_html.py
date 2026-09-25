"""Page HTML de synthèse (publiée en artifact) : diagrammes SVG en ligne + tables de traçabilité."""
import os
from html import escape as h
from build import svg, css_vars, LIGHT, DARK, DIAGRAM_CSS, OUT
from model import (env, fbs, tech, SUBFUNCS, FUNC_NAMES, TRACE, OPS_TRACE, USE_CASES,
                   COMPONENTS, COMP_LABEL, COMP_GROUP, GROUPS)

order = [c[0] for g in GROUPS for c in COMPONENTS if c[6] == g[0]]
CAT = {"Entrée": "c-in", "Sortie": "c-out", "Ressource": "c-res", "Contrainte": "c-con"}

ops_rows = "".join(
    f'<tr><td><span class="dot {CAT[k]}"></span>{h(a)}</td><td>{h(f)}</td><td class="muted">{k}</td>'
    f'<td>{" ".join(f"<code>{x}</code>" for x in fs)}</td></tr>' for a, f, k, fs in OPS_TRACE)

head1 = "".join(f'<th colspan="{sum(1 for c in order if COMP_GROUP[c] == g[0])}" class="grp-h">{h(g[1])}</th>' for g in GROUPS)
head2 = "".join(f'<th class="rot"><span>{h(COMP_LABEL[c])}</span></th>' for c in order)
body = []
for fid, name in FUNC_NAMES.items():
    body.append(f'<tr class="frow"><th colspan="{len(order) + 1}"><code>{fid}</code> {h(name)}</th></tr>')
    for sid, sname, f in SUBFUNCS:
        if f == fid:
            cells = "".join('<td class="on">●</td>' if c in TRACE[sid] else "<td></td>" for c in order)
            body.append(f'<tr><th class="fn"><code>{sid}</code> {h(sname)}</th>{cells}</tr>')
counts = "".join(f"<td>{sum(1 for s in TRACE.values() if c in s)}</td>" for c in order)
body.append(f'<tr class="tot"><th class="fn">Fonctions réalisées</th>{counts}</tr>')
matrix = f'<table class="mx"><thead><tr><th class="corner" rowspan="2">Fonction \\ composant</th>{head1}</tr><tr>{head2}</tr></thead><tbody>{"".join(body)}</tbody></table>'

uc_rows = "".join(f"<tr><td><code>{i}</code></td><td><strong>{h(t)}</strong></td><td>{h(d)}</td></tr>" for i, t, d in USE_CASES)

TRADEOFFS = [
    ("Mode de dépose", "Treuil depuis le vol stationnaire", "Atterrissage chez le client ; largage sous parachute",
     "Le drone reste hors de portée du public, pas besoin de zone d'atterrissage dégagée en ville."),
    ("Architecture de vol", "Multirotor (quadri ou octo)", "VTOL hybride à voilure fixe",
     "Rayon urbain court (moins de 10 km), stationnaire précis pour la dépose, mécanique simple."),
    ("Liaison de commande", "4G/5G + radio C2 de secours", "Radio dédiée seule ; satellite",
     "Portée hors vue (BVLOS) sans infrastructure propre, redondance exigée par l'analyse de risque."),
    ("Évitement d'obstacles", "Fusion caméras stéréo + LiDAR", "Caméras seules ; radar",
     "Détection des câbles fins et fonctionnement de nuit ; le radar est plus lourd et moins précis."),
]
trade_rows = "".join(f"<tr><td><strong>{h(a)}</strong></td><td>{h(b)}</td><td class='muted'>{h(c)}</td><td>{h(d)}</td></tr>" for a, b, c, d in TRADEOFFS)


def fig(d, cap, minw):
    return (f'<figure class="card"><div class="scroll"><div style="min-width:{minw}px">{svg(d)}</div></div>'
            f'<figcaption>{cap}</figcaption></figure>')


page = f"""<title>Architecture du drone livreur</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=IBM+Plex+Mono:wght@500;600&family=IBM+Plex+Sans:ital,wght@0,400;0,600;1,400&display=swap">
<style>
:root{{{css_vars(LIGHT)};--font-body:'IBM Plex Sans',system-ui,-apple-system,'Segoe UI',Arial,sans-serif;--font-mono:'IBM Plex Mono',ui-monospace,Menlo,Consolas,monospace;--font-disp:'Barlow Condensed','Arial Narrow',Arial,sans-serif;--on:#DCEEF3}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{{css_vars(DARK)};--on:#1B3441;color-scheme:dark}}}}
:root[data-theme="dark"]{{{css_vars(DARK)};--on:#1B3441;color-scheme:dark}}
body{{background:var(--bg);color:var(--ink);font:15px/1.6 var(--font-body)}}
.wrap{{max-width:1180px;margin:0 auto;padding-inline:20px;padding-block:40px 80px;display:grid;gap:56px}}
header{{display:grid;gap:14px}}
.eyebrow,.idx{{font:600 11.5px/1.2 var(--font-mono);letter-spacing:.1em;text-transform:uppercase;color:var(--accent)}}
h1,h2{{font-family:var(--font-disp);font-weight:700;line-height:1.02;text-wrap:balance;margin:0;letter-spacing:.005em}}
h1{{font-size:clamp(40px,7vw,68px)}}
h2{{font-size:clamp(28px,4vw,38px)}}
h3{{font:600 15px/1.3 var(--font-body);margin:0}}
p{{margin:0;max-width:68ch}}
.lede{{font-size:17px;color:var(--muted);max-width:70ch}}
.chain{{display:grid;grid-template-columns:repeat(3,1fr);gap:0;border:1px solid var(--line);border-radius:10px;overflow:hidden;background:var(--surface);margin-top:10px}}
.chain a{{display:grid;gap:4px;padding:16px 18px;color:inherit;text-decoration:none;border-right:1px solid var(--line)}}
.chain a:last-child{{border-right:0}}
.chain a:hover{{background:var(--grp)}}
.chain a:focus-visible{{outline:2px solid var(--accent);outline-offset:-2px}}
.chain b{{font:700 22px/1 var(--font-disp)}}
.chain span{{color:var(--muted);font-size:13.5px}}
section{{display:grid;gap:18px;scroll-margin-top:16px}}
.sh{{display:grid;gap:8px}}
.cols{{display:grid;grid-template-columns:1.2fr 1fr;gap:28px;align-items:start}}
ul.keys{{margin:0;padding-left:18px;display:grid;gap:6px;max-width:68ch}}
.card{{background:var(--surface);border:1px solid var(--line);border-radius:10px;margin:0}}
figure.card{{padding:14px 14px 10px}}
figcaption{{font-size:12.5px;color:var(--muted);padding:8px 4px 0}}
.scroll{{overflow-x:auto}}
table{{border-collapse:collapse;width:100%;font-size:13.5px}}
.tbl{{padding:4px 0}}
.tbl th,.tbl td{{text-align:left;padding:9px 14px;border-bottom:1px solid var(--line);vertical-align:top}}
.tbl th{{font:600 11px/1.2 var(--font-mono);letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}}
.tbl tr:last-child td{{border-bottom:0}}
code{{font:500 12px var(--font-mono);color:var(--accent)}}
.muted{{color:var(--muted)}}
.dot{{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:8px;vertical-align:1px}}
.dot.c-in{{background:var(--c-in)}}.dot.c-out{{background:var(--c-out)}}.dot.c-res{{background:var(--c-res)}}.dot.c-con{{background:var(--c-con)}}
.mx{{font-size:12.5px;width:auto;min-width:100%}}
.mx th,.mx td{{border:1px solid var(--line)}}
.mx td{{width:30px;min-width:30px;text-align:center;color:var(--accent);font-size:13px;padding:3px 0}}
.mx td.on{{background:var(--on)}}
.mx .grp-h{{font:600 9.5px/1.2 var(--font-mono);letter-spacing:.06em;color:var(--muted);background:var(--grp);padding:6px 2px;text-align:center}}
.mx th.rot{{height:150px;vertical-align:bottom;padding:6px 0;font-weight:400;font-size:12px}}
.mx th.rot span{{writing-mode:vertical-rl;transform:rotate(180deg);white-space:nowrap;display:inline-block}}
.mx .corner{{text-align:left;vertical-align:bottom;padding:8px 10px;font:600 11px var(--font-mono);color:var(--muted);text-transform:uppercase;letter-spacing:.06em}}
.mx th.fn{{text-align:left;font-weight:400;padding:4px 10px 4px 18px;white-space:nowrap;position:sticky;left:0;background:var(--surface);z-index:1}}
.mx .corner{{position:sticky;left:0;background:var(--surface);z-index:2}}
.mx tr.frow th{{text-align:left;background:var(--fn);font-weight:600;padding:6px 10px}}
.mx tr.tot td{{color:var(--ink);font-weight:600;background:var(--grp)}}
.mx tr.tot th{{font-weight:600;background:var(--grp)}}
.files{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px}}
.files div{{padding:14px 16px;display:grid;gap:4px}}
.files code{{font-size:12.5px;word-break:break-all}}
.files span{{color:var(--muted);font-size:13px}}
@media (max-width:760px){{.chain{{grid-template-columns:1fr}}.chain a{{border-right:0;border-bottom:1px solid var(--line)}}.cols{{grid-template-columns:1fr}}}}
{DIAGRAM_CSS}
</style>
<div class="wrap">
<header>
  <div class="eyebrow">ESILV · Chaire PLM · Capgemini Engineering · Cas d'étude MBSE</div>
  <h1>Drone de livraison urbaine</h1>
  <p class="lede">Architecture système d'un service de livraison de colis par drone pour le marché mondial.
  Le système est décrit en trois vues successives : environnement, fonctions, composants. Des liens de
  traçabilité justifient le passage d'une vue à l'autre.</p>
  <nav class="chain" aria-label="Vues d'architecture">
    <a href="#operationnel"><span class="idx">Vue opérationnelle · boîte noire</span><b>Pourquoi ?</b><span>Acteurs, systèmes externes et flux échangés</span></a>
    <a href="#fonctionnel"><span class="idx">Vue fonctionnelle · boîte grise</span><b>Quoi ?</b><span>8 fonctions, 42 sous-fonctions</span></a>
    <a href="#technique"><span class="idx">Vue technique · boîte blanche</span><b>Comment ?</b><span>8 sous-systèmes, 24 composants</span></a>
  </nav>
</header>

<section id="cas-usage">
  <div class="sh"><div class="idx">00 · Cadrage</div><h2>Cas d'usage et hypothèses</h2></div>
  <div class="cols">
    <div class="card tbl"><table><thead><tr><th>Id</th><th>Cas d'usage</th><th>Contenu</th></tr></thead><tbody>{uc_rows}</tbody></table></div>
    <div style="display:grid;gap:10px">
      <h3>Hypothèses de dimensionnement</h3>
      <ul class="keys">
        <li>Colis de 2,5 kg au plus, rayon d'action de 10 km autour du hub.</li>
        <li>Vol hors vue du télépilote (BVLOS), supervisé à distance, un opérateur pour plusieurs drones.</li>
        <li>Catégorie « spécifique » du règlement UE 2019/947, analyse de risque SORA, vol dans l'espace U-space.</li>
        <li>Dépose par treuil en vol stationnaire, sans atterrissage chez le client.</li>
        <li>Vol de jour comme de nuit, pluie modérée, vent jusqu'à 12 m/s.</li>
      </ul>
    </div>
  </div>
</section>

<section id="operationnel">
  <div class="sh"><div class="idx">01 · Vue opérationnelle · analyse de l'environnement</div><h2>Diagramme d'environnement</h2></div>
  <p>Le drone est traité comme une boîte noire. Seuls apparaissent ce qui l'entoure pendant son cycle de vie
  (livraison, recharge, maintenance, autorisation) et les flux échangés, classés selon les quatre catégories du cours.</p>
  {fig(env, "14 acteurs et systèmes externes. Le réseau électrique est secondaire : il n'échange avec le drone qu'à travers la station de recharge.", 980)}
  <ul class="keys">
    <li>Deux flux structurants font la mission : le colis entre depuis l'expéditeur, il sort livré chez le destinataire.</li>
    <li>Les ressources (énergie, positionnement, liaison de données, supervision) sont nécessaires sans être transformées.</li>
    <li>Les contraintes pèsent le plus sur l'architecture : réglementation, U-space, météo, obstacles et acceptabilité par les riverains.</li>
  </ul>
</section>

<section id="fonctionnel">
  <div class="sh"><div class="idx">02 · Vue fonctionnelle · analyse comportementale</div><h2>Arbre fonctionnel (FBS)</h2></div>
  <p>Ce que le drone doit faire pour réaliser la mission, sans choix technologique : chaque fonction est un verbe
  à l'infinitif qui transforme des entrées en sorties.</p>
  {fig(fbs, "F0 est la mission. Les fonctions F1 à F8 sont de niveau 1, les sous-fonctions de niveau 2 sont numérotées x.y.", 1080)}
</section>

<section id="technique">
  <div class="sh"><div class="idx">03 · Vue technique · analyse structurelle</div><h2>Diagramme d'interactions techniques</h2></div>
  <p>Les composants concrets (matériel et logiciel) qui réalisent les fonctions, regroupés en sous-systèmes, et les flux
  physiques qu'ils échangent entre eux et avec les systèmes externes. La couleur d'un flux indique sa nature.</p>
  {fig(tech, "L'ordinateur de mission centralise la navigation, l'évitement et la gestion du colis. Le contrôleur de vol garde la stabilisation en boucle courte.", 1080)}
</section>

<section id="tracabilite">
  <div class="sh"><div class="idx">04 · Traçabilité entre les vues</div><h2>Couverture de bout en bout</h2></div>
  <p>Chaque interaction de l'environnement est couverte par au moins une fonction, et chaque fonction par au moins un
  composant. Dans l'autre sens, aucun composant n'est sans fonction : rien d'inutile n'est embarqué.</p>
  <h3>Vue opérationnelle → vue fonctionnelle</h3>
  <div class="card tbl scroll"><table><thead><tr><th>Acteur ou système externe</th><th>Flux</th><th>Catégorie</th><th>Fonctions qui le couvrent</th></tr></thead><tbody>{ops_rows}</tbody></table></div>
  <h3>Vue fonctionnelle → vue technique</h3>
  <div class="card scroll">{matrix}</div>
</section>

<section id="arbitrages">
  <div class="sh"><div class="idx">05 · Arbitrages techniques</div><h2>Choix d'architecture à défendre</h2></div>
  <div class="card tbl scroll"><table><thead><tr><th>Sujet</th><th>Choix retenu</th><th>Alternatives écartées</th><th>Justification</th></tr></thead><tbody>{trade_rows}</tbody></table></div>
</section>

<section id="fichiers">
  <div class="sh"><div class="idx">Fichiers</div><h2>Sources éditables</h2></div>
  <div class="files">
    <div class="card"><code>livrables/drone_mbse.drawio</code><span>Les 3 diagrammes et la matrice, en 4 onglets, à ouvrir dans draw.io (app.diagrams.net).</span></div>
    <div class="card"><code>livrables/png/</code><span>Les 3 diagrammes en PNG haute définition, prêts pour les slides.</span></div>
    <div class="card"><code>src/model.py</code><span>Le modèle unique d'où tout est généré : modifier puis relancer <code>build.py</code>.</span></div>
  </div>
</section>
</div>
"""
with open(os.path.join(OUT, "drone_mbse.html"), "w", encoding="utf-8") as f:
    f.write(page)
print("html", len(page))
