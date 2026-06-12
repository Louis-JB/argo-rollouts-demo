#!/usr/bin/env python3
"""Génère la présentation PowerPoint (argo-rollouts.pptx) à partir d'un contenu structuré.
Usage: python3 build_pptx.py
Dépendance: python-pptx  (pip install --user python-pptx)
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# Palette
ARGO = RGBColor(0xEF, 0x76, 0x27)      # orange Argo
DARK = RGBColor(0x1B, 0x1F, 0x2A)
GREY = RGBColor(0x55, 0x5A, 0x66)
GREEN = RGBColor(0x2E, 0xA0, 0x43)
RED = RGBColor(0xC0, 0x39, 0x2B)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]

W, H = prs.slide_width, prs.slide_height


def _tf(box):
    tf = box.text_frame
    tf.word_wrap = True
    return tf


def section(title, subtitle=""):
    s = prs.slides.add_slide(BLANK)
    bg = s.background.fill
    bg.solid()
    bg.fore_color.rgb = DARK
    bar = s.shapes.add_shape(1, Inches(0), Inches(3.0), Inches(0.25), Inches(1.5))
    bar.fill.solid(); bar.fill.fore_color.rgb = ARGO; bar.line.fill.background()
    box = s.shapes.add_textbox(Inches(0.8), Inches(2.9), Inches(11.7), Inches(1.8))
    tf = _tf(box)
    p = tf.paragraphs[0]; p.text = title
    p.font.size = Pt(40); p.font.bold = True; p.font.color.rgb = WHITE
    if subtitle:
        sp = tf.add_paragraph(); sp.text = subtitle
        sp.font.size = Pt(20); sp.font.color.rgb = ARGO
    return s


def title_slide(title, subtitle, footer):
    s = prs.slides.add_slide(BLANK)
    bg = s.background.fill; bg.solid(); bg.fore_color.rgb = DARK
    bar = s.shapes.add_shape(1, Inches(0.8), Inches(2.4), Inches(4.2), Inches(0.18))
    bar.fill.solid(); bar.fill.fore_color.rgb = ARGO; bar.line.fill.background()
    box = s.shapes.add_textbox(Inches(0.8), Inches(2.6), Inches(11.7), Inches(2.5))
    tf = _tf(box)
    p = tf.paragraphs[0]; p.text = title
    p.font.size = Pt(48); p.font.bold = True; p.font.color.rgb = WHITE
    sp = tf.add_paragraph(); sp.text = subtitle
    sp.font.size = Pt(24); sp.font.color.rgb = ARGO
    fb = s.shapes.add_textbox(Inches(0.8), Inches(6.4), Inches(11.7), Inches(0.8))
    fp = _tf(fb).paragraphs[0]; fp.text = footer
    fp.font.size = Pt(14); fp.font.color.rgb = GREY
    return s


def content(title, bullets):
    """bullets: list of (text, level, kind) ; kind in {'', 'ok','ko','code','head'}"""
    s = prs.slides.add_slide(BLANK)
    # bandeau titre
    bar = s.shapes.add_shape(1, Inches(0), Inches(0), W, Inches(1.15))
    bar.fill.solid(); bar.fill.fore_color.rgb = DARK; bar.line.fill.background()
    accent = s.shapes.add_shape(1, Inches(0), Inches(1.15), W, Inches(0.08))
    accent.fill.solid(); accent.fill.fore_color.rgb = ARGO; accent.line.fill.background()
    tb = s.shapes.add_textbox(Inches(0.6), Inches(0.18), Inches(12.1), Inches(0.9))
    tp = _tf(tb).paragraphs[0]; tp.text = title
    tp.font.size = Pt(30); tp.font.bold = True; tp.font.color.rgb = WHITE

    box = s.shapes.add_textbox(Inches(0.7), Inches(1.5), Inches(11.9), Inches(5.6))
    tf = _tf(box); first = True
    for text, level, kind in bullets:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.level = level
        run = p.add_run(); run.text = text
        f = run.font
        if kind == 'code':
            f.name = 'Consolas'; f.size = Pt(15); f.color.rgb = GREY
            p.space_before = Pt(2); p.space_after = Pt(2)
        elif kind == 'head':
            f.size = Pt(20); f.bold = True; f.color.rgb = ARGO
            p.space_before = Pt(8)
        elif kind == 'ok':
            f.size = Pt(18); f.color.rgb = GREEN; f.bold = True
        elif kind == 'ko':
            f.size = Pt(18); f.color.rgb = RED; f.bold = True
        else:
            f.size = Pt(18 - level * 2); f.color.rgb = DARK
            p.space_after = Pt(4)
            if level == 0:
                f.bold = False
    return s


# ----------------------------------------------------------------------------
B = lambda t, lvl=0, k='': (t, lvl, k)

title_slide(
    "Argo Rollouts",
    "Déploiement progressif & rollback automatique sur Kubernetes",
    "Projet de recherche — Écosystème Kubernetes & GitOps   •   Louis — 2026",
)

content("Plan", [
    B("1.  La technologie — problème, définition, fonctionnement", 0, 'head'),
    B("2.  Cas d'usage professionnel — où, comment, avantages/limites", 0, 'head'),
    B("3.  Mise en œuvre technique — architecture, manifests, démo live", 0, 'head'),
    B("4.  Retour d'expérience — bilan, avis, améliorations", 0, 'head'),
    B("", 0),
    B("Démo 100% fonctionnelle : ArgoCD (GitOps) + Argo Rollouts + analyse", 0),
    B("automatique sur un cluster local kind.", 0),
])

content("Le problème : le Deployment classique", [
    B("Un Deployment fait un rolling update : il remplace les pods un à un…", 0),
    B("sans jamais vérifier si la nouvelle version fonctionne correctement.", 0),
    B("", 0),
    B("Une v2 buggée part vers 100% des utilisateurs", 0, 'ko'),
    B("Détection tardive (alertes, support, utilisateurs mécontents)", 0, 'ko'),
    B("Rollback manuel, sous stress, en plein incident", 0, 'ko'),
    B("", 0),
    B("On déploie « en aveugle ». Besoin : déployer prudemment et MESURER avant de généraliser.", 0, 'head'),
])

content("Qu'est-ce qu'Argo Rollouts ?", [
    B("Un contrôleur Kubernetes (projet CNCF, famille Argo) qui remplace le", 0),
    B("Deployment par une ressource Rollout offrant la progressive delivery :", 0),
    B("", 0),
    B("Canary : un % croissant du trafic vers la nouvelle version", 0, ''),
    B("Blue-Green : deux environnements, bascule instantanée", 0, ''),
    B("Analyse automatique : promotion ou rollback piloté par des métriques", 0, ''),
    B("", 0),
    B("Objectif : une mise en production graduelle, mesurée et réversible automatiquement.", 0, 'head'),
])

content("Fonctionnement global", [
    B("Rollout (remplace Deployment)", 0, 'code'),
    B("   ├─ ReplicaSet STABLE   (version actuelle)", 0, 'code'),
    B("   ├─ ReplicaSet CANARY   (nouvelle version)", 0, 'code'),
    B("   └─ AnalysisRun         (mesure la santé du canary → décide)", 0, 'code'),
    B("", 0),
    B("À chaque palier (setWeight 20 → 40 → …), le contrôleur :", 0, 'head'),
    B("ajuste la proportion de pods/trafic canary,", 1),
    B("marque une pause (manuelle ou minutée),", 1),
    B("lance une analyse ; si elle échoue → rollback automatique.", 1),
])

content("Les briques : Rollout + AnalysisTemplate", [
    B("Rollout — la stratégie :", 0, 'head'),
    B("strategy:", 0, 'code'),
    B("  canary:", 0, 'code'),
    B("    steps:", 0, 'code'),
    B("      - setWeight: 20", 0, 'code'),
    B("      - pause: { duration: 30s }", 0, 'code'),
    B("      - setWeight: 40", 0, 'code'),
    B("      - analysis: { templates: [{ templateName: success-rate }] }", 0, 'code'),
    B("", 0),
    B("AnalysisTemplate — le critère de décision (métrique Prometheus, requête HTTP,", 0),
    B("ou Job de sonde). Hors limites → métrique Failed → Rollout avorté → retour stable.", 0),
])

content("Cas d'usage en entreprise & écosystème", [
    B("Réduction du risque de mise en prod : tester la v2 sur 5–10% du trafic réel", 0),
    B("Déploiements fréquents (plusieurs/jour) sans fenêtre de maintenance", 0),
    B("SLO-driven delivery : promotion conditionnée à des métriques (latence,", 0),
    B("taux d'erreur, succès) issues de Prometheus, Datadog, New Relic, CloudWatch…", 1),
    B("Couplé au GitOps (ArgoCD/Flux) : déploiement déclaratif, auditable, reproductible", 0),
    B("Projet CNCF (Argoproj) — combo standard avec ArgoCD ; voisins : Flagger, Spinnaker", 0),
    B("", 0),
    B("Contextes : microservices, APIs critiques, e-commerce, SaaS à fort trafic.", 0, 'head'),
])

content("Avantages / Limites", [
    B("Avantages", 0, 'ok'),
    B("Rollback automatique en cas de régression → moins d'incidents", 1),
    B("Pas de downtime, exposition contrôlée", 1),
    B("Décision objective (métriques) plutôt qu'« au feeling »", 1),
    B("Intégration native : ArgoCD, Prometheus, Istio, NGINX", 1),
    B("Limites", 0, 'ko'),
    B("Complexité accrue (CRD, analyse, parfois service mesh)", 1),
    B("Contrôle fin du trafic = Istio/NGINX/SMI (sinon split par nb de pods)", 1),
    B("Nécessite de bonnes métriques : analyse mal calibrée = fausse confiance", 1),
])

content("Architecture de la démo", [
    B("Cluster local kind + ArgoCD (déjà en place) + Argo Rollouts v1.7.2", 0, 'head'),
    B("git push ─▶ GitHub Actions (lint/validation des manifests)", 0, 'code'),
    B("        └─▶ ArgoCD (pull) ─▶ Rollout ─▶ Contrôleur Argo Rollouts", 0, 'code'),
    B("                                          ├─ RS stable / RS canary", 0, 'code'),
    B("                                          └─ AnalysisRun (Job de sonde HTTP)", 0, 'code'),
    B("", 0),
    B("App de démo : argoproj/rollouts-demo — une couleur par version.", 0),
    B("Le tag spécial bad-red renvoie des HTTP 500 (version buggée déterministe).", 0),
])

content("Choix techniques clés", [
    B("Stratégie canary sans service mesh → split par nombre de pods (simple, portable)", 0),
    B("Services stable + canary : le contrôleur y injecte le pod-template-hash", 0),
    B("→ la sonde cible précisément les pods canary", 1),
    B("Probes TCP (et non HTTP /color) : les pods bad-red restent Ready malgré les 500", 0),
    B("→ on démontre un rollback piloté par l'ANALYSE, pas par la santé", 1),
    B("AnalysisTemplate type Job : 30 requêtes, exige ≥ 95% de succès", 0),
    B("(autonome ; variante Prometheus fournie pour la production)", 1),
])

content("Démo 1 — Canary SAIN (promotion auto)", [
    B("set image … :green  →  le rollout progresse :", 0, 'head'),
    B("Step 1/9  setWeight 20%   ▸ 1 pod green / 4 pods blue", 0, 'code'),
    B("Step 4/9  setWeight 40%   ▸ AnalysisRun lancé", 0, 'code'),
    B('   probe ▸ "30/30 requetes en succes -> 100% (seuil 95%)  ANALYSE OK"', 0, 'code'),
    B("Step 9/9  setWeight 100%  ▸ Healthy, stable = green", 0, 'code'),
    B("", 0),
    B("Analyse réussie → promotion automatique jusqu'à 100%.", 0, 'ok'),
])

content("Démo 2 — Canary DÉFAILLANT (rollback auto)", [
    B("set image … :bad-red  →  l'analyse sonde le canary :", 0, 'head'),
    B("probe ▸ HTTP/1.1 500 Internal Server Error  (x25)", 0, 'code'),
    B('probe ▸ "5/30 requetes en succes -> 16% (seuil 95%)  ANALYSE KO"', 0, 'code'),
    B("Status: Degraded", 0, 'code'),
    B('Message: RolloutAborted: Metric "http-success-rate" assessed Failed', 0, 'code'),
    B("         due to failed (1) > failureLimit (0)", 0, 'code'),
    B("", 0),
    B("Analyse échouée → rollback automatique : trafic gardé sur green,", 0, 'ko'),
    B("zéro impact utilisateur, zéro intervention humaine.", 0, 'ko'),
])

content("Difficultés rencontrées & solutions", [
    B("App sans /metrics → analyse Prometheus impossible", 0, 'head'),
    B("AnalysisTemplate type Job (sonde HTTP autonome)", 1),
    B("Probe HTTP tuait les pods bad-red (500) avant l'analyse", 0, 'head'),
    B("Bascule en probe TCP : pods Ready mais erreurs mesurées par l'analyse", 1),
    B("Cibler uniquement le canary pour la sonde", 0, 'head'),
    B("Services stable/canary gérés par le contrôleur (pod-template-hash)", 1),
    B("Disque limité (94%)", 0, 'head'),
    B("Pas de stack Prometheus lourd : dashboard Rollouts + kind load des images", 1),
])

content("Retour d'expérience : bilan, avis, améliorations", [
    B("Appris : progressive delivery en pratique (étapes, pauses, analyse, rollback) ;", 0),
    B("imbrication GitOps ↔ Rollouts ; les métriques comme contrat de qualité.", 0),
    B("Points forts : rollback auto fiable, intégration native, déclaratif", 0, 'ok'),
    B("Points faibles : complexité, trafic fin nécessitant un mesh, analyse à calibrer", 0, 'ko'),
    B("Mon avis : excellent compromis sécurité/vélocité pour des services critiques ;", 0, 'head'),
    B("overkill pour un petit projet mono-service à faible trafic.", 0),
    B("Améliorations possibles :", 0, 'head'),
    B("Trafic fin via Istio/NGINX • analyse Prometheus réelle (p95 + erreurs) •", 1),
    B("notifications Slack • Blue-Green avec tests preview • multi-cluster ApplicationSet", 1),
])

title_slide(
    "Merci — Questions ?",
    "kubectl argo rollouts get rollout rollouts-demo --watch",
    "Dépôt : manifests • GitOps • CI • diagrammes • captures réelles d'exécution",
)

import os
out = os.path.join(os.path.dirname(__file__), "argo-rollouts.pptx")
prs.save(out)
print(f"OK -> {out}  ({len(prs.slides.__iter__.__self__._sldIdLst)} slides)")
