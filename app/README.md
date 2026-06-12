# Application de démonstration

On n'écrit pas d'application maison : on réutilise l'image officielle
**`argoproj/rollouts-demo`**, conçue pour visualiser les déploiements.

- Sert une **couleur par version** (blue, green, yellow, orange, red, purple…).
  L'UI affiche une grille de carrés : la couleur de chaque carré = la version
  qui a répondu à la requête → on **voit** le trafic basculer pendant le canary.
- Endpoint `GET /color` : renvoie la couleur (HTTP 200).
- Tags spéciaux **`bad-*`** (ex. `bad-red`) : renvoient des **HTTP 500** —
  parfaits pour simuler une version défaillante et déclencher un rollback.

Aucun `/metrics` n'est exposé : c'est pourquoi l'analyse de la démo utilise un
**Job de sonde** plutôt que Prometheus (voir `../manifests/analysistemplate.yaml`).

Images préchargées dans le cluster kind :
```bash
kind load docker-image argoproj/rollouts-demo:blue argoproj/rollouts-demo:green \
  argoproj/rollouts-demo:bad-red busybox:1.36 --name argocd-cluster
```
