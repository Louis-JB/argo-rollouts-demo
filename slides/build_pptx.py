#!/usr/bin/env python3
"""Génère la présentation PowerPoint (argo-rollouts.pptx) — thème sombre élégant.
Usage: python3 build_pptx.py
Dépendances: python-pptx, Pillow
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from PIL import Image as PILImage

# ---------------------------------------------------------------- palette
BG      = RGBColor(0x14, 0x18, 0x23)   # fond principal (bleu nuit)
BG_SECT = RGBColor(0x0E, 0x11, 0x19)   # fond slides de section
PANEL   = RGBColor(0x1E, 0x25, 0x33)   # cartes
PANEL2  = RGBColor(0x23, 0x2B, 0x3B)
BORDER  = RGBColor(0x32, 0x3C, 0x4F)
ACCENT  = RGBColor(0xEF, 0x76, 0x27)   # orange Argo
BLUE    = RGBColor(0x55, 0xA8, 0xF5)
GREEN   = RGBColor(0x3F, 0xC4, 0x6B)
RED     = RGBColor(0xF0, 0x64, 0x5A)
TEXT    = RGBColor(0xE8, 0xEA, 0xED)
MUTED   = RGBColor(0x97, 0x9F, 0xB0)
WHITE   = RGBColor(0xFF, 0xFF, 0xFF)

FONT = "Calibri"
MONO = "Consolas"

HERE = os.path.dirname(os.path.abspath(__file__))
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]
EW, EH = prs.slide_width, prs.slide_height

_page = 0


# ---------------------------------------------------------------- helpers
def _solid(shape, color):
    shape.fill.solid(); shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    shape.shadow.inherit = False


def _bg(slide, color=BG):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color


def _rect(slide, x, y, w, h, color, line=None, lw=1.0):
    sp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    _solid(sp, color)
    if line is not None:
        sp.line.color.rgb = line; sp.line.width = Pt(lw)
    return sp


def _round(slide, x, y, w, h, color, line=BORDER, lw=1.0, radius=0.08):
    sp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    _solid(sp, color)
    if line is not None:
        sp.line.color.rgb = line; sp.line.width = Pt(lw)
    try:
        sp.adjustments[0] = radius
    except Exception:
        pass
    return sp


def _text(slide, x, y, w, h, runs, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, space=4):
    """runs: list of paragraphs ; chaque paragraphe = list de (texte, size, color, bold, font)."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    for i, para in enumerate(runs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align; p.space_after = Pt(space); p.space_before = Pt(0)
        for (txt, size, color, bold, font) in para:
            r = p.add_run(); r.text = txt
            r.font.size = Pt(size); r.font.color.rgb = color
            r.font.bold = bold; r.font.name = font
    return tb


def R(txt, size=18, color=TEXT, bold=False, font=FONT):
    return (txt, size, color, bold, font)


def _footer(slide, dark=True):
    global _page
    _page += 1
    c = MUTED
    _text(slide, 0.55, 7.06, 8, 0.35, [[R("Argo Rollouts — Projet de recherche Kubernetes & GitOps", 10, c)]])
    _text(slide, 11.0, 7.06, 1.78, 0.35, [[R(f"{_page:02d}", 10, ACCENT, True)]], align=PP_ALIGN.RIGHT)


def header(slide, title, kicker=None):
    """Bandeau de titre épuré : carré orange + titre + filet."""
    _bg(slide, BG)
    _rect(slide, 0.55, 0.62, 0.16, 0.5, ACCENT)            # accent vertical
    runs = []
    if kicker:
        runs.append([R(kicker.upper(), 11, ACCENT, True)])
    runs.append([R(title, 27, WHITE, True)])
    _text(slide, 0.85, 0.5, 11.6, 1.0, runs, anchor=MSO_ANCHOR.MIDDLE, space=2)
    _rect(slide, 0.55, 1.45, 12.23, 0.022, BORDER)         # filet sous le titre
    _footer(slide)
    return slide


def bullet_lines(slide, x, y, w, h, items, size=17, gap=8):
    """items: list de (texte, kind) ; kind: '', 'sub', 'ok', 'ko', 'mut', 'head'."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    first = True
    for txt, kind in items:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.space_after = Pt(gap); p.space_before = Pt(0)
        if kind == 'head':
            r = p.add_run(); r.text = txt
            r.font.size = Pt(size + 1); r.font.bold = True; r.font.color.rgb = ACCENT
            r.font.name = FONT
            continue
        # puce
        bullet, bcol, tcol, tb_ = "▸  ", ACCENT, TEXT, False
        if kind == 'sub':
            bullet, bcol, tcol = "–  ", MUTED, TEXT
            p.level = 1
        elif kind == 'ok':
            bullet, bcol, tcol, tb_ = "✓  ", GREEN, GREEN, True
        elif kind == 'ko':
            bullet, bcol, tcol, tb_ = "✕  ", RED, RED, True
        elif kind == 'mut':
            bullet, bcol, tcol = "▸  ", MUTED, MUTED
        rb = p.add_run(); rb.text = bullet
        rb.font.size = Pt(size); rb.font.bold = True; rb.font.color.rgb = bcol; rb.font.name = FONT
        rt = p.add_run(); rt.text = txt
        rt.font.size = Pt(size); rt.font.bold = tb_; rt.font.color.rgb = tcol; rt.font.name = FONT
    return tb


def code_box(slide, x, y, w, h, lines, size=14, title=None):
    _round(slide, x, y, w, h, PANEL, line=BORDER, radius=0.05)
    if title:
        _text(slide, x + 0.25, y + 0.12, w - 0.5, 0.3, [[R(title, 11, MUTED, True, MONO)]])
        y += 0.38
    tb = slide.shapes.add_textbox(Inches(x + 0.25), Inches(y + 0.08), Inches(w - 0.5), Inches(h - 0.3))
    tf = tb.text_frame; tf.word_wrap = False
    tf.margin_left = 0; tf.margin_top = 0; tf.margin_right = 0; tf.margin_bottom = 0
    for i, (txt, col) in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(2)
        r = p.add_run(); r.text = txt
        r.font.size = Pt(size); r.font.name = MONO; r.font.color.rgb = col
    return tb


def card(slide, x, y, w, h, title, items, accent=ACCENT, size=15):
    _round(slide, x, y, w, h, PANEL, line=BORDER, radius=0.06)
    _rect(slide, x, y + 0.18, 0.10, 0.42, accent)   # petit onglet accent
    _text(slide, x + 0.30, y + 0.20, w - 0.5, 0.45, [[R(title, 16, WHITE, True)]])
    bullet_lines(slide, x + 0.30, y + 0.78, w - 0.55, h - 1.0, items, size=size, gap=6)


def add_pic(slide, rel, x=None, y=2.0, w=None, h=None, max_w=12.2, max_h=4.7, frame=True):
    path = os.path.join(HERE, rel)
    iw, ih = PILImage.open(path).size
    ratio = iw / ih
    if h is None and w is None:
        h = max_h; w = h * ratio
        if w > max_w:
            w = max_w; h = w / ratio
    elif w is None:
        w = h * ratio
    elif h is None:
        h = w / ratio
    if x is None:
        x = (13.333 - w) / 2
    if frame:
        _round(slide, x - 0.06, y - 0.06, w + 0.12, h + 0.12, PANEL, line=BORDER, radius=0.03)
    slide.shapes.add_picture(path, Inches(x), Inches(y), Inches(w), Inches(h))
    return x, y, w, h


# ---------------------------------------------------------------- slides
def title_slide():
    s = prs.slides.add_slide(BLANK); _bg(s, BG_SECT)
    # bande verticale d'accent à gauche
    _rect(s, 0, 0, 0.22, 7.5, ACCENT)
    # "logo" progressive delivery : 3 barres croissantes
    for i, (col, hh) in enumerate([(BORDER, 0.5), (ACCENT, 0.8), (GREEN, 1.1)]):
        _round(s, 0.95 + i * 0.55, 2.0 + (1.1 - hh), 0.42, hh, col, line=None, radius=0.25)
    _text(s, 0.95, 3.35, 11.5, 1.6,
          [[R("Argo Rollouts", 54, WHITE, True)]], anchor=MSO_ANCHOR.TOP)
    _rect(s, 1.0, 4.45, 3.6, 0.06, ACCENT)
    _text(s, 0.95, 4.65, 11.5, 0.8,
          [[R("Déploiement progressif & rollback automatique sur Kubernetes", 22, MUTED)]])
    _text(s, 0.95, 6.5, 11.5, 0.6,
          [[R("Projet de recherche — Écosystème Kubernetes & GitOps", 13, MUTED),
            R("      •      ", 13, BORDER),
            R("Louis — 2026", 13, ACCENT, True)]])
    return s


def section_slide(num, title, subtitle):
    s = prs.slides.add_slide(BLANK); _bg(s, BG_SECT)
    _rect(s, 0, 0, 0.22, 7.5, ACCENT)
    # gros numéro filigrane
    _text(s, 8.3, 0.2, 5.0, 7.2, [[R(num, 300, PANEL, True)]],
          align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
    _text(s, 1.0, 2.7, 9.0, 1.0, [[R(f"PARTIE {num}", 15, ACCENT, True)]])
    _text(s, 1.0, 3.15, 10.5, 1.4, [[R(title, 40, WHITE, True)]])
    _rect(s, 1.05, 4.35, 3.0, 0.05, ACCENT)
    _text(s, 1.0, 4.55, 10.0, 0.8, [[R(subtitle, 18, MUTED)]])
    return s


# ============================================================== CONTENU
title_slide()

# --- Plan
s = prs.slides.add_slide(BLANK); header(s, "Plan de la présentation")
items = [
    ("1", "La technologie", "Le problème, la définition, le fonctionnement"),
    ("2", "Cas d'usage professionnel", "Où, comment, avantages & limites, écosystème"),
    ("3", "Mise en œuvre technique", "Architecture, choix, démonstration live"),
    ("4", "Retour d'expérience", "Bilan, avis personnel, améliorations"),
]
for i, (n, t, d) in enumerate(items):
    y = 1.85 + i * 1.20
    _round(s, 0.85, y, 11.6, 1.02, PANEL, line=BORDER, radius=0.10)
    _round(s, 1.05, y + 0.21, 0.6, 0.6, BG, line=ACCENT, lw=1.5, radius=0.5)
    _text(s, 1.05, y + 0.21, 0.6, 0.6, [[R(n, 22, ACCENT, True)]], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    _text(s, 1.95, y + 0.14, 10.3, 0.5, [[R(t, 19, WHITE, True)]])
    _text(s, 1.95, y + 0.55, 10.3, 0.4, [[R(d, 14, MUTED)]])

# --- Le problème
s = prs.slides.add_slide(BLANK); header(s, "Le problème : le Deployment classique", "Pourquoi aller plus loin")
_text(s, 0.85, 1.65, 11.6, 0.8,
      [[R("Un ", 18, TEXT), R("Deployment", 18, ACCENT, True),
        R(" fait un ", 18, TEXT), R("rolling update", 18, WHITE, True),
        R(" : il remplace les pods un à un… sans jamais vérifier si la nouvelle version fonctionne.", 18, TEXT)]])
card(s, 0.85, 2.65, 5.75, 3.7, "Les risques", [
    ("Une v2 buggée part vers 100 % des utilisateurs", 'ko'),
    ("Détection tardive : alertes, support, churn", 'ko'),
    ("Rollback manuel, sous stress, en plein incident", 'ko'),
    ("Aucune mesure objective avant de généraliser", 'ko'),
], accent=RED)
card(s, 6.85, 2.65, 5.6, 3.7, "Le besoin", [
    ("Exposer la v2 à une fraction du trafic d'abord", ''),
    ("Mesurer sa santé en conditions réelles", ''),
    ("Promouvoir seulement si les métriques sont bonnes", ''),
    ("Revenir en arrière automatiquement sinon", ''),
], accent=GREEN)

# --- Qu'est-ce qu'Argo Rollouts
s = prs.slides.add_slide(BLANK); header(s, "Qu'est-ce qu'Argo Rollouts ?", "Définition")
_text(s, 0.85, 1.65, 11.6, 0.9,
      [[R("Un ", 18, TEXT), R("contrôleur Kubernetes", 18, WHITE, True),
        R(" (projet CNCF, famille Argo) qui remplace le Deployment par une ressource ", 18, TEXT),
        R("Rollout", 18, ACCENT, True), R(" offrant la progressive delivery.", 18, TEXT)]])
card(s, 0.85, 2.7, 3.75, 3.5, "Canary", [
    ("% croissant du trafic vers la v2", ''),
    ("20% → 40% → 60% → 100%", 'mut'),
], accent=ACCENT, size=15)
card(s, 4.78, 2.7, 3.75, 3.5, "Blue-Green", [
    ("Deux environnements isolés", ''),
    ("Bascule instantanée", 'mut'),
], accent=BLUE, size=15)
card(s, 8.7, 2.7, 3.75, 3.5, "Analyse auto", [
    ("Décision pilotée par métriques", ''),
    ("Promotion ou rollback", 'mut'),
], accent=GREEN, size=15)
_text(s, 0.85, 6.35, 11.6, 0.5,
      [[R("→ Objectif : une mise en production ", 16, TEXT),
        R("graduelle, mesurée et réversible automatiquement.", 16, ACCENT, True)]])

# --- Fonctionnement
s = prs.slides.add_slide(BLANK); header(s, "Fonctionnement global", "Architecture interne")
code_box(s, 0.85, 1.75, 6.0, 2.5, [
    ("Rollout  (remplace Deployment)", WHITE),
    ("   │", MUTED),
    ("   ├─ ReplicaSet STABLE   v actuelle", GREEN),
    ("   ├─ ReplicaSet CANARY   v nouvelle", ACCENT),
    ("   └─ AnalysisRun         décide", BLUE),
], size=15, title="ressources gérées")
card(s, 7.1, 1.75, 5.35, 4.6, "À chaque palier, le contrôleur", [
    ("Ajuste la proportion de trafic/pods canary", ''),
    ("Marque une pause (minutée ou manuelle)", ''),
    ("Lance une analyse de la santé du canary", ''),
    ("Promeut si OK", 'ok'),
    ("Rollback automatique si KO", 'ko'),
])
code_box(s, 0.85, 4.45, 6.0, 1.9, [
    ("steps:", WHITE),
    ("  - setWeight: 20", TEXT),
    ("  - pause: { duration: 30s }", TEXT),
    ("  - analysis: { success-rate }", ACCENT),
], size=14, title="exemple de stratégie")

# --- Usage entreprise + écosystème
s = prs.slides.add_slide(BLANK); header(s, "Cas d'usage en entreprise & écosystème", "Adoption")
card(s, 0.85, 1.75, 5.75, 4.6, "Utilisation en production", [
    ("Réduire le risque : tester la v2 sur 5–10 % du trafic", ''),
    ("Déployer plusieurs fois/jour sans maintenance", ''),
    ("SLO-driven : promotion liée aux métriques", ''),
    ("latence, taux d'erreur, succès (Prometheus, Datadog…)", 'sub'),
    ("Couplé au GitOps (ArgoCD / Flux)", ''),
])
card(s, 6.85, 1.75, 5.6, 4.6, "Écosystème", [
    ("Projet CNCF (Argoproj), combo standard avec ArgoCD", ''),
    ("Voisins : Flagger (Flux), Spinnaker", ''),
    ("Analyse native : Prometheus, Datadog, New Relic,", ''),
    ("CloudWatch, Graphite, Job / Web custom", 'sub'),
    ("Contextes : microservices, API critiques, e-commerce, SaaS", ''),
], accent=BLUE)

# --- Avantages / limites
s = prs.slides.add_slide(BLANK); header(s, "Avantages & limites", "Analyse critique")
card(s, 0.85, 1.75, 5.75, 4.6, "Avantages", [
    ("Rollback automatique → moins d'incidents", 'ok'),
    ("Pas de downtime, exposition contrôlée", 'ok'),
    ("Décision objective (métriques), pas « au feeling »", 'ok'),
    ("Intégration native : ArgoCD, Prometheus, Istio", 'ok'),
], accent=GREEN)
card(s, 6.85, 1.75, 5.6, 4.6, "Limites", [
    ("Complexité accrue (CRD, analyse, parfois mesh)", 'ko'),
    ("Trafic fin = Istio / NGINX / SMI requis", 'ko'),
    ("Nécessite de bonnes métriques (sinon fausse confiance)", 'ko'),
    ("Courbe d'apprentissage, observabilité indispensable", 'ko'),
], accent=RED)

# --- Architecture démo
s = prs.slides.add_slide(BLANK); header(s, "Architecture de la démo", "Stack & flux")
code_box(s, 0.85, 1.75, 11.6, 2.15, [
    ("git push ─▶ GitHub Actions (lint + validation des manifests)", TEXT),
    ("        └─▶ ArgoCD (pull) ─▶ Rollout ─▶ Contrôleur Argo Rollouts", ACCENT),
    ("                                          ├─ ReplicaSet stable / canary", GREEN),
    ("                                          └─ AnalysisRun (Job de sonde HTTP)", BLUE),
], size=15, title="flux GitOps de bout en bout")
card(s, 0.85, 4.15, 5.7, 2.55, "Environnement & astuce", [
    ("Cluster kind + ArgoCD + Argo Rollouts v1.7.2", ''),
    ("App rollouts-demo : 1 couleur = 1 version", ''),
    ("Le tag bad-red renvoie des HTTP 500", 'ko'),
    ("version « buggée » déterministe pour le rollback", 'sub'),
], size=14)
add_pic(s, "img/ui-app.png", x=6.95, y=4.15, max_w=5.5, max_h=2.35)
_text(s, 6.95, 6.52, 5.5, 0.3, [[R("Capture réelle de l'UI de l'app de démo", 11, MUTED)]])

# --- Choix techniques
s = prs.slides.add_slide(BLANK); header(s, "Choix techniques clés", "Décisions d'implémentation")
card(s, 0.85, 1.75, 11.6, 4.6, "4 décisions structurantes", [
    ("Canary sans service mesh → split par nombre de pods (simple, portable)", ''),
    ("Services stable + canary : le contrôleur y injecte le pod-template-hash", ''),
    ("la sonde cible ainsi précisément les pods canary", 'sub'),
    ("Probes TCP (et non HTTP /color) : les pods bad-red restent Ready malgré les 500", ''),
    ("on démontre un rollback piloté par l'ANALYSE, pas par la santé", 'sub'),
    ("AnalysisTemplate de type Job : sonde 30 requêtes, exige ≥ 95 % de succès", ''),
    ("autonome ; variante Prometheus fournie pour la production", 'sub'),
], size=16)

# --- Démo 1
s = prs.slides.add_slide(BLANK); header(s, "Démo 1 — Canary sain", "Promotion automatique")
card(s, 0.85, 1.75, 3.55, 4.6, "Scénario", [
    ("Déploiement de la version green", ''),
    ("Canary 20% → 40%", 'mut'),
    ("AnalysisRun sonde le canary", ''),
    ("30/30 = 100 % (seuil 95%)", 'ok'),
    ("Promotion auto à 100 %", 'ok'),
], accent=GREEN, size=14)
add_pic(s, "img/demo-canary-inprogress.png", x=4.65, y=1.75, max_w=7.9, max_h=4.7)

# --- Démo 2
s = prs.slides.add_slide(BLANK); header(s, "Démo 2 — Canary défaillant", "Rollback automatique")
card(s, 0.85, 1.75, 3.55, 4.6, "Scénario", [
    ("Déploiement de bad-red", ''),
    ("Réponses HTTP 500", 'ko'),
    ("Sonde : 5/30 = 16 %", 'ko'),
    ("Metric Failed → RolloutAborted", 'ko'),
    ("Trafic gardé sur green, 0 downtime", 'ok'),
], accent=RED, size=14)
add_pic(s, "img/demo-rollback.png", x=4.65, y=1.95, max_w=7.9, max_h=4.3)

# --- REX
s = prs.slides.add_slide(BLANK); header(s, "Bilan, avis & améliorations", "Conclusion")
card(s, 0.85, 1.75, 5.75, 2.95, "Ce que j'ai appris", [
    ("Le progressive delivery en pratique", ''),
    ("L'imbrication GitOps ↔ Rollouts", ''),
    ("Les métriques comme contrat de qualité", ''),
], accent=BLUE, size=14)
card(s, 6.85, 1.75, 5.6, 2.95, "Mon avis", [
    ("Excellent compromis sécurité / vélocité", 'ok'),
    ("Pour des services critiques à fort trafic", 'mut'),
    ("Overkill pour un petit mono-service", 'ko'),
], size=14)
card(s, 0.85, 4.9, 11.6, 1.55, "Améliorations possibles", [
    ("Trafic fin via Istio/NGINX · analyse Prometheus réelle (p95 + erreurs) · "
     "notifications Slack · Blue-Green avec tests preview · multi-cluster ApplicationSet", 'mut'),
], accent=ACCENT, size=14)

# --- Merci
s = prs.slides.add_slide(BLANK); _bg(s, BG_SECT)
_rect(s, 0, 0, 0.22, 7.5, ACCENT)
_text(s, 0.95, 2.5, 11.5, 1.2, [[R("Merci de votre attention", 44, WHITE, True)]])
_rect(s, 1.0, 3.7, 3.0, 0.05, ACCENT)
_text(s, 0.95, 3.95, 11.5, 0.6, [[R("Questions ?", 22, MUTED)]])
code_box(s, 0.95, 4.9, 8.2, 1.0,
         [("kubectl argo rollouts get rollout rollouts-demo --watch", GREEN)], size=15)
_text(s, 0.95, 6.2, 11.5, 0.5,
      [[R("github.com/Louis-JB/argo-rollouts-demo", 14, BLUE, True)]])


# ---------------------------------------------------------------- save
out = os.path.join(HERE, "argo-rollouts.pptx")
prs.save(out)
n = len(prs.slides._sldIdLst)
print(f"OK -> {out}  ({n} slides)")
