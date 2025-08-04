Gestion des dépendances : approche Poetry (recommandée) + alternative Pipenv
================================================================================

1. Installer l’outil  
   • Linux/mac :  
     ```bash
     curl -sSL https://install.python-poetry.org | python3 -
     ```  
   • Windows : exécuter le même script dans PowerShell.

2. Initialiser le projet  
   ```bash
   cd my-video-pipeline
   poetry init  # réponds ↵ pour accepter les valeurs par défaut
   ```
   Cela crée `pyproject.toml` (manifeste) et `.venv/` local.

3. Renseigner les contraintes
   ```bash
   poetry add tenacity colorlog tqdm
   poetry add --group dev pytest pytest-mock ruff
   ```
   • `--group dev` (anciennement `--dev`) garde les libs de test hors prod.  
   • Les versions figées vont dans `poetry.lock` ; **commit** les deux fichiers.

4. Gérer les dépendances lourdes / options GPU  
   Dans `pyproject.toml` :
   ```toml
   [tool.poetry.extras]
   gpu = ["torch==2.2.1+cu121", "xformers"]
   cpu = ["torch==2.2.1+cpu"]
   ```
   L’utilisateur choisit :
   ```bash
   poetry install --extras gpu
   ```

5. Dépendances système non Python  
   • FFmpeg : documenter `apt-get install ffmpeg` ou `choco install ffmpeg`.  
   • CUDA : pointer vers le toolkit Nvidia requis par la version de Torch.

6. Scripts de confort  
   Dans `[tool.poetry.scripts]` :
   ```toml
   make-video = "make_video:main"
   ```
   Lancement : `poetry run make-video transcript.txt -v`.

7. Variables d’environnement  
   • Ajouter `.env` (non commit) :  
     ```
     OPENAI_API_KEY=…
     UNSPLASH_TOKEN=…
     ```  
   • Poetry charge `.env` automatiquement depuis la v1.7.

8. Verrous de production  
   • CI : `poetry install --no-root --only main` (ignore extras dev).  
   • Dockerfile :  
     ```dockerfile
     COPY pyproject.toml poetry.lock .
     RUN poetry install --only main --no-root
     ```

9. Mise à jour contrôlée  
   ```bash
   poetry update --dry-run         # voir ce qui va changer
   poetry update tenacity -G main  # maj ciblée
   poetry lock --no-update         # regen lock si conflit manuel
   ```

10. Alternative Pipenv (si déjà en place)
    ```bash
    pipenv install tenacity colorlog tqdm
    pipenv install --dev pytest pytest-mock ruff
    pipenv lock --requirements > requirements.txt   # pour Docker
    ```
    • Lancer : `pipenv run make-video …`.  
    • Pour les extras GPU/CPU, créer deux fichiers `Pipfile-gpu`, `Pipfile-cpu` ou utiliser les environnements séparés.

11. Bonnes pratiques communes  
    • Garder toujours le lockfile sous contrôle de version.  
    • `pre-commit` : installez ruff, black, isort en hooks.  
    • Ne mélangez pas `pip install` manuel dans la venv Poetry/Pipenv.  
    • Taguer vos releases Git avec la version du `pyproject.toml`.  
    • Documenter la commande de réinstallation :  
      ```bash
      git clone …
      cd project
      poetry install --extras gpu
      ```

Avec Poetry ou Pipenv, vous obtenez : iso-reproductibilité, isolation de l’environnement, scripts exécutables et mises à jour traçables—indispensables pour un pipeline multimédia où les bibliothèques évoluent vite.[{'index': 1}]