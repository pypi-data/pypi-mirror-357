# deploy_me

> 🚀 Le couteau suisse « one-shot » pour publier un paquet Python en un seul appel.

`deploy_me` automatise **tout** le pipeline :  
– bootstrap de projet (pyproject/README/licence/git…)  
– création de dépôt GitHub + push + tag  
– build Python & éventuel frontend npm  
– installation locale (_editable_)  
– publication PyPI via Twine  

Aucune interaction : lance et profite !

---

## Installation

```bash
pip install deploy_me
```

ou en local :

```bash
git clone https://github.com/<toi>/deploy_me.git
cd deploy_me
pip install -e .
```

---

## Pré-requis

| Outil               | Rôle                                  |
|---------------------|---------------------------------------|
| **git**             | versionnage + push GitHub             |
| **Python ≥ 3.8**    | exécution du script                   |
| **GITHUB_TOKEN**    | droits `repo` + `user:email`          |
| _(optionnel)_ **npm** | build du dossier `frontend/` (si présent) |

Crée un fichier `.env` :

```env
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
# PKG_NAME=override_nom_paquet   # (facultatif)
```

---

## Usage

Dans le dossier de **ton** projet (vide ou existant) :

```bash
deploy-me            # ou : python -m deploy_me
```

Le script :

1. installe les dépendances manquantes (`build`, `twine`, …)  
2. crée les fichiers de base s’ils n’existent pas  
3. incrémente le patch de version (`0.0.X → 0.0.X+1`)  
4. construit le paquet (`python -m build`)  
5. `pip install -U -e .`  
6. init git / commit / tag / push  
7. upload `dist/*` sur PyPI  

> **Boom !** Ton paquet est en ligne et déjà installé à jour sur ta machine.

---

## Exemples

### Publier un tout nouveau projet

```bash
mkdir awesome
cd awesome
deploy-me
# => crée pyproject, README, etc. puis publie automatiquement
```

### Publier un projet déjà existant

```bash
cd awesome
git status         # doit être propre
deploy-me
# => bump version, build, push, upload
```

---

## Dépendances runtime

- `requests`
- `toml`
- `python-dotenv`

Les outils « build » (`build`, `twine`) sont installés à la volée si absents.

---

## Pourquoi pas un simple *Makefile* ?

Parce que :

- tu oublies toujours une étape (« Twine ? tag git ? bump ?… »)  
- ça détecte et installe ce qu’il manque (git, deps Python, npm)  
- aucun copier-coller : **un fichier, une commande, fini**.

---

## Contribuer

Les MR / PR sont les bienvenues.  
Avant de pousser :

```bash
python -m pip install -e ".[dev]"
pytest
```

---

## Licence

MIT – fais-en bon usage, améliore-le, partage-le !
