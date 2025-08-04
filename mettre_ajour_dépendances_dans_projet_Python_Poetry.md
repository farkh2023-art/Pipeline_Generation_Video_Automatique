<think>
Nous sommes dans un projet Python utilisant Poetry pour la gestion des dépendances.
 L'utilisateur demande comment mettre à jour les dépendances.
 Étapes :
 1. Mettre à jour le fichier `pyproject.toml` (soit manuellement, soit via la commande `poetry add`)
 2. Mettre à jour le fichier `poetry.lock` pour refléter les versions exactes.
 3. Mettre à jour l'environnement virtuel.

 Je vais détailler les commandes et les bonnes pratiques.
</think>
Pour mettre à jour les dépendances dans un projet Python avec **Poetry**, suivez cette procédure complète :

---

### 1. Mise à jour contrôlée (recommandée)
```bash
# Afficher les dépendances obsolètes
poetry show --outdated

# Mettre à jour UNE dépendance spécifique
poetry add package@latest     # Version la plus récente
poetry add "package@^2.1"     # Spécifier une nouvelle borne

# Mettre à jour toutes les dépendances dans leurs contraintes actuelles
poetry update
```

---

### 2. Mise à jour agressive (attention aux breaking changes)
```bash
# Relâcher temporairement les contraintes dans pyproject.toml
# Exemple : remplacer "^1.2" par ">=1.2"

# Forcer la résolution des dernières versions
poetry update --latest
```

---

### 3. Mise à jour sélective par groupe
```toml
# pyproject.toml
[tool.poetry.group.dev.dependencies]
pytest = "^8.0"
mypy = "^1.8"
```
```bash
poetry update --group dev
```

---

### 4. Gestion des conflits
Après `poetry update` :
1. Si échec : examiner l'erreur (ex: `SolverProblemError`)
2. Ajuster manuellement les versions dans `pyproject.toml`
3. Relancer `poetry lock --no-update` pour recalculer le lockfile

---

### 5. Workflow complet pour une mise à jour sûre
```bash
# 1. Créer une branche
git checkout -b update-deps

# 2. Mettre à jour le lockfile
poetry update

# 3. Lancer les tests
poetry run pytest -v

# 4. Vérifier les régressions
git diff poetry.lock  # Examiner les changements

# 5. Valider (si les tests passent)
git add pyproject.toml poetry.lock
git commit -m "chore(deps): update packages"
```

---

### 6. Cas spéciaux
**Mettre à jour Python** :
```toml
# pyproject.toml
[tool.poetry.dependencies]
python = "^3.11"  # Changer la version ici
```
```bash
poetry env use python3.11  # Créer un nouvel environnement
poetry install
```

**Mettre à jour Poetry lui-même** :
```bash
poetry self update
```

---

### Bonnes pratiques
1. **Toujours versionner** `poetry.lock` dans le dépôt
2. **Mettre à jour régulièrement** (ex: mensuellement)
3. **Utiliser Dependabot** pour les mises à jour automatiques ([exemple config](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file))
4. **Vérifier les changements** sur [PyPI](https://pypi.org/) / [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/viewing-your-repositorys-releases-and-tags) avant les MAJ majeures

> ⚠️ **Testez systématiquement** après une mise à jour !  
> Les breaking changes sont fréquents dans les bibliothèques ML (Torch, TensorFlow, etc.).