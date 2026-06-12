#!/usr/bin/env bash
# Pousse ce dépôt sur GitHub et met à jour repoURL dans gitops/application.yaml.
# Prérequis : être authentifié (gh auth login)  OU  exporter un token : export GH_TOKEN=ghp_xxx
set -euo pipefail

REPO_NAME="${1:-argo-rollouts-demo}"
VISIBILITY="${2:-public}"   # public | private
export PATH="$HOME/.local/bin:$PATH"

cd "$(dirname "$0")"

# Authentification : token via env si fourni
if [ -n "${GH_TOKEN:-}" ]; then
  echo "$GH_TOKEN" | gh auth login --with-token
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "❌ Non authentifié. Lance d'abord :  gh auth login   (ou)   export GH_TOKEN=<ton_token>"
  exit 1
fi

USER=$(gh api user --jq .login)
echo "✓ Authentifié en tant que $USER"

git branch -M main

# Crée le repo s'il n'existe pas, sinon ajoute juste le remote
if gh repo view "$USER/$REPO_NAME" >/dev/null 2>&1; then
  echo "Le dépôt $USER/$REPO_NAME existe déjà — ajout du remote."
  git remote add origin "https://github.com/$USER/$REPO_NAME.git" 2>/dev/null || true
else
  gh repo create "$REPO_NAME" --"$VISIBILITY" --source=. --remote=origin --description "Argo Rollouts — progressive delivery & GitOps (projet de recherche)"
fi

# Met à jour repoURL dans l'Application ArgoCD
sed -i "s#https://github.com/CHANGEME/argo-rollouts-demo.git#https://github.com/$USER/$REPO_NAME.git#" gitops/application.yaml
git add gitops/application.yaml
git commit -q -m "GitOps: pointe repoURL vers le dépôt $USER/$REPO_NAME" || true

git push -u origin main
echo ""
echo "✅ Poussé sur https://github.com/$USER/$REPO_NAME"
echo "   Active la boucle GitOps :  kubectl apply -f gitops/application.yaml"
