"""Génère les livrables : drone_mbse.drawio, SVG par diagramme, page HTML."""
import os
from html import escape
from model import (DIAGRAMS, SUBFUNCS, FUNC_NAMES, TRACE, OPS_TRACE, USE_CASES,
                   COMPONENTS, COMP_LABEL, COMP_GROUP, GROUP_LABEL, GROUPS)

OUT = os.path.join(os.path.dirname(__file__), "..", "livrables")

LIGHT = dict(bg="#EEF1F0", surface="#FFFFFF", ink="#15202A", muted="#56636E", line="#D3DAD9",
             line_strong="#9AA6AD", grp="#F3F6F6", accent="#0E6A86", c_in="#2E7D4F", c_out="#0E6A86",
             c_res="#B07A12", c_con="#B0413E", sec="#7C8891", ext="#2B3A47", ext_ink="#F2F5F6",
             f_elec="#C27F0E", f_data="#0E6A86", f_mech="#5E6A73", f_rf="#7456A6", fn="#E3EEF1")
DARK = dict(bg="#0E141A", surface="#151E26", ink="#E3E9ED", muted="#97A4AE", line="#2A3743",
            line_strong="#4A5A67", grp="#1A242D", accent="#5DB8D5", c_in="#62BE8A", c_out="#5DB8D5",
            c_res="#E0A845", c_con="#E27A76", sec="#8795A0", ext="#C9D3DA", ext_ink="#0E141A",
            f_elec="#E0A845", f_data="#5DB8D5", f_mech="#9AA6AF", f_rf="#A88BDB", fn="#1C2D36")


def css_vars(p):
    return ";".join(f"--{k.replace('_', '-')}:{v}" for k, v in p.items())


EDGE_CLASSES = ["c-in", "c-out", "c-res", "c-con", "sec", "f-elec", "f-data", "f-mech", "f-rf"]
DIAGRAM_CSS = """
.dg{font-family:var(--font-body,'IBM Plex Sans',Arial,sans-serif);display:block}
.dg text{fill:var(--ink)}
.dg .bgr{fill:var(--surface)}
.dg .n{fill:var(--surface);stroke:var(--line-strong);stroke-width:1.2}
.dg .n.sys{fill:var(--ink);stroke:var(--ink)}
.dg .n.sys+text,.dg .t-sys{fill:var(--surface)}
.dg .n.fn{fill:var(--fn);stroke:var(--accent);stroke-width:1.4}
.dg .n.ext{fill:var(--ext);stroke:var(--ext)}
.dg .t-ext{fill:var(--ext-ink)}
.dg .n.sec{stroke:var(--sec);stroke-dasharray:5 4}
.dg .t2{fill:var(--muted);font-weight:400}
.dg .t-sys .t2,.dg .t-ext .t2{fill:inherit;opacity:.8}
.dg .t1{font-weight:600}
.dg .e{fill:none;stroke-width:1.6;stroke-linejoin:round}
.dg .e.tree{stroke:var(--line-strong);stroke-width:1.3}
.dg .e.dash{stroke-dasharray:5 4}
.dg .lbg{fill:var(--surface);opacity:.94}
.dg .lt{font-size:10.5px;fill:var(--muted)}
.dg .grp{fill:var(--grp);stroke:var(--line)}
.dg .grp-t{font-family:var(--font-mono,'IBM Plex Mono',monospace);font-size:10px;font-weight:600;letter-spacing:.08em;fill:var(--muted)}
.dg .bnd{fill:none;stroke:var(--ink);stroke-width:1.5;stroke-dasharray:9 5}
.dg .bnd-t{font-family:var(--font-mono,'IBM Plex Mono',monospace);font-size:11px;font-weight:600;letter-spacing:.06em;fill:var(--ink)}
.dg .lg{font-size:11.5px;fill:var(--ink)}
.dg .note{font-size:11px;fill:var(--muted);font-style:italic}
.dg .zone{font-family:var(--font-mono,'IBM Plex Mono',monospace);font-size:15px;font-weight:600;letter-spacing:.12em;fill:var(--ink)}
""" + "".join(
    f".dg .e.{c}{{stroke:var(--{c})}}.dg .mk.{c}{{fill:var(--{c})}}.dg .n.{c}{{stroke:var(--{c});stroke-width:2}}"
    for c in EDGE_CLASSES)


def tw(s, fs):  # largeur de texte estimée
    return max(len(l) for l in s.split("\n")) * fs * 0.56


def label_pos(e):
    if e["lp"]:
        return e["lp"]
    pts = e["pts"]
    best = max(range(len(pts) - 1), key=lambda i: abs(pts[i + 1][0] - pts[i][0]) + abs(pts[i + 1][1] - pts[i][1]))
    a, b = pts[best], pts[best + 1]
    return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)


def text_block(x, y, label, fs, lh, cls="", first_bold=True, extra=""):
    lines = label.split("\n")
    y0 = y - (len(lines) - 1) * lh / 2
    out = [f'<text x="{x}" y="{y0}" font-size="{fs}" text-anchor="middle" dominant-baseline="central" class="{cls}"{extra}>']
    for i, l in enumerate(lines):
        c = ("t1" if i == 0 else "t2") if first_bold and len(lines) > 1 else ""
        dy = "0" if i == 0 else str(lh)
        out.append(f'<tspan x="{x}" dy="{dy}" class="{c}">{escape(l)}</tspan>')
    out.append("</text>")
    return "".join(out)


def svg(d, standalone=False):
    p = []
    p.append(f'<svg class="dg dg-{d.key}" viewBox="0 0 {d.w} {d.h}" xmlns="http://www.w3.org/2000/svg" '
             f'role="img" aria-label="{escape(d.title)}"' + (f' width="{d.w}" height="{d.h}"' if standalone else "") + ">")
    if standalone:
        p.append(f"<style>.dg{{{css_vars(LIGHT)}}}{DIAGRAM_CSS}</style>")
        p.append(f'<rect class="bgr" width="{d.w}" height="{d.h}"/>')
    p.append("<defs>")
    for c in EDGE_CLASSES:
        p.append(f'<marker id="m-{d.key}-{c}" viewBox="0 0 10 10" refX="9.5" refY="5" markerWidth="7" '
                 f'markerHeight="7" orient="auto-start-reverse"><path class="mk {c}" d="M0,0 L10,5 L0,10 z"/></marker>')
    p.append("</defs>")
    p.append(f'<g transform="translate({d.dx},0)">')
    for g in d.groups:
        w, h = g["x1"] - g["x0"], g["y1"] - g["y0"]
        if g["cls"] == "bnd":
            p.append(f'<rect class="bnd" x="{g["x0"]}" y="{g["y0"]}" width="{w}" height="{h}" rx="10"/>')
            p.append(f'<text class="bnd-t" x="{g["x0"] + 12}" y="{g["y1"] - 10}">{escape(g["label"].upper())}</text>')
        else:
            p.append(f'<rect class="grp" x="{g["x0"]}" y="{g["y0"]}" width="{w}" height="{h}" rx="6"/>')
            p.append(f'<text class="grp-t" x="{g["lx"]}" y="{g["y0"] + 15}">{escape(g["label"])}</text>')
    for e in d.edges:
        pts = " ".join(f"{x},{y}" for x, y in e["pts"])
        m = ""
        if e["arrow"]:
            m += f' marker-end="url(#m-{d.key}-{e["cls"]})"'
            if e["both"]:
                m += f' marker-start="url(#m-{d.key}-{e["cls"]})"'
        cls = f'e {e["cls"]}' + (" dash" if e["dash"] else "")
        p.append(f'<polyline class="{cls}" points="{pts}"{m}/>')
    for n in d.nodes.values():
        x0, y0 = n["cx"] - n["w"] / 2, n["cy"] - n["h"] / 2
        rx = 8 if n["cls"] in ("sys", "fn") else 6
        p.append(f'<rect class="n {n["cls"]}" x="{x0}" y="{y0}" width="{n["w"]}" height="{n["h"]}" rx="{rx}"/>')
        fs = {"sys": 15, "fn": 12.5, "sub": 11}.get(n["cls"], 12)
        tcls = {"sys": "t-sys", "ext": "t-ext"}.get(n["cls"], "")
        bold_all = n["cls"] in ("sys", "fn")
        p.append(text_block(n["cx"], n["cy"], n["label"], fs, fs * 1.28, tcls,
                            first_bold=n["cls"] not in ("sub", "fn", "sys"),
                            extra=' font-weight="600"' if bold_all else ""))
    for e in d.edges:
        if not e["label"]:
            continue
        x, y = label_pos(e)
        fs, lh = 10.5, 12.5
        n = e["label"].count("\n") + 1
        w, h = tw(e["label"], fs) + 8, n * lh + 4
        p.append(f'<rect class="lbg" x="{x - w / 2}" y="{y - h / 2}" width="{w}" height="{h}" rx="3"/>')
        p.append(text_block(x, y, e["label"], fs, lh, "lt", first_bold=False))
    if d.legend:
        x, y = d.legend_pos
        for c, lab in d.legend:
            dash = ' stroke-dasharray="5 4"' if c == "sec" else ""
            p.append(f'<line class="e {c}" x1="{x}" y1="{y}" x2="{x + 28}" y2="{y}"{dash} marker-end="url(#m-{d.key}-{c})"/>')
            p.append(f'<text class="lg" x="{x + 36}" y="{y}" dominant-baseline="central">{escape(lab)}</text>')
            x += 50 + len(lab) * 6.6
    for (x, y), t in d.notes:
        p.append(f'<text class="note" x="{x}" y="{y}">{escape(t)}</text>')
    for x, y, t in d.texts:
        p.append(f'<text class="zone" x="{x}" y="{y}" text-anchor="middle">{escape(t)}</text>')
    p.append("</g></svg>")
    return "".join(p)


# ------------------------------------------------------------------ draw.io
L = LIGHT


def dstyle(**kw):
    return "".join(f"{k}={v};" for k, v in kw.items())


NODE_STYLE = {
    "sys": dstyle(rounded=1, arcSize=10, fillColor=L["ink"], strokeColor=L["ink"], fontColor="#FFFFFF", fontSize=15, fontStyle=1),
    "fn": dstyle(rounded=1, arcSize=10, fillColor=L["fn"], strokeColor=L["accent"], fontSize=12, fontStyle=1),
    "sub": dstyle(rounded=1, arcSize=10, fillColor="#FFFFFF", strokeColor=L["line_strong"], fontSize=11),
    "cmp": dstyle(rounded=1, arcSize=10, fillColor="#FFFFFF", strokeColor=L["line_strong"], fontSize=11),
    "ext": dstyle(rounded=1, arcSize=10, fillColor=L["ext"], strokeColor=L["ext"], fontColor="#FFFFFF", fontSize=11),
    "sec": dstyle(rounded=1, arcSize=10, fillColor="#FFFFFF", strokeColor=L["sec"], dashed=1, fontSize=11),
}
for c in ("c-in", "c-out", "c-res", "c-con"):
    NODE_STYLE[c] = dstyle(rounded=1, arcSize=10, fillColor="#FFFFFF", strokeColor=L[c.replace("-", "_")], strokeWidth=2, fontSize=12)


def x(s):
    return escape(s, quote=True)


def html_label(s):
    lines = s.split("\n")
    return "<b>" + escape(lines[0]) + "</b>" + "".join("<br>" + escape(l) for l in lines[1:]) if len(lines) > 1 else escape(s)


def drawio_page(d, pid):
    cells = ['<mxCell id="0"/>', '<mxCell id="1" parent="0"/>']
    boxes = {}
    dx = d.dx
    for g in d.groups:
        w, h = g["x1"] - g["x0"], g["y1"] - g["y0"]
        boxes[g["id"]] = (g["x0"], g["y0"], w, h)
        if g["cls"] == "bnd":
            st = dstyle(rounded=1, arcSize=2, fillColor="none", strokeColor=L["ink"], dashed=1, strokeWidth=1.5,
                        verticalAlign="bottom", align="left", spacingLeft=10, spacingBottom=4, fontStyle=1, fontSize=11)
            lab = g["label"].upper()
        else:
            st = dstyle(rounded=1, arcSize=4, fillColor=L["grp"], strokeColor=L["line"], verticalAlign="top",
                        align="left", spacingLeft=g["lx"] - g["x0"], fontStyle=1, fontSize=10, fontColor=L["muted"])
            lab = g["label"]
        cells.append(f'<mxCell id="{pid}-{g["id"]}" value="{x(lab)}" style="{st}html=1;whiteSpace=wrap;" vertex="1" parent="1">'
                     f'<mxGeometry x="{g["x0"] + dx}" y="{g["y0"]}" width="{w}" height="{h}" as="geometry"/></mxCell>')
    for n in d.nodes.values():
        x0, y0 = n["cx"] - n["w"] / 2, n["cy"] - n["h"] / 2
        boxes[n["id"]] = (x0, y0, n["w"], n["h"])
        lab = html_label(n["label"]) if n["cls"] not in ("sub", "fn", "sys") else escape(n["label"]).replace("\n", "<br>")
        cells.append(f'<mxCell id="{pid}-{n["id"]}" value="{x(lab)}" style="{NODE_STYLE[n["cls"]]}html=1;whiteSpace=wrap;" vertex="1" parent="1">'
                     f'<mxGeometry x="{x0 + dx}" y="{y0}" width="{n["w"]}" height="{n["h"]}" as="geometry"/></mxCell>')
    for i, e in enumerate(d.edges):
        pts = e["pts"]
        sx, sy, sw, sh = boxes[e["src"]]
        tx, ty, tw_, th = boxes[e["dst"]]
        # l'ordre des points suit la flèche ; source/target doivent suivre le même ordre
        (ax, ay), (bx, by) = pts[0], pts[-1]

        def rel(px, py, b):
            return min(max((px - b[0]) / b[2], 0), 1), min(max((py - b[1]) / b[3], 0), 1)
        s_box, t_box = boxes[e["src"]], boxes[e["dst"]]
        if not (s_box[0] - 1 <= ax <= s_box[0] + s_box[2] + 1 and s_box[1] - 1 <= ay <= s_box[1] + s_box[3] + 1):
            s_box, t_box = t_box, s_box
            src, dst = e["dst"], e["src"]
        else:
            src, dst = e["src"], e["dst"]
        ex, ey = rel(ax, ay, s_box)
        nx, ny = rel(bx, by, t_box)
        color = L.get(e["cls"].replace("-", "_"), L["line_strong"])
        if e["cls"] == "tree":
            color = L["line_strong"]
        st = dstyle(edgeStyle="none", rounded=0, html=1, strokeColor=color, strokeWidth=1.6, fontSize=10,
                    fontColor=L["muted"], labelBackgroundColor="#FFFFFF",
                    endArrow="block" if e["arrow"] else "none", endFill=1, endSize=5,
                    startArrow="block" if e["both"] else "none", startFill=1, startSize=5,
                    exitX=round(ex, 4), exitY=round(ey, 4), exitPerimeter=0,
                    entryX=round(nx, 4), entryY=round(ny, 4), entryPerimeter=0)
        if e["dash"]:
            st += "dashed=1;"
        # position du libellé le long du tracé (-1..1)
        lx, ly = label_pos(e)
        segs = list(zip(pts, pts[1:]))
        lens = [abs(b[0] - a[0]) + abs(b[1] - a[1]) for a, b in segs]
        tot, acc, best = sum(lens) or 1, 0, (1e9, 0.5)
        for (a, b), ln in zip(segs, lens):
            for k in range(0, 41):
                t = k / 40
                px, py = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                dd = (px - lx) ** 2 + (py - ly) ** 2
                if dd < best[0]:
                    best = (dd, (acc + ln * t) / tot)
            acc += ln
        rel_x = round(2 * best[1] - 1, 3)
        if src != e["src"]:
            rel_x = -rel_x
        wp = "".join(f'<mxPoint x="{px + dx}" y="{py}"/>' for px, py in (pts[1:-1] if src == e["src"] else pts[-2:0:-1]))
        lab = escape(e["label"]).replace("\n", "<br>")
        cells.append(f'<mxCell id="{pid}-e{i}" value="{x(lab)}" style="{st}" edge="1" parent="1" source="{pid}-{src}" target="{pid}-{dst}">'
                     f'<mxGeometry x="{rel_x}" relative="1" as="geometry"><Array as="points">{wp}</Array></mxGeometry></mxCell>')
    if d.legend:
        lx, ly = d.legend_pos
        for j, (c, lab) in enumerate(d.legend):
            col = L[c.replace("-", "_")]
            st = dstyle(endArrow="block", endFill=1, endSize=5, strokeColor=col, strokeWidth=1.6, html=1) + ("dashed=1;" if c == "sec" else "")
            cells.append(f'<mxCell id="{pid}-lg{j}" style="{st}" edge="1" parent="1"><mxGeometry relative="1" as="geometry">'
                         f'<mxPoint x="{lx + dx}" y="{ly}" as="sourcePoint"/><mxPoint x="{lx + dx + 28}" y="{ly}" as="targetPoint"/></mxGeometry></mxCell>')
            w = len(lab) * 6.6 + 10
            cells.append(f'<mxCell id="{pid}-lgt{j}" value="{x(lab)}" style="text;html=1;align=left;verticalAlign=middle;fontSize=11;" vertex="1" parent="1">'
                         f'<mxGeometry x="{lx + dx + 34}" y="{ly - 10}" width="{w}" height="20" as="geometry"/></mxCell>')
            lx += 50 + len(lab) * 6.6
    for j, ((nx_, ny_), t) in enumerate(d.notes):
        cells.append(f'<mxCell id="{pid}-note{j}" value="{x(t)}" style="text;html=1;align=left;verticalAlign=middle;fontSize=11;fontStyle=2;fontColor={L["muted"]};" vertex="1" parent="1">'
                     f'<mxGeometry x="{nx_ + dx}" y="{ny_ - 10}" width="700" height="20" as="geometry"/></mxCell>')
    for j, (tx, ty, t) in enumerate(d.texts):
        cells.append(f'<mxCell id="{pid}-zone{j}" value="{x(t)}" style="text;html=1;align=center;verticalAlign=middle;fontSize=15;fontStyle=1;" vertex="1" parent="1">'
                     f'<mxGeometry x="{tx + dx - 150}" y="{ty - 12}" width="300" height="24" as="geometry"/></mxCell>')
    return (f'<diagram id="{pid}" name="{x(d.title)}"><mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" '
            f'guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{d.w}" '
            f'pageHeight="{d.h}" math="0" shadow="0"><root>{"".join(cells)}</root></mxGraphModel></diagram>')


def drawio_matrix(pid):
    cells = ['<mxCell id="0"/>', '<mxCell id="1" parent="0"/>']
    comps = [c[0] for c in COMPONENTS]
    x0, y0, cw, rh, fw = 20, 20, 30, 22, 250
    hh = 150
    base = dstyle(html=1, whiteSpace="wrap", strokeColor=L["line"], fontSize=10)

    def cell(i, val, xx, yy, w, h, extra=""):
        cells.append(f'<mxCell id="{pid}-{i}" value="{x(val)}" style="{base}{extra}" vertex="1" parent="1">'
                     f'<mxGeometry x="{xx}" y="{yy}" width="{w}" height="{h}" as="geometry"/></mxCell>')
    cell("corner", "Fonction \\ Composant", x0, y0 + 20, fw, hh - 20, "fillColor=#FFFFFF;fontStyle=1;align=left;spacingLeft=6;verticalAlign=bottom;")
    # bandeau sous-systèmes
    k = 0
    for gid, glab, *_ in GROUPS:
        members = [c for c in comps if COMP_GROUP[c] == gid]
        cell(f"g{gid}", glab, x0 + fw + k * cw, y0, len(members) * cw, 20, f"fillColor={L['grp']};fontStyle=1;fontSize=9;")
        k += len(members)
    order = [c for gid, *_ in GROUPS for c in comps if COMP_GROUP[c] == gid]
    for j, c in enumerate(order):
        cell(f"h{c}", COMP_LABEL[c], x0 + fw + j * cw, y0 + 20, cw, hh - 20,
             "fillColor=#FFFFFF;horizontal=0;align=left;spacingLeft=4;verticalAlign=middle;")
    y = y0 + hh
    for fid in FUNC_NAMES:
        cell(f"r{fid}", f"{fid}  {FUNC_NAMES[fid]}", x0, y, fw + len(order) * cw, rh,
             f"fillColor={L['fn']};fontStyle=1;align=left;spacingLeft=6;")
        y += rh
        for sid, name, f in SUBFUNCS:
            if f != fid:
                continue
            cell(f"r{sid}", f"{sid}  {name}", x0, y, fw, rh, "fillColor=#FFFFFF;align=left;spacingLeft=14;")
            for j, c in enumerate(order):
                on = c in TRACE[sid]
                cell(f"c{sid}-{c}", "●" if on else "", x0 + fw + j * cw, y, cw, rh,
                     f"fillColor={'#DCEEF3' if on else '#FFFFFF'};fontColor={L['accent']};fontSize=12;")
            y += rh
    return (f'<diagram id="{pid}" name="Matrice de traçabilité"><mxGraphModel grid="1" gridSize="10" page="1" '
            f'pageWidth="1000" pageHeight="{y + 20}"><root>{"".join(cells)}</root></mxGraphModel></diagram>')


def build_drawio():
    pages = [drawio_page(d, f"p{i}") for i, d in enumerate(DIAGRAMS)] + [drawio_matrix("p9")]
    return f'<mxfile host="app.diagrams.net" type="device">{"".join(pages)}</mxfile>'


if __name__ == "__main__":
    os.makedirs(os.path.join(OUT, "png"), exist_ok=True)
    with open(os.path.join(OUT, "drone_mbse.drawio"), "w", encoding="utf-8") as f:
        f.write(build_drawio())
    os.makedirs(os.path.join(OUT, "svg"), exist_ok=True)
    for i, d in enumerate(DIAGRAMS, 1):
        with open(os.path.join(OUT, "svg", f"{i}_{d.key}.svg"), "w", encoding="utf-8") as f:
            f.write(svg(d, standalone=True))
    print("ok")
