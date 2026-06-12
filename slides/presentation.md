---
marp: true
title: Argo Rollouts — Progressive Delivery & GitOps
author: Louis
paginate: true
theme: default
---

<!-- _class: lead -->

# Argo Rollouts
## Déploiement progressif & rollback automatique sur Kubernetes

Projet de recherche — Écosystème Kubernetes & GitOps

*Louis — 2026*

---

# Plan

1. **La technologie** — le problème, ce qu'est Argo Rollouts, son fonctionnement
2. **Cas d'usage professionnel** — où, comment, avantages/limites
3. **Mise en œuvre technique** — architecture, manifests, démo live
4. **Retour d'expérience** — bilan, avis, améliorations

> Démo 100 % fonctionnelle : ArgoCD (GitOps) + Argo Rollouts + analyse automatique sur un cluster local `kind`.

---

<!-- _class: lead -->
# 1. La technologie

---

# Le problème : le `Deployment` classique

Un `Deployment` fait un **rolling update** : il remplace les pods un à un…
**sans jamais vérifier** si la nouvelle version fonctionne correctement.

- 🔴 Une v2 buggée part vers **100 % des utilisateurs**
- 🔴 Détection tardive (alertes, support, utilisateurs mécontents)
- 🔴 Rollback **manuel**, sous stress, en pleine incident

➡️ On déploie « en aveugle ». Le besoin : **déployer prudemment et mesurer avant de généraliser**.

---

# Qu'est-ce qu'Argo Rollouts ?

Un **contrôleur Kubernetes** (projet CNCF, famille Argo) qui remplace le
`Deployment` par une ressource **`Rollout`** offrant des stratégies de
*progressive delivery* :

- **Canary** : on envoie un % croissant du trafic vers la nouvelle version
- **Blue-Green** : deux environnements, bascule instantanée
- **Analyse automatique** : promotion ou rollback **piloté par des métriques**

> Objectif : transformer un déploiement « tout ou rien » en une mise en
> production **graduelle, mesurée et réversible automatiquement**.

---

# Fonctionnement global

```
Rollout (remplace Deployment)
   │
   ├─ ReplicaSet STABLE  (version actuelle)
   ├─ ReplicaSet CANARY  (nouvelle version)
   └─ AnalysisRun        (mesure la santé du canary → décide)
```

À chaque palier (`setWeight 20 → 40 → …`), le contrôleur :
1. ajuste la proportion de pods/trafic canary,
2. (optionnel) marque une **pause** (manuelle ou minutée),
3. lance une **analyse** ; si elle échoue → **rollback automatique**.

---

# Les briques : Rollout + AnalysisTemplate

**`Rollout`** — la stratégie :
```yaml
strategy:
  canary:
    steps:
      - setWeight: 20
      - pause: { duration: 30s }
      - setWeight: 40
      - analysis: { templates: [{ templateName: success-rate }] }
```

**`AnalysisTemplate`** — le critère de décision (métrique Prometheus, requête
HTTP, ou Job de sonde). Si le résultat sort des clous → la métrique est
`Failed` → le Rollout est **avorté** et revient à la version stable.

---

<!-- _class: lead -->
# 2. Cas d'usage professionnel

---

# Comment c'est utilisé en entreprise

- **Réduction du risque de mise en prod** : tester la v2 sur 5–10 % du trafic réel
- **Déploiements fréquents** (plusieurs/jour) sans fenêtre de maintenance
- **SLO-driven delivery** : promotion conditionnée à des métriques (latence,
  taux d'erreur, taux de succès) issues de Prometheus/Datadog/New Relic
- **Couplé au GitOps** (ArgoCD/Flux) : le déploiement progressif devient
  déclaratif, auditable et reproductible

Contextes typiques : microservices, APIs critiques, e-commerce, SaaS à fort trafic.

---

# Avantages / Limites

**✅ Avantages**
- Rollback **automatique** en cas de régression → moins d'incidents
- Pas de downtime, exposition contrôlée
- Décision objective (métriques) plutôt qu'« au feeling »
- S'intègre nativement à l'écosystème (ArgoCD, Prometheus, Istio, NGINX)

**⚠️ Limites**
- Complexité accrue (CRD, analyse, parfois service mesh)
- Le contrôle **fin** du trafic exige Istio / NGINX / SMI (sinon split par nb de pods)
- Nécessite de **bonnes métriques** : une analyse mal calibrée = fausse confiance
- Courbe d'apprentissage, observabilité indispensable

---

# Écosystème & adoption

- **Projet CNCF** (Argoproj), même famille qu'**ArgoCD** — combo standard du marché
- Alternatives / voisins : **Flagger** (Flux), **Spinnaker**, déploiements Istio natifs
- Intégrations natives d'analyse : **Prometheus**, Datadog, New Relic, Wavefront,
  CloudWatch, Graphite, Job/Web custom
- Utilisé par de grands acteurs cloud-native pour la *continuous delivery* à grande échelle

---

<!-- _class: lead -->
# 3. Mise en œuvre technique

---

# Architecture de la démo

Cluster local **kind** + **ArgoCD** (déjà en place) + **Argo Rollouts v1.7.2**.

```
git push ─▶ GitHub Actions (lint/validation des manifests)
        └─▶ ArgoCD (pull) ─▶ Rollout ─▶ Contrôleur Argo Rollouts
                                          ├─ RS stable / RS canary
                                          └─ AnalysisRun (Job de sonde HTTP)
```

App de démo : `argoproj/rollouts-demo` — une **couleur par version** ;
le tag spécial **`bad-red`** renvoie des **HTTP 500** (version « buggée » déterministe).

---

# Choix techniques clés

- **Stratégie canary** sans service mesh → split par nombre de pods (simple, portable)
- **Services `stable` + `canary`** : le contrôleur y injecte le `pod-template-hash`
  → la sonde cible **précisément** les pods canary
- **Probes TCP** (et non HTTP `/color`) : les pods `bad-red` restent *Ready* malgré
  les 500 → on démontre un rollback **piloté par l'analyse**, pas par la santé
- **AnalysisTemplate de type Job** : sonde 30 requêtes, exige ≥ 95 % de succès
  (autonome, sans dépendance externe ; variante **Prometheus** fournie pour la prod)

---

# Démo 1 — Canary SAIN (promotion auto)

`set image … :green` puis le rollout progresse :

```
Step 1/9  setWeight 20%   ▸ 1 pod green / 4 pods blue
Step 4/9  setWeight 40%   ▸ AnalysisRun lancé
   probe ▸ "30/30 requetes en succes -> 100% (seuil 95%)  ANALYSE OK"
Step 9/9  setWeight 100%  ▸ ✔ Healthy, stable = green
```

✅ Analyse réussie → **promotion automatique** jusqu'à 100 %.

---

# Démo 2 — Canary DÉFAILLANT (rollback auto)

`set image … :bad-red` → l'analyse sonde le canary :

```
probe ▸ HTTP/1.1 500 Internal Server Error  (x25)
probe ▸ "5/30 requetes en succes -> 16% (seuil 95%)  ANALYSE KO"

Status: ✖ Degraded
Message: RolloutAborted: Metric "http-success-rate" assessed Failed
         due to failed (1) > failureLimit (0)
```

❌ Analyse échouée → **rollback automatique** : le trafic reste sur `green`,
**zéro impact utilisateur**, **zéro intervention humaine**.

---

# Difficultés rencontrées & solutions

| Difficulté | Solution apportée |
|---|---|
| App sans `/metrics` → analyse Prometheus impossible | AnalysisTemplate **type Job** (sonde HTTP autonome) |
| Probe HTTP tuait les pods `bad-red` (500) avant l'analyse | Bascule en **probe TCP** : pods *Ready* mais erreurs mesurées par l'analyse |
| Cibler uniquement le canary pour la sonde | **Services stable/canary** gérés par le contrôleur (pod-template-hash) |
| Disque limité (94 %) | Pas de stack Prometheus lourd : **dashboard Rollouts** + images chargées via `kind load` |

---

<!-- _class: lead -->
# 4. Retour d'expérience

---

# Bilan & avis technique

**Ce que j'ai appris**
- Le *progressive delivery* en pratique : étapes, pauses, analyse, rollback
- L'imbrication **GitOps (ArgoCD) ↔ Rollouts** : déploiement déclaratif et sûr
- L'importance des **métriques** comme contrat de qualité d'un déploiement

**Points forts** : rollback auto fiable, intégration native, déclaratif.
**Points faibles** : complexité, trafic fin nécessitant un mesh, analyse à bien calibrer.

**Mon avis** : excellent compromis sécurité/vélocité pour des services critiques ;
overkill pour un petit projet mono-service à faible trafic.

---

# Améliorations possibles

- **Contrôle fin du trafic** via Istio/NGINX (vrais pourcentages, pas par pods)
- **Analyse Prometheus** réelle (latence p95 + taux d'erreur) plutôt qu'une sonde
- **Notifications** (Slack) sur promotion/abort
- **Blue-Green** + tests automatisés sur l'environnement *preview*
- **Multi-cluster** via ArgoCD ApplicationSet

---

<!-- _class: lead -->

# Merci — Questions ?

**Dépôt** : manifests, GitOps, CI, diagrammes, captures réelles
`kubectl argo rollouts get rollout rollouts-demo --watch`
