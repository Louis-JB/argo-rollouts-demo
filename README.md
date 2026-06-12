# Argo Rollouts — Progressive Delivery sur Kubernetes (démo GitOps)

> Projet de recherche — Écosystème Kubernetes & GitOps
> Sujet : **Argo Rollouts** (déploiement progressif : canary / blue-green avec analyse automatique)

Ce dépôt contient une implémentation complète et **fonctionnelle** d'un déploiement
*canary* automatisé sur Kubernetes, piloté en GitOps par ArgoCD, avec **promotion et
rollback automatiques** basés sur l'analyse d'un indicateur de qualité (taux de succès HTTP).

---

## 🎯 Le problème résolu

Un `Deployment` Kubernetes standard fait du *rolling update* : il remplace les anciens
pods par les nouveaux **sans mesurer** si la nouvelle version se comporte correctement.
Si la v2 est buggée, **100 % des utilisateurs** sont impactés, et le rollback est manuel.

**Argo Rollouts** remplace le `Deployment` par une ressource `Rollout` qui permet :

- d'exposer la nouvelle version à une **fraction progressive** du trafic (20 % → 40 % → …) ;
- de **mesurer automatiquement** sa santé (métriques, sondes) à chaque palier ;
- de **promouvoir** la version si tout va bien, ou de **revenir en arrière automatiquement**
  au moindre signe de dégradation — le tout sans intervention humaine.

---

## 🏗️ Architecture

Voir [diagrams/architecture.md](diagrams/architecture.md) pour les schémas Mermaid.

```
git push ──▶ GitHub Actions (lint/validation)
        └──▶ ArgoCD (pull) ──▶ Rollout ──▶ Contrôleur Argo Rollouts
                                              ├─ ReplicaSet stable
                                              ├─ ReplicaSet canary
                                              └─ AnalysisRun (sonde le canary, décide promote/rollback)
```

| Composant | Rôle |
|-----------|------|
| **ArgoCD** | GitOps : synchronise le cluster avec `manifests/` (déjà installé) |
| **Argo Rollouts** | Contrôleur de déploiement progressif (CRD `Rollout`, `AnalysisTemplate`) |
| **rollouts-demo** | App de démo : sert une couleur par version ; le tag `bad-red` renvoie des HTTP 500 |
| **AnalysisTemplate** | Sonde le service canary, calcule le taux de succès, décide |
| **Prometheus** | (optionnel) métriques du contrôleur / variante d'analyse réaliste |

---

## 📂 Structure du dépôt

```
manifests/        # Ce qu'ArgoCD déploie (Rollout, Services, AnalysisTemplate, namespace)
gitops/           # Application ArgoCD (la boucle GitOps)
monitoring/       # Prometheus + variante d'AnalysisTemplate basée Prometheus (production)
diagrams/         # Schémas d'architecture (Mermaid)
docs/             # Runbook de démo + captures réelles d'exécution
slides/           # Trame de la présentation (10-15 slides)
.github/workflows # CI : validation des manifests (kubeconform + yamllint)
```

---

## 🚀 Démarrage rapide

Prérequis : `docker`, `kind`, `kubectl`, `helm`, plugin `kubectl-argo-rollouts`.

```bash
# 1. (si besoin) créer un cluster + installer Argo Rollouts
kind create cluster --name argocd-cluster
kubectl create namespace argo-rollouts
kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/download/v1.7.2/install.yaml

# 2. déployer la démo
kubectl apply -k manifests/

# 3. suivre le rollout
kubectl argo rollouts get rollout rollouts-demo -n demo --watch
```

Le scénario complet (canary sain + canary défaillant) est détaillé dans
[docs/demo-runbook.md](docs/demo-runbook.md), avec les **sorties réelles** dans
[docs/captures/](docs/captures/).

---

## 🔁 GitOps (ArgoCD)

```bash
# adapter repoURL dans gitops/application.yaml, puis :
kubectl apply -f gitops/application.yaml
```

ArgoCD surveille alors `manifests/` : tout `git push` qui change l'image du Rollout
déclenche automatiquement un nouveau canary, analysé et promu/annulé sans action manuelle.

---

## ✅ Résultats de la démo (résumé)

| Scénario | Image canary | Taux de succès mesuré | Décision automatique |
|----------|--------------|-----------------------|----------------------|
| Canary sain | `green` | 30/30 = **100 %** | ✅ Promotion à 100 % |
| Canary défaillant | `bad-red` | 5/30 = **16 %** | ❌ **Rollback** (trafic conservé sur `green`) |

> Message du contrôleur lors du rollback :
> `Metric "http-success-rate" assessed Failed due to failed (1) > failureLimit (0)`

---

## 📸 Captures d'écran

- [docs/screenshots/](docs/screenshots/) — UI **ArgoCD** (Application Synced/Healthy + arbre de ressources)
  et **GitHub Actions** (CI au vert).
- [docs/captures/](docs/captures/) — sorties textuelles réelles de `kubectl argo rollouts`
  (canary sain, rollback automatique, logs de la sonde).
- [slides/img/](slides/img/) — captures intégrées au diaporama (dashboard Argo Rollouts
  canary/rollback, grille de trafic).
