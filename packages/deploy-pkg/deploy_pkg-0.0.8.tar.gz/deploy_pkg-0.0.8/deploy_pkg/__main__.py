#!/usr/bin/env python3
"""
deploy_pkg
=========

Script « one-shot » pour :

1. Vérifier la présence de Git (sinon erreur explicite).
2. Installer au vol les dépendances Python requises (build, twine, toml,
   python-dotenv, requests) si elles manquent.
3. Charger `.env` ; récupérer GITHUB_TOKEN (+ éventuel PKG_NAME).
4. Déterminer le nom du paquet :
      - s’il existe déjà un pyproject.toml → on récupère `project.name`
      - sinon PKG_NAME dans .env → sinon nom du dossier racine
5. Interroger l’API GitHub pour obtenir nom complet, email et login.
6. Créer automatiquement (si absent) :
      - pyproject.toml (PEP 621 complet, version 0.0.1)
      - README.md, LICENSE (MIT), MANIFEST.in, .gitignore
      - Avertir si le nom est déjà pris sur PyPI.
7. Nettoyer build/ dist/ *.egg-info/ __pycache__/ etc.
8. Incrémenter le patch de version dans pyproject.toml.
9. S’il existe un `package.json` quelque part :
      - bump de version
      - `npm install` puis `npm run build`.
10. Construire le paquet Python (`python -m build`).
11. Installer/mettre à jour localement en mode editable (`pip install -U -e .`).
12. Initialiser Git s’il n’existe pas, premier commit, .gitignore.
13. Créer le repo GitHub via l’API si `origin` absent, ajouter remote,
    push branche main.
14. Commit « patch update #<version> », tag `v<version>`, push + tags.
15. Publier `dist/*` sur PyPI avec Twine.

Aucun prompt, tout est automatique.
"""

import os
import sys
import shutil
import subprocess
import json
from pathlib import Path

# ----------------------------------------------------------------------
# 0. Vérifier la présence de Git
# ----------------------------------------------------------------------
import shutil as _shutil
if _shutil.which("git") is None:
    sys.exit("❌ Git n’est pas installé ou indisponible dans le PATH.")

# ----------------------------------------------------------------------
# 1. Installer/charger les libs tierces au besoin
# ----------------------------------------------------------------------
def ensure_tools():
    try:
        import toml, build, twine, dotenv, requests  # noqa
    except ImportError:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade",
             "build", "twine", "toml", "python-dotenv", "requests"],
            check=True
        )

ensure_tools()

import toml
import requests
from dotenv import load_dotenv

# ----------------------------------------------------------------------
# 2. Contexte & helpers
# ----------------------------------------------------------------------
ROOT = Path.cwd()
PYPROJECT = ROOT / "pyproject.toml"

def run(cmd, **kw):
    """simple wrapper check=True"""
    subprocess.run(cmd, check=True, **kw)

def bump_patch(v: str) -> str:
    major, minor, patch = map(int, v.split('.'))
    return f"{major}.{minor}.{patch + 1}"

def pypi_name_taken(name: str) -> bool:
    return requests.get(f"https://pypi.org/pypi/{name}/json").status_code == 200

def git(*args):
    run(["git", *args])

# ----------------------------------------------------------------------
# 3. Charger .env ; récupérer le token GitHub et PKG_NAME override
# ----------------------------------------------------------------------
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    sys.exit("❌ GITHUB_TOKEN manquant dans .env")

PKG_NAME_ENV = os.getenv("PKG_NAME")  # facultatif

# ----------------------------------------------------------------------
# 4. Déterminer le nom du paquet
# ----------------------------------------------------------------------
if PYPROJECT.exists():
    data_tmp = toml.load(PYPROJECT)
    PKG_NAME = data_tmp["project"]["name"]
else:
    PKG_NAME = PKG_NAME_ENV or ROOT.name.replace(" ", "_")

# ----------------------------------------------------------------------
# 5. Infos développeur depuis GitHub
# ----------------------------------------------------------------------
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
user_json = requests.get("https://api.github.com/user", headers=HEADERS).json()
GH_LOGIN = user_json.get("login") or "unknown"
GH_NAME  = user_json.get("name")  or GH_LOGIN
GH_EMAIL = (user_json.get("email")
            or f"{GH_LOGIN}@users.noreply.github.com")

# ----------------------------------------------------------------------
# 6. Bootstrapping fichiers de base si absents
# ----------------------------------------------------------------------
if not PYPROJECT.exists():
    if pypi_name_taken(PKG_NAME):
        print(f"⚠️  Le nom « {PKG_NAME} » est déjà utilisé sur PyPI.")
    print("📝 Création pyproject.toml…")
    PYPROJECT.write_text(toml.dumps({
        "project": {
            "name": PKG_NAME,
            "version": "0.0.1",
            "description": "",
            "readme": "README.md",
            "license": {"text": "MIT"},
            "authors": [{"name": GH_NAME, "email": GH_EMAIL}],
            "requires-python": ">=3.8",
            "dependencies": [],
        },
        "build-system": {
            "requires": ["setuptools>=64", "wheel"],
            "build-backend": "setuptools.build_meta"
        }
    }))

if not (ROOT / "README.md").exists():
    (ROOT / "README.md").write_text(f"# {PKG_NAME}\n\nGenerated by deploy_me\n")
if not (ROOT / "LICENSE").exists():
    (ROOT / "LICENSE").write_text(
        "MIT License\n\n"
        "Permission is hereby granted, free of charge, to any person obtaining a copy "
        "of this software and associated documentation files..."
    )
if not (ROOT / "MANIFEST.in").exists():
    (ROOT / "MANIFEST.in").write_text("include README.md\ninclude LICENSE\n")
if not (ROOT / ".gitignore").exists():
    (ROOT / ".gitignore").write_text(
        "__pycache__/\n.env\n.DS_Store\n*.egg-info/\ndist/\nbuild/\n")

# ----------------------------------------------------------------------
# 7. Nettoyage build
# ----------------------------------------------------------------------
for d in ("build", "dist"):
    shutil.rmtree(ROOT / d, ignore_errors=True)
for egg in ROOT.glob("*.egg-info"):
    shutil.rmtree(egg, ignore_errors=True)
for p in ROOT.rglob("__pycache__"):
    shutil.rmtree(p, ignore_errors=True)

# ----------------------------------------------------------------------
# 8. Bump version dans pyproject.toml
# ----------------------------------------------------------------------
data = toml.load(PYPROJECT)
old_version = data["project"]["version"]
new_version = bump_patch(old_version)
data["project"]["version"] = new_version
PYPROJECT.write_text(toml.dumps(data))
print(f"🔖 Version : {old_version} → {new_version}")

# ----------------------------------------------------------------------
# 9. Frontend éventuel
# ----------------------------------------------------------------------
pkg_json = next(ROOT.glob("**/package.json"), None)
if pkg_json:
    with pkg_json.open() as f:
        pkg = json.load(f)
    v_old = pkg.get("version", "0.0.0")
    v_new = bump_patch(v_old)
    pkg["version"] = v_new
    pkg_json.write_text(json.dumps(pkg, indent=2))
    run(["npm", "install"], cwd=pkg_json.parent)
    run(["npm", "run", "build"], cwd=pkg_json.parent)
    print(f"🌐 Frontend version : {v_old} → {v_new}")

# ----------------------------------------------------------------------
# 10. Build Python
# ----------------------------------------------------------------------
run([sys.executable, "-m", "build"])

# ----------------------------------------------------------------------
# 11. Installation locale editable
# ----------------------------------------------------------------------
run([sys.executable, "-m", "pip", "install", "--upgrade", "-e", "."])
print("✅ Paquet installé/à-jour localement (-e).")

# ----------------------------------------------------------------------
# 12. Initialisation Git si besoin
# ----------------------------------------------------------------------
if not (ROOT / ".git").exists():
    git("init")
    git("add", ".")
    git("commit", "-m", "Initial commit")
    print("🗂️  Dépôt Git initialisé.")

# ----------------------------------------------------------------------
# 13. Création repo GitHub & remote origin si absent
# ----------------------------------------------------------------------
remotes = subprocess.run(["git", "remote"], capture_output=True,
                         text=True).stdout.strip().splitlines()
if "origin" not in remotes:
    repo_url = f"https://github.com/{GH_LOGIN}/{PKG_NAME}.git"
    create = requests.post("https://api.github.com/user/repos",
                           headers=HEADERS,
                           json={"name": PKG_NAME, "private": False})
    if create.status_code not in (201, 422):  # 422 = déjà existant
        sys.exit(f"❌ Erreur création repo GitHub : {create.text}")
    git("remote", "add", "origin", repo_url)
    git("branch", "-M", "main")
    git("push", "-u", "origin", "main")
    print(f"🌍 Repo GitHub prêt : {repo_url}")

# ----------------------------------------------------------------------
# 13 bis. Harmoniser le nom du repo si le pyproject a changé
# ----------------------------------------------------------------------
def current_remote_repo():
    url = subprocess.run(["git", "remote", "get-url", "origin"],
                         capture_output=True, text=True).stdout.strip()
    # formats possibles : https://github.com/user/repo.git  ou  git@github.com:user/repo.git
    repo_slug = url.rsplit("/", 1)[-1].removesuffix(".git")
    return repo_slug

remote_repo_name = current_remote_repo()

if remote_repo_name != PKG_NAME:
    print(f"🔄 Le repo GitHub s’appelle « {remote_repo_name} », "
          f"mais le paquet est « {PKG_NAME} » → renommage…")

    # 1. rename via GitHub API
    patch = requests.patch(
        f"https://api.github.com/repos/{GH_LOGIN}/{remote_repo_name}",
        headers=HEADERS,
        json={"name": PKG_NAME}
    )
    if patch.status_code not in (200, 201):
        sys.exit(f"❌ Impossible de renommer le repo GitHub : {patch.text}")

    # 2. mettre à jour l'URL du remote local
    new_url = f"https://github.com/{GH_LOGIN}/{PKG_NAME}.git"
    git("remote", "set-url", "origin", new_url)
    print(f"✅ Renommé → {new_url}")

    # 3. avertissement éventuel sur le dossier
    if ROOT.name != PKG_NAME:
        print(f"⚠️  Ton dossier local s’appelle « {ROOT.name} ». "
              f"Si tu veux l’harmoniser, renomme-le manuellement.")
        
# ----------------------------------------------------------------------
# 14. Commit patch, tag, push
# ----------------------------------------------------------------------
git("add", ".")
git("commit", "-m", f"patch update #{new_version}")
git("tag", f"v{new_version}")
git("push")
git("push", "--tags")
print(f"🚀 Pushed tag v{new_version}")

# ----------------------------------------------------------------------
# 15. Upload sur PyPI
# ----------------------------------------------------------------------
run(["twine", "upload", "dist/*"])
print("🎉 Déploiement PyPI terminé !")
