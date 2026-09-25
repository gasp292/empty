"""Modèle MBSE du drone de livraison : une seule source pour draw.io, SVG/PNG et la page HTML."""

# ---------------------------------------------------------------- utilitaires
class Diagram:
    def __init__(self, key, title, w, h, dx=0):
        self.key, self.title, self.w, self.h, self.dx = key, title, w, h, dx
        self.groups, self.nodes, self.edges, self.legend, self.notes = [], {}, [], [], []

    def group(self, gid, label, x0, y0, x1, y1, cls="grp", lx=None):
        self.groups.append(dict(id=gid, label=label, x0=x0, y0=y0, x1=x1, y1=y1, cls=cls,
                                lx=x0 + 10 if lx is None else lx))

    def node(self, nid, label, cx, cy, w=150, h=44, cls="cmp"):
        self.nodes[nid] = dict(id=nid, label=label, cx=cx, cy=cy, w=w, h=h, cls=cls)

    def edge(self, src, dst, pts, label="", cls="", both=False, lp=None, arrow=True, dash=False):
        self.edges.append(dict(src=src, dst=dst, pts=pts, label=label, cls=cls,
                               both=both, lp=lp, arrow=arrow, dash=dash))


def lerp(a, b, t):
    return (round(a[0] + (b[0] - a[0]) * t), round(a[1] + (b[1] - a[1]) * t))


# ================================================================ 1. ENVIRONNEMENT
env = Diagram("env", "Diagramme d'environnement", 1240, 800)
env.node("drone", "Drone de livraison\nurbaine", 620, 420, 250, 100, "sys")

TOP = [("res1", "Station de recharge\n(base drone)", 200, "Électricité", False),
       ("res2", "Constellation GNSS\n(GPS, Galileo)", 410, "Signal de\npositionnement", False),
       ("res3", "Réseau mobile\n4G / 5G", 620, "Données\n(télémétrie, ordres)", True),
       ("res4", "Centre de supervision\n(télépilote)", 830, "Ordres de mission,\nétat du vol", True),
       ("res5", "Opérateur\nde maintenance", 1040, "Maintenance,\ndiagnostic", True)]
BOT = [("con1", "Régulateur\n(EASA, DGAC)", 200, "Lois, normes\n(règl. UE 2019/947)", "in"),
       ("con2", "U-space / UTM\n(gestion du trafic)", 410, "Autorisations de vol,\nzones géographiques", "both"),
       ("con3", "Climat\n(météo)", 620, "Vent, pluie,\ntempérature", "in"),
       ("con4", "Environnement urbain\n(bâti, obstacles)", 830, "Obstacles (bâti,\ncâbles, oiseaux)", "in"),
       ("con5", "Tiers / riverains\n(public au sol)", 1040, "Bruit, risque\nde chute, vie privée", "out")]
for i, (nid, lab, x, flow, both) in enumerate(TOP):
    env.node(nid, lab, x, 150, 180, 56, "c-res")
    a, b = (540 + 40 * i, 370), (x, 178)
    env.edge(nid, "drone", [b, a], flow, "c-res", both=both, lp=lerp(a, b, 0.62))
for i, (nid, lab, x, flow, d) in enumerate(BOT):
    env.node(nid, lab, x, 690, 180, 56, "c-con")
    a, b = (540 + 40 * i, 470), (x, 662)
    pts = [a, b] if d == "out" else [b, a]
    env.edge(nid if d != "out" else "drone", "drone" if d != "out" else nid, pts, flow, "c-con",
             both=(d == "both"), lp=lerp(a, b, 0.62))
env.node("in1", "Expéditeur\n(hub logistique)", 110, 360, 180, 56, "c-in")
env.node("in2", "Plateforme\nde commande", 110, 480, 180, 56, "c-in")
env.node("out1", "Destinataire", 1130, 360, 180, 56, "c-out")
env.node("out2", "Smartphone\ndu destinataire", 1130, 480, 180, 56, "c-out")
env.edge("in1", "drone", [(200, 360), (495, 395)], "Colis", "c-in")
env.edge("in2", "drone", [(200, 480), (495, 445)], "Ordre de livraison", "c-in")
env.edge("drone", "out1", [(745, 395), (1040, 360)], "Colis livré", "c-out")
env.edge("drone", "out2", [(745, 445), (1040, 480)], "Notification,\ncode de retrait", "c-out", both=True)
env.node("sec1", "Réseau électrique", 200, 45, 180, 48, "sec")
env.edge("sec1", "res1", [(200, 69), (200, 122)], "Électricité", "sec", dash=True)
env.edge("out1", "out2", [(1130, 388), (1130, 452)], "Utilise", "sec", dash=True, arrow=False)
env.legend = [("c-in", "Entrées structurantes"), ("c-out", "Sorties structurantes"),
              ("c-res", "Ressources"), ("c-con", "Contraintes"), ("sec", "Système externe secondaire")]
env.legend_pos = (20, 770)

# ================================================================ 2. FONCTIONNEL (FBS)
FUNCS = [
    ("F1", "Gérer la mission", ["Recevoir l'ordre\nde livraison", "Planifier la\ntrajectoire",
                                "Obtenir l'autorisation\nde vol", "Suivre et rendre\ncompte de la mission"]),
    ("F2", "Gérer le colis", ["Accueillir et\nverrouiller le colis", "Mesurer la masse\ndu colis",
                              "Maintenir le colis\npendant le vol", "Déposer le colis\nau destinataire"]),
    ("F3", "Se déplacer\ndans l'air", ["Générer la poussée", "Contrôler l'attitude", "Décoller",
                                       "Atterrir", "Supporter les efforts\nmécaniques"]),
    ("F4", "Naviguer", ["Se localiser", "Percevoir\nl'environnement", "Détecter et éviter\nles obstacles",
                        "Suivre la trajectoire"]),
    ("F5", "Communiquer", ["Échanger avec\nla supervision", "Échanger avec\nl'U-space (UTM)",
                           "Interagir avec\nle destinataire", "S'identifier\nà distance",
                           "Se rendre visible\net audible"]),
    ("F6", "Gérer l'énergie", ["Recevoir l'énergie\nde recharge", "Stocker l'énergie",
                               "Surveiller l'état\nde la batterie", "Distribuer l'énergie"]),
    ("F7", "Assurer la sécurité", ["Surveiller l'état\ndu système", "Respecter les zones\nde vol (geofencing)",
                                   "Gérer les modes\ndégradés", "Limiter la gravité\nd'une chute",
                                   "Protéger des\nintempéries"]),
    ("F8", "Permettre\nla maintenance", ["Enregistrer les\ndonnées de vol", "Diagnostiquer\nles pannes",
                                         "Mettre à jour\nles logiciels", "Permettre l'échange\nde modules"]),
]
fbs = Diagram("fbs", "Arbre fonctionnel (FBS)", 1338, 500)
fbs.node("F0", "F0  Livrer un colis par drone\nen milieu urbain", 669, 44, 360, 52, "sys")
for i, (fid, name, subs) in enumerate(FUNCS):
    x0 = 20 + i * 164
    cx = x0 + 75
    fbs.node(fid, f"{fid}  {name}", cx, 160, 150, 52, "fn")
    fbs.edge("F0", fid, [(669, 70), (669, 106), (cx, 106), (cx, 134)], cls="tree", arrow=False)
    for j, s in enumerate(subs):
        sid = f"{fid}.{j + 1}"
        cy = 236 + j * 54
        fbs.node(sid, f"{sid[1:]}  {s}", x0 + 85, cy, 130, 44, "sub")
        fbs.edge(fid, sid, [(x0 + 9, 186), (x0 + 9, cy), (x0 + 20, cy)], cls="tree", arrow=False)

SUBFUNCS = [(f"{fid}.{j + 1}", s.replace("\n", " "), fid)
            for fid, _, subs in FUNCS for j, s in enumerate(subs)]
FUNC_NAMES = {fid: n.replace("\n", " ") for fid, n, _ in FUNCS}

# ================================================================ 3. TECHNIQUE
tech = Diagram("tech", "Diagramme d'interactions techniques", 1505, 925, dx=80)
T = tech
T.group("bnd", "Système : drone de livraison", 170, 100, 1230, 825, "bnd")
GROUPS = [("g-per", "PERCEPTION", 190, 135, 560, 290), ("g-com", "COMMUNICATION", 600, 135, 1210, 230),
          ("g-nrg", "ÉNERGIE", 190, 340, 360, 650), ("g-avi", "AVIONIQUE", 400, 340, 920, 500),
          ("g-pay", "CHARGE UTILE", 980, 340, 1210, 650), ("g-pro", "PROPULSION", 400, 555, 900, 650),
          ("g-str", "STRUCTURE", 190, 700, 560, 800), ("g-saf", "SÉCURITÉ", 900, 700, 1210, 800)]
LABEL_X = {"g-avi": 560, "g-pro": 560, "g-com": 905}  # libellés décalés pour ne pas croiser un flux
for g in GROUPS:
    T.group(*g, lx=LABEL_X.get(g[0]))
COMPONENTS = [  # id, libellé, cx, cy, w, h, sous-système
    ("gnss", "Récepteur GNSS", 285, 185, 150, 44, "g-per"),
    ("cam", "Caméras stéréo", 465, 185, 150, 44, "g-per"),
    ("lidar", "LiDAR", 285, 250, 150, 44, "g-per"),
    ("us", "Capteurs ultrasons", 465, 250, 150, 44, "g-per"),
    ("modem", "Modem 4G/5G\n+ antenne", 690, 185, 150, 44, "g-com"),
    ("radio", "Radio C2\nde secours", 870, 185, 150, 44, "g-com"),
    ("rid", "Module\nRemote ID", 1050, 185, 150, 44, "g-com"),
    ("conn", "Connecteur\nde charge", 275, 392, 150, 44, "g-nrg"),
    ("bms", "BMS\n(gestion batterie)", 275, 460, 150, 44, "g-nrg"),
    ("bat", "Batterie Li-ion", 275, 530, 150, 44, "g-nrg"),
    ("pdb", "Carte de\ndistribution", 275, 610, 150, 44, "g-nrg"),
    ("fc", "Contrôleur de vol\nautopilote + firmware\nIMU, baromètre, compas", 525, 430, 200, 70, "g-avi"),
    ("mc", "Ordinateur de mission\nOS + logiciels mission,\nnavigation, évitement", 795, 430, 200, 70, "g-avi"),
    ("mass", "Capteur de masse", 1095, 392, 170, 44, "g-pay"),
    ("bay", "Compartiment\n+ verrou", 1095, 460, 170, 44, "g-pay"),
    ("winch", "Treuil + câble", 1095, 530, 170, 44, "g-pay"),
    ("dcam", "Caméra de dépose", 1095, 610, 170, 44, "g-pay"),
    ("esc", "Variateurs\n(ESC) ×4", 475, 610, 130, 44, "g-pro"),
    ("mot", "Moteurs\nbrushless ×4", 650, 610, 130, 44, "g-pro"),
    ("prop", "Hélices ×4", 825, 610, 130, 44, "g-pro"),
    ("frame", "Châssis carbone\n+ bras", 285, 760, 150, 44, "g-str"),
    ("gear", "Train\nd'atterrissage", 465, 760, 150, 44, "g-str"),
    ("para", "Parachute", 985, 760, 140, 44, "g-saf"),
    ("lights", "Feux\n+ haut-parleur", 1135, 760, 140, 44, "g-saf"),
]
for cid, lab, cx, cy, w, h, _ in COMPONENTS:
    T.node(cid, lab, cx, cy, w, h, "cmp")
EXTERNALS = [
    ("x-env", "Environnement urbain\n(obstacles)", 100, 40), ("x-gnss", "Constellation GNSS", 285, 40),
    ("x-net", "Réseau 4G/5G", 690, 40), ("x-sup", "Centre de\nsupervision", 870, 40),
    ("x-rx", "Récepteurs Remote ID\n(autorités)", 1050, 40),
    ("x-maint", "Opérateur de\nmaintenance", 10, 310), ("x-sta", "Station\nde recharge", 10, 392),
    ("x-exp", "Expéditeur\n(hub)", 1335, 460), ("x-dest", "Destinataire", 1335, 530),
    ("x-phone", "Smartphone\ndestinataire", 1335, 610), ("x-tiers", "Tiers / riverains", 1335, 880),
    ("x-air", "Atmosphère (air)", 825, 880),
]
for xid, lab, cx, cy in EXTERNALS:
    T.node(xid, lab, cx, cy, 150, 48, "ext")

E = T.edge
# flux avec l'environnement
E("x-env", "lidar", [(100, 64), (100, 250), (210, 250)], "Lumière, échos\n(obstacles)", "f-rf", lp=(100, 157))
E("x-gnss", "gnss", [(285, 64), (285, 163)], "Signal GNSS", "f-rf", lp=(285, 82))
E("x-net", "modem", [(690, 64), (690, 163)], "Télémétrie, ordres", "f-data", both=True, lp=(690, 82))
E("x-sup", "radio", [(870, 64), (870, 163)], "Commandes C2", "f-data", both=True, lp=(870, 82))
E("rid", "x-rx", [(1050, 163), (1050, 64)], "Identification", "f-rf", lp=(1050, 82))
E("x-maint", "fc", [(85, 310), (440, 310), (440, 395)], "Journaux de vol, MAJ", "f-data", both=True, lp=(262, 310))
E("x-sta", "conn", [(85, 392), (200, 392)], "Électricité", "f-elec")
E("x-exp", "bay", [(1260, 460), (1180, 460)], "Colis", "f-mech")
E("winch", "x-dest", [(1180, 530), (1260, 530)], "Colis livré", "f-mech")
E("x-phone", "dcam", [(1260, 610), (1180, 610)], "QR code", "f-rf")
E("prop", "x-air", [(825, 632), (825, 856)], "Poussée", "f-mech", lp=(825, 745))
E("lights", "x-tiers", [(1135, 782), (1135, 880), (1260, 880)], "Lumière, son", "f-rf", lp=(1197, 880))
# flux internes
E("g-per", "mc", [(540, 290), (540, 325), (710, 325), (710, 395)], "Position, images,\ndistances", "f-data", lp=(625, 325))
E("modem", "mc", [(755, 207), (755, 395)], "Mission,\ntélémétrie", "f-data", both=True, lp=(755, 290))
E("radio", "mc", [(870, 207), (870, 395)], "C2 secours", "f-data", both=True, lp=(870, 290))
E("mc", "rid", [(895, 410), (945, 410), (945, 315), (1050, 315), (1050, 207)], "Position, ID", "f-data", lp=(998, 315))
E("fc", "mc", [(625, 430), (695, 430)], "Consignes,\nétat", "f-data", both=True)
E("bms", "fc", [(350, 455), (425, 455)], "État\nbatterie", "f-data")
E("fc", "esc", [(475, 465), (475, 588)], "Consignes\nmoteurs", "f-data", lp=(475, 527))
E("mc", "g-pay", [(895, 455), (980, 455)], "Largage,\nmesures", "f-data", both=True, lp=(940, 455))
E("mc", "g-saf", [(870, 465), (870, 527), (955, 527), (955, 700)], "Déclenchement,\nsignalisation", "f-data", lp=(955, 612))
E("conn", "bms", [(275, 414), (275, 438)], "", "f-elec")
E("bms", "bat", [(275, 482), (275, 508)], "", "f-elec", both=True)
E("bat", "pdb", [(275, 552), (275, 588)], "", "f-elec")
E("pdb", "esc", [(350, 610), (410, 610)], "", "f-elec")
E("esc", "mot", [(540, 610), (585, 610)], "", "f-elec")
E("mot", "prop", [(715, 610), (760, 610)], "", "f-mech")
E("mot", "g-str", [(650, 632), (650, 760), (560, 760)], "Efforts\nmécaniques", "f-mech", lp=(650, 690))
E("frame", "gear", [(360, 760), (390, 760)], "", "f-mech")
E("bay", "mass", [(1095, 438), (1095, 414)], "", "f-mech")
E("bay", "winch", [(1095, 482), (1095, 508)], "", "f-mech")
T.legend = [("f-elec", "Électricité"), ("f-data", "Données / signaux"),
            ("f-mech", "Mécanique / matière"), ("f-rf", "Ondes (lumière, son, radio)")]
T.legend_pos = (-60, 872)
T.notes = [((-60, 905), "Non représenté : alimentation basse tension de tous les équipements par la carte de distribution.")]

COMP_LABEL = {c[0]: c[1].split("\n")[0] if c[0] in ("fc", "mc") else c[1].replace("\n", " ")
              for c in COMPONENTS}
COMP_GROUP = {c[0]: c[6] for c in COMPONENTS}
GROUP_LABEL = {g[0]: g[1] for g in GROUPS}

# ================================================================ 4. TRAÇABILITÉ
# fonction -> composants qui la réalisent
TRACE = {
    "F1.1": ["modem", "mc"], "F1.2": ["mc"], "F1.3": ["mc", "modem"], "F1.4": ["mc", "modem"],
    "F2.1": ["bay"], "F2.2": ["mass"], "F2.3": ["bay", "frame"], "F2.4": ["winch", "dcam"],
    "F3.1": ["esc", "mot", "prop"], "F3.2": ["fc", "esc"], "F3.3": ["fc", "mot", "prop"],
    "F3.4": ["fc", "us", "gear"], "F3.5": ["frame"],
    "F4.1": ["gnss", "fc"], "F4.2": ["cam", "lidar", "us"], "F4.3": ["mc", "cam", "lidar"],
    "F4.4": ["fc", "mc"],
    "F5.1": ["modem", "radio"], "F5.2": ["modem", "mc"], "F5.3": ["dcam", "lights"], "F5.4": ["rid"],
    "F5.5": ["lights"],
    "F6.1": ["conn"], "F6.2": ["bat"], "F6.3": ["bms"], "F6.4": ["pdb"],
    "F7.1": ["fc", "mc", "bms"], "F7.2": ["mc", "gnss"], "F7.3": ["fc", "mc"], "F7.4": ["para"],
    "F7.5": ["frame"],
    "F8.1": ["fc", "mc"], "F8.2": ["mc", "fc"], "F8.3": ["mc", "modem"], "F8.4": ["frame", "bat"],
}
# interaction opérationnelle -> fonctions qui la couvrent
OPS_TRACE = [
    ("Expéditeur", "Colis", "Entrée", ["F2.1", "F2.2"]),
    ("Plateforme de commande", "Ordre de livraison", "Entrée", ["F1.1"]),
    ("Destinataire", "Colis livré", "Sortie", ["F2.4"]),
    ("Smartphone du destinataire", "Notification, code de retrait", "Sortie", ["F5.3"]),
    ("Station de recharge", "Électricité", "Ressource", ["F6.1"]),
    ("Constellation GNSS", "Signal de positionnement", "Ressource", ["F4.1"]),
    ("Réseau 4G / 5G", "Télémétrie, ordres", "Ressource", ["F5.1", "F1.4"]),
    ("Centre de supervision", "Ordres de mission, état du vol", "Ressource", ["F5.1", "F7.3"]),
    ("Opérateur de maintenance", "Maintenance, diagnostic", "Ressource", ["F8.1", "F8.2", "F8.3", "F8.4"]),
    ("Régulateur", "Lois, normes", "Contrainte", ["F5.4", "F7.2", "F7.4"]),
    ("U-space / UTM", "Autorisations, zones géographiques", "Contrainte", ["F1.3", "F5.2", "F7.2"]),
    ("Climat", "Vent, pluie, température", "Contrainte", ["F3.2", "F7.5"]),
    ("Environnement urbain", "Obstacles", "Contrainte", ["F4.2", "F4.3"]),
    ("Tiers / riverains", "Bruit, risque de chute, vie privée", "Contrainte", ["F7.4", "F5.5", "F3.1"]),
]
USE_CASES = [
    ("UC1", "Livrer un colis", "Utilisation nominale : chargement au hub, vol, dépose au treuil, retour."),
    ("UC2", "Annuler ou dérouter une mission", "Destinataire absent, zone de dépose occupée, ordre du télépilote."),
    ("UC3", "Gérer une situation d'urgence", "Perte de liaison, panne moteur, batterie faible : retour base, atterrissage d'urgence ou parachute."),
    ("UC4", "Recharger le drone", "Entre deux missions, sur la station de la base."),
    ("UC5", "Maintenir le drone", "Inspection, diagnostic, mise à jour logicielle, remplacement de modules."),
    ("UC6", "Faire certifier et autoriser le système", "Dossier auprès du régulateur, enregistrement U-space."),
]

# contrôles de cohérence
assert set(TRACE) == {s[0] for s in SUBFUNCS}, "fonction non tracée"
assert {c for cs in TRACE.values() for c in cs} == set(COMP_GROUP), "composant non tracé"
assert {f for *_, fs in OPS_TRACE for f in fs} <= set(TRACE)
DIAGRAMS = [env, fbs, tech]
