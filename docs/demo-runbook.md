# Runbook de démonstration

Commandes exactes pour reproduire la démo en live (idéal pour la soutenance).
Les sorties réelles capturées sont dans [captures/](captures/).

> Astuce : exporter une fois pour toutes
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> CTX=kind-argocd-cluster
> alias kar="kubectl-argo-rollouts --context $CTX -n demo"
> ```

## 0. Déploiement initial

```bash
kubectl --context $CTX apply -k manifests/
kar get rollout rollouts-demo --watch    # Ctrl-C quand "Healthy"
```

## 1. Visualiser le trafic (facultatif mais joli)

```bash
# UI colorée : chaque carré = une requête, sa couleur = la version qui a répondu
kubectl --context $CTX -n demo port-forward svc/rollouts-demo 8080:80
# -> http://localhost:8080

# Dashboard Argo Rollouts (vue graphique des étapes/analyses)
kubectl argo rollouts dashboard -n demo
# -> http://localhost:3100
```

## 2. Scénario CANARY SAIN (promotion automatique)

```bash
kar set image rollouts-demo rollouts-demo=argoproj/rollouts-demo:green
kar get rollout rollouts-demo --watch
```
Observer : 20 % → pause → 40 % → **AnalysisRun** (sonde 30 req. = 100 %) → 60 % → 80 % → 100 %.
Résultat attendu : `Healthy`, image stable = `green`.
👉 captures `01`, `02`, `03`.

## 3. Scénario CANARY DÉFAILLANT (rollback automatique)

```bash
kar set image rollouts-demo rollouts-demo=argoproj/rollouts-demo:bad-red
kar get rollout rollouts-demo --watch
```
Observer : le canary démarre, l'analyse sonde le service canary → **16 % de succès** →
métrique `Failed` → `RolloutAborted` → retour automatique sur `green`.
👉 captures `04`, `05`, `06`.

```bash
# voir le log de la sonde qui a déclenché le rollback
kubectl --context $CTX -n demo logs -l job-name | grep -E "Resultat|ANALYSE"
```

## 4. Remise à l'état stable

```bash
kar set image rollouts-demo rollouts-demo=argoproj/rollouts-demo:green
```

## Commandes utiles pour la soutenance

```bash
kar get rollout rollouts-demo            # arbre d'état (stable/canary/analysis)
kar status rollouts-demo                 # statut court
kar promote rollouts-demo                # forcer la promotion (skip pause)
kar abort rollouts-demo                  # avorter manuellement
kar undo rollouts-demo                   # revenir à la révision précédente
kubectl -n demo get analysisrun          # historique des analyses
```
