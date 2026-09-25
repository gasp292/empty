"""Modèle MBSE du drone de livraison : une seule source pour draw.io, SVG/PNG et la page HTML."""

# ---------------------------------------------------------------- utilitaires
class Diagram:
    def __init__(self, key, title, w, h, dx=0):
        self.key, self.title, self.w, self.h, self.dx = key, title, w, h, dx
        self.groups, self.nodes, self.edges, self.legend, self.notes = [], {}, [], [], []
        self.texts = []  # titres de zones : (x, y, texte)

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
FUNCS = [  # id, nom FR, sous-fonctions FR, nom EN, sous-fonctions EN
    ("F1", "Gérer la mission", ["Recevoir l'ordre\nde livraison", "Planifier la\ntrajectoire",
                                "Obtenir l'autorisation\nde vol", "Suivre et rendre\ncompte de la mission"],
     "Manage the mission", ["Receive the\ndelivery order", "Plan the route", "Obtain flight\nauthorization",
                            "Track and report\nmission status"]),
    ("F2", "Gérer le colis", ["Accueillir et\nverrouiller le colis", "Mesurer la masse\ndu colis",
                              "Maintenir le colis\npendant le vol", "Authentifier\nle destinataire",
                              "Déposer le colis\nau destinataire", "Fournir une preuve\nde livraison",
                              "Gérer les retours et\ncolis non livrés"],
     "Handle the package", ["Accept and lock\nthe package", "Measure the\npackage mass", "Hold the package\nin flight",
                            "Authenticate\nthe recipient", "Deliver the package\nto the recipient",
                            "Provide proof\nof delivery", "Handle returns and\nundelivered packages"]),
    ("F3", "Se déplacer\ndans l'air", ["Générer la poussée", "Contrôler l'attitude", "Décoller",
                                       "Tenir un vol\nstationnaire", "Atterrir", "Supporter les efforts\nmécaniques"],
     "Move through\nthe air", ["Generate thrust", "Control attitude", "Take off", "Hover in place", "Land",
                               "Withstand\nmechanical loads"]),
    ("F4", "Naviguer", ["Se localiser", "Percevoir\nl'environnement", "Détecter et éviter\nobstacles, aéronefs",
                        "Suivre la trajectoire", "Identifier, vérifier\nla zone de dépose"],
     "Navigate", ["Determine\nits position", "Perceive the\nenvironment", "Detect and avoid\nobstacles, aircraft",
                  "Follow the route", "Identify and check\nthe drop zone"]),
    ("F5", "Communiquer", ["Échanger avec\nla supervision", "Échanger avec\nl'U-space (UTM)",
                           "Interagir avec\nle destinataire", "S'identifier\nà distance",
                           "Se rendre visible\net audible", "Sécuriser les\ncommunications"],
     "Communicate", ["Exchange with\nthe telepilot", "Exchange with\nU-space (UTM)", "Interact with\nthe recipient",
                     "Identify itself\nremotely", "Be visible\nand audible", "Secure\ncommunications"]),
    ("F6", "Gérer l'énergie", ["Recevoir l'énergie\nde recharge", "Stocker l'énergie",
                               "Surveiller l'état\nde la batterie", "Distribuer l'énergie"],
     "Manage energy", ["Receive\ncharging energy", "Store energy", "Monitor\nbattery state", "Distribute energy"]),
    ("F7", "Assurer la sécurité", ["Surveiller l'état\ndu système", "Respecter les zones\nde vol (geofencing)",
                                   "Gérer les modes\ndégradés", "Limiter la gravité\nd'une chute",
                                   "Protéger des\nintempéries", "Limiter les nuisances\n(bruit, vie privée)"],
     "Ensure safety", ["Monitor\nsystem health", "Respect flight zones\n(geofencing)", "Manage\ndegraded modes",
                       "Limit the severity\nof a fall", "Withstand\nbad weather", "Limit nuisance\n(noise, privacy)"]),
    ("F8", "Permettre\nla maintenance", ["Enregistrer les\ndonnées de vol", "Diagnostiquer\nles pannes",
                                         "Mettre à jour\nles logiciels", "Permettre l'échange\nde modules"],
     "Enable\nmaintenance", ["Record\nflight data", "Diagnose failures", "Update software", "Allow module\nreplacement"]),
]


def build_fbs(key, title, root, lang):
    n_max = max(len(f[2]) for f in FUNCS)
    d = Diagram(key, title, 1338, 236 + (n_max - 1) * 54 + 45)
    d.node("F0", root, 669, 44, 360, 52, "sys")
    for i, (fid, name_fr, subs_fr, name_en, subs_en) in enumerate(FUNCS):
        name, subs = (name_fr, subs_fr) if lang == "fr" else (name_en, subs_en)
        x0 = 20 + i * 164
        cx = x0 + 75
        d.node(fid, f"{fid}  {name}", cx, 160, 150, 52, "fn")
        d.edge("F0", fid, [(669, 70), (669, 106), (cx, 106), (cx, 134)], cls="tree", arrow=False)
        for j, s in enumerate(subs):
            sid = f"{fid}.{j + 1}"
            cy = 236 + j * 54
            d.node(sid, f"{sid[1:]}  {s}", x0 + 85, cy, 130, 44, "sub")
            d.edge(fid, sid, [(x0 + 9, 186), (x0 + 9, cy), (x0 + 20, cy)], cls="tree", arrow=False)
    return d


fbs = build_fbs("fbs", "Arbre fonctionnel (FBS)", "F0  Livrer un colis par drone\nen milieu urbain", "fr")
fbs_en = build_fbs("fbs_en", "Functional breakdown structure", "Delivery drone", "en")

SUBFUNCS = [(f"{f[0]}.{j + 1}", s.replace("\n", " "), f[0]) for f in FUNCS for j, s in enumerate(f[2])]
SUBFUNCS_EN = [(f"{f[0]}.{j + 1}", s.replace("\n", " "), f[0]) for f in FUNCS for j, s in enumerate(f[4])]
FUNC_NAMES = {f[0]: f[1].replace("\n", " ") for f in FUNCS}

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
    "F2.1": ["bay"], "F2.2": ["mass"], "F2.3": ["bay", "frame"], "F2.4": ["dcam", "mc"],
    "F2.5": ["winch", "dcam"], "F2.6": ["dcam", "mc"], "F2.7": ["bay", "winch", "mc"],
    "F3.1": ["esc", "mot", "prop"], "F3.2": ["fc", "esc"], "F3.3": ["fc", "mot", "prop"],
    "F3.4": ["fc", "gnss", "mot"], "F3.5": ["fc", "us", "gear"], "F3.6": ["frame"],
    "F4.1": ["gnss", "fc"], "F4.2": ["cam", "lidar", "us"], "F4.3": ["mc", "cam", "lidar"],
    "F4.4": ["fc", "mc"], "F4.5": ["dcam", "lidar", "mc"],
    "F5.1": ["modem", "radio"], "F5.2": ["modem", "mc"], "F5.3": ["lights", "modem"], "F5.4": ["rid"],
    "F5.5": ["lights"], "F5.6": ["modem", "mc"],
    "F6.1": ["conn"], "F6.2": ["bat"], "F6.3": ["bms"], "F6.4": ["pdb"],
    "F7.1": ["fc", "mc", "bms"], "F7.2": ["mc", "gnss"], "F7.3": ["fc", "mc"], "F7.4": ["para"],
    "F7.5": ["frame"], "F7.6": ["prop", "mc"],
    "F8.1": ["fc", "mc"], "F8.2": ["mc", "fc"], "F8.3": ["mc", "modem"], "F8.4": ["frame", "bat"],
}
# interaction opérationnelle -> fonctions qui la couvrent
OPS_TRACE = [
    ("Expéditeur", "Colis", "Entrée", ["F2.1", "F2.2", "F2.7"]),
    ("Plateforme de commande", "Ordre de livraison", "Entrée", ["F1.1", "F1.4"]),
    ("Destinataire", "Colis livré", "Sortie", ["F2.5", "F2.7"]),
    ("Smartphone du destinataire", "Notification, code de retrait", "Sortie", ["F2.4", "F2.6", "F5.3"]),
    ("Station de recharge", "Électricité", "Ressource", ["F6.1"]),
    ("Constellation GNSS", "Signal de positionnement", "Ressource", ["F4.1"]),
    ("Réseau 4G / 5G", "Télémétrie, ordres", "Ressource", ["F5.1", "F5.6"]),
    ("Centre de supervision", "Ordres de mission, état du vol", "Ressource", ["F5.1", "F7.3"]),
    ("Opérateur de maintenance", "Maintenance, diagnostic", "Ressource", ["F8.1", "F8.2", "F8.3", "F8.4"]),
    ("Régulateur", "Lois, normes", "Contrainte", ["F5.4", "F7.2", "F7.4"]),
    ("U-space / UTM", "Autorisations, zones géographiques", "Contrainte", ["F1.3", "F5.2", "F7.2"]),
    ("Climat", "Vent, pluie, température", "Contrainte", ["F3.2", "F7.5"]),
    ("Environnement urbain", "Obstacles", "Contrainte", ["F4.2", "F4.3"]),
    ("Tiers / riverains", "Bruit, risque de chute, vie privée", "Contrainte", ["F7.4", "F7.6", "F5.5"]),
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
# ================================================================ 1bis. ENVIRONNEMENT (EN, mise en page du slide 13)
en = Diagram("env_en", "Environment diagram", 1700, 990)
en.node("drone", "Delivery drone\n(system of interest)", 850, 490, 320, 140, "sys")
EN_TOP = [("Regulator\n(EASA, DGAC)", "Laws, standards\n(EU 2019/947, U-space)", "in"),
          ("Drone traffic management\n(UTM / U-space)", "Flight authorizations,\nrestricted areas", "both"),
          ("Climate", "Wind, rain,\ntemperature, humidity", "in"),
          ("Urban environment", "Obstacles (buildings,\ntrees, cables, birds)", "in"),
          ("Other airspace users\n(helicopters, drones)", "Collision risk,\nRemote ID", "both"),
          ("Third parties /\nlocal residents", "Noise, fall risk,\nprivacy", "out")]
EN_BOT = [("Charging station", "Electricity", "in"),
          ("GNSS constellation\n(GPS, Galileo)", "Positioning signal", "in"),
          ("4G / 5G network", "Data (telemetry,\ncommands)", "both"),
          ("Remote supervision\noperator (telepilot)", "Mission commands,\ntakeover", "both"),
          ("Maintenance operator", "Maintenance operations,\ndiagnostics", "both"),
          ("Drop zone /\nparcel locker", "Landing or\ndrop surface", "in")]
for row, items, cls, ny, dy_node, dy_sys in (("t", EN_TOP, "c-con", 120, 148, 420), ("b", EN_BOT, "c-res", 840, 812, 560)):
    for i, (lab, flow, d) in enumerate(items):
        nid, x = f"{row}{i}", 350 + 200 * i
        en.node(nid, lab, x, ny, 180, 56, cls)
        a, b = (x, dy_node), (715 + 54 * i, dy_sys)
        lp = lerp(a, b, 0.35)
        if d == "out":
            en.edge("drone", nid, [b, a], flow, cls, lp=lp)
        else:
            en.edge(nid, "drone", [a, b], flow, cls, both=(d == "both"), lp=lp)
en.node("grid", "Energy grid", 350, 950, 180, 48, "sec")
en.edge("grid", "b0", [(350, 926), (350, 868)], "Electricity", "sec", dash=True)
en.node("wh", "Warehouse\n(warehouse operator)", 420, 430, 190, 56, "c-in")
en.node("plat", "E-commerce\nordering platform", 420, 550, 190, 56, "c-in")
en.node("cust", "Customer", 130, 550, 180, 48, "sec")
en.edge("wh", "drone", [(515, 430), (690, 455)], "Package\n(loading, returns)", "c-in", both=True)
en.edge("plat", "drone", [(515, 550), (690, 525)], "Delivery order /\ndelivery status", "c-in", both=True)
en.edge("cust", "plat", [(220, 550), (325, 550)], "Online\norder", "sec", dash=True)
en.node("rec", "Recipient", 1280, 430, 190, 56, "c-out")
en.node("phone", "Recipient's\nsmartphone", 1280, 550, 190, 56, "c-out")
en.edge("drone", "rec", [(1010, 455), (1185, 430)], "Delivered package\n(returned package)", "c-out", both=True)
en.edge("drone", "phone", [(1010, 525), (1185, 550)], "Notification, pickup\ncode, proof of delivery", "c-out", both=True)
en.edge("rec", "phone", [(1280, 458), (1280, 522)], "Uses", "sec", dash=True, arrow=False)
en.texts = [(850, 44, "CONSTRAINTS"), (420, 375, "STRUCTURING INPUTS"), (1280, 375, "STRUCTURING OUTPUTS"),
            (850, 905, "RESOURCES")]
en.legend = [("c-in", "Structuring inputs"), ("c-out", "Structuring outputs"), ("c-res", "Resources"),
             ("c-con", "Constraints"), ("sec", "Secondary external system")]
en.legend_pos = (930, 965)

DIAGRAMS = [env, fbs, tech, en, fbs_en]

# ================================================================ 3bis. TECHNIQUE (EN, format des slides 20-21)
import copy
TECH_EN = {
    "Système : drone de livraison": "Delivery drone", "PERCEPTION": "Perception", "COMMUNICATION": "Communication",
    "ÉNERGIE": "Energy", "AVIONIQUE": "Avionics", "CHARGE UTILE": "Payload", "PROPULSION": "Propulsion",
    "STRUCTURE": "Structure", "SÉCURITÉ": "Safety",
    "Récepteur GNSS": "GNSS receiver", "Caméras stéréo": "Stereo cameras", "LiDAR": "LiDAR",
    "Capteurs ultrasons": "Ultrasonic sensors", "Modem 4G/5G\n+ antenne": "4G/5G modem\n+ antenna",
    "Radio C2\nde secours": "Backup C2\nradio", "Module\nRemote ID": "Remote ID\nmodule",
    "Connecteur\nde charge": "Charging\nconnector", "BMS\n(gestion batterie)": "BMS (battery\nmanagement)",
    "Batterie Li-ion": "Li-ion battery", "Carte de\ndistribution": "Power distribution\nboard",
    "Contrôleur de vol\nautopilote + firmware\nIMU, baromètre, compas": "Flight controller\nautopilot + firmware\nIMU, barometer, compass",
    "Ordinateur de mission\nOS + logiciels mission,\nnavigation, évitement": "Mission computer\nOS + mission, navigation,\navoidance software",
    "Capteur de masse": "Load cell (mass)", "Compartiment\n+ verrou": "Package bay\n+ lock",
    "Treuil + câble": "Winch + tether", "Caméra de dépose": "Drop-zone camera",
    "Variateurs\n(ESC) ×4": "Speed controllers\n(ESC) ×4", "Moteurs\nbrushless ×4": "Brushless\nmotors ×4",
    "Hélices ×4": "Propellers ×4", "Châssis carbone\n+ bras": "Carbon frame\n+ arms",
    "Train\nd'atterrissage": "Landing gear", "Parachute": "Parachute", "Feux\n+ haut-parleur": "Lights\n+ speaker",
    "Environnement urbain\n(obstacles)": "Urban environment\n(obstacles)", "Constellation GNSS": "GNSS constellation",
    "Réseau 4G/5G": "4G/5G network", "Centre de\nsupervision": "Remote supervision\noperator",
    "Récepteurs Remote ID\n(autorités)": "Remote ID receivers\n(authorities)",
    "Opérateur de\nmaintenance": "Maintenance\noperator", "Station\nde recharge": "Charging\nstation",
    "Expéditeur\n(hub)": "Warehouse", "Destinataire": "Recipient", "Smartphone\ndestinataire": "Recipient's\nsmartphone",
    "Tiers / riverains": "Third parties /\nresidents", "Atmosphère (air)": "Atmosphere (air)",
    "Lumière, échos\n(obstacles)": "Light, echoes\n(obstacles)", "Signal GNSS": "GNSS signal",
    "Télémétrie, ordres": "Telemetry, commands", "Commandes C2": "C2 commands", "Identification": "Identification",
    "Journaux de vol, MAJ": "Flight logs, updates", "Électricité": "Electricity", "Colis": "Package",
    "Colis livré": "Delivered package", "QR code": "Pickup QR code", "Poussée": "Thrust", "Lumière, son": "Light, sound",
    "Position, images,\ndistances": "Position, images,\ndistances", "Mission,\ntélémétrie": "Mission,\ntelemetry",
    "C2 secours": "Backup C2", "Position, ID": "Position, ID", "Consignes,\nétat": "Setpoints,\nstatus",
    "État\nbatterie": "Battery\nstatus", "Consignes\nmoteurs": "Motor\ncommands", "Largage,\nmesures": "Release,\nmeasures",
    "Déclenchement,\nsignalisation": "Trigger,\nsignalling", "Efforts\nmécaniques": "Mechanical\nloads",
}
tech_en = copy.deepcopy(tech)
tech_en.key, tech_en.title = "tech_en", "Technical interaction diagram"
for g in tech_en.groups:
    g["label"] = TECH_EN[g["label"]]
for n in tech_en.nodes.values():
    n["label"] = TECH_EN[n["label"]]
# libellés des liaisons courtes, placés à côté du trait
SHORT = {("conn", "bms"): ("Electricity", (313, 426)), ("bms", "bat"): ("Electricity", (313, 495)),
         ("bat", "pdb"): ("Electricity", (313, 570)), ("pdb", "esc"): ("Power", (380, 598)),
         ("esc", "mot"): ("Power", (562, 598)), ("mot", "prop"): ("Torque", (737, 598)),
         ("bay", "mass"): ("Weight", (1127, 426)), ("bay", "winch"): ("Package", (1130, 495)),
         ("frame", "gear"): ("Loads", (375, 748))}
for e in tech_en.edges:
    if e["label"]:
        e["label"] = TECH_EN[e["label"]]
    elif (e["src"], e["dst"]) in SHORT:
        e["label"], e["lp"] = SHORT[(e["src"], e["dst"])]
tech_en.legend = []
tech_en.notes = [((-60, 905), "Not shown: low-voltage supply of every piece of equipment by the power distribution board.")]
COMP_EN = {c[0]: TECH_EN[c[1]].replace("\n", " ") for c in COMPONENTS}
COMP_EN["fc"], COMP_EN["mc"] = "Flight controller", "Mission computer"
DIAGRAMS.append(tech_en)
