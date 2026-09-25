"""Exporte les diagrammes anglais en JSON pour le générateur PowerPoint."""
import json, os
from model import en, fbs_en, tech_en, COMPONENTS, COMP_EN, GROUPS, TRACE, SUBFUNCS_EN
from model import TECH_EN
from build import label_pos, LIGHT, OUT

COVERAGE = [
    ("Constraint", "Regulator", "Laws, standards", "5.4, 7.2, 7.4"),
    ("Constraint", "UTM / U-space", "Flight authorizations, restricted areas", "1.3, 5.2, 7.2"),
    ("Constraint", "Climate", "Wind, rain, temperature, humidity", "3.2, 7.5"),
    ("Constraint", "Urban environment", "Obstacles", "4.2, 4.3"),
    ("Constraint", "Other airspace users", "Collision risk, Remote ID", "4.3, 5.4"),
    ("Constraint", "Third parties / local residents", "Noise, fall risk, privacy", "5.5, 7.4, 7.6"),
    ("Input", "Warehouse", "Package (loading, returns)", "2.1, 2.2, 2.7"),
    ("Input", "E-commerce ordering platform", "Delivery order / delivery status", "1.1, 1.4, 2.6"),
    ("Output", "Recipient", "Delivered package (returned package)", "2.5, 2.7"),
    ("Output", "Recipient's smartphone", "Notification, pickup code, proof of delivery", "2.4, 2.6, 5.3"),
    ("Resource", "Charging station", "Electricity", "6.1"),
    ("Resource", "GNSS constellation", "Positioning signal", "4.1"),
    ("Resource", "4G / 5G network", "Data (telemetry, commands)", "5.1, 5.6"),
    ("Resource", "Remote supervision operator", "Mission commands, takeover", "5.1, 7.3"),
    ("Resource", "Maintenance operator", "Maintenance operations, diagnostics", "8.1, 8.2, 8.3, 8.4"),
    ("Resource", "Drop zone / parcel locker", "Landing or drop surface", "2.5, 3.5, 4.5"),
]


def dump(d):
    return dict(key=d.key, w=d.w, h=d.h, dx=d.dx, groups=d.groups, notes=d.notes, nodes=list(d.nodes.values()),
                edges=[dict(e, lp=label_pos(e)) if e["label"] else e for e in d.edges],
                texts=d.texts, legend=d.legend, legend_pos=getattr(d, "legend_pos", None))


GL = {g[0]: TECH_EN[g[1]] for g in GROUPS}
COMP_TRACE = [(COMP_EN[c[0]], GL[c[6]], ", ".join(s[1:] for s in TRACE if c[0] in TRACE[s])) for g in GROUPS for c in COMPONENTS if c[6] == g[0]]
json.dump(dict(palette={k: v.lstrip("#") for k, v in LIGHT.items()}, env=dump(en), fbs=dump(fbs_en),
               tech=dump(tech_en), coverage=COVERAGE, comp_trace=COMP_TRACE), open(os.path.join(os.path.dirname(__file__), "diagrams_en.json"), "w"),
          ensure_ascii=False)
print("json ok")
