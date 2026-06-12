# GitOps avec ArgoCD

`application.yaml` déclare une **Application ArgoCD** qui maintient le cluster
synchronisé avec le dossier [`../manifests`](../manifests) du dépôt.

## Activer la boucle GitOps

1. Pousser ce dépôt sur GitHub/GitLab.
2. Remplacer `repoURL` dans `application.yaml` par l'URL du dépôt.
3. Appliquer :
   ```bash
   kubectl apply -f gitops/application.yaml
   kubectl -n argocd get application rollouts-demo
   ```

Dès lors : tout `git push` modifiant l'image du Rollout déclenche
automatiquement un nouveau canary (analyse + promotion/rollback), sans `kubectl`.

## Pourquoi c'est puissant

- **Source unique de vérité** : l'état désiré est dans Git (versionné, auditable, reviewable)
- **Self-heal** : ArgoCD corrige toute dérive manuelle dans le cluster
- **Rollback applicatif** = simple `git revert`
- Combiné à Argo Rollouts : on obtient un **déploiement progressif déclaratif**
