Pipeline de Génération Vidéo Automatique
🚀 Vue d'ensemble du Projet
Ce pipeline automatise la création de vidéos narrées et illustrées à partir d'un simple fichier transcript en texte ou Markdown. Il orchestre de manière séquentielle plusieurs étapes critiques, en gérant les échecs et en assurant la traçabilité.

Fonctionnalités clés :

Interface en ligne de commande (CLI) robuste pour une utilisation aisée.

Journalisation détaillée et colorée pour le débogage et le monitoring.

Gestion d'erreurs résiliente avec des stratégies de "retry" pour les étapes fragiles (TTS, génération d'images).

Modules indépendants pour une maintenance simplifiée.

Conteneurisation (Docker) pour des déploiements reproductibles sur des environnements CPU ou GPU.

Relance à chaud pour reprendre le traitement après une interruption.

🛠️ Installation
Le projet utilise Poetry pour gérer ses dépendances.

Cloner le dépôt :

git clone https://github.com/votre-utilisateur/votre-projet.git
cd votre-projet

Installer Poetry :
Si Poetry n'est pas déjà installé, suivez les instructions officielles :
curl -sSL https://install.python-poetry.org | python3 -

Installer les dépendances :
Le pipeline nécessite le binaire ffmpeg. Assurez-vous qu'il est installé sur votre système et accessible via la variable d'environnement $PATH.

# Pour macOS:
brew install ffmpeg

# Pour Linux (Ubuntu):
sudo apt-get update && sudo apt-get install -y ffmpeg

Installez ensuite les dépendances Python du projet :

# Pour un environnement CPU:
poetry install --extras cpu

# Pour un environnement GPU (nécessite un driver NVIDIA compatible):
poetry install --extras gpu

💻 Utilisation
Le point d'entrée du pipeline est le script make_video.py.

Commande de base
Générez une vidéo à partir d'un fichier transcript :

poetry run python make_video.py input/mon_transcript.md

Options utiles
-o, --output-dir : Spécifiez un répertoire de sortie (par défaut : output/).

-v, --verbose : Augmentez le niveau de journalisation (utiliser -vv pour le mode DEBUG).

--skip : Sautez les étapes déjà traitées pour les chapitres dont les fichiers de sortie existent déjà.

Exemple de transcript (mon_transcript.md)
# Mon Super Sujet

Ceci est l'introduction du cours. Nous allons apprendre beaucoup de choses !

---

## Chapitre 1 : Les bases

Le premier chapitre couvre les concepts fondamentaux.
- Concept 1
- Concept 2

Ce paragraphe sert à illustrer le contenu.

---

## Chapitre 2 : La pratique

Maintenant, appliquons ce que nous avons appris.

---


🐳 Déploiement avec Docker
Pour un déploiement reproductible et conteneurisé, deux Dockerfiles sont fournis dans ce dépôt.

Dockerfile.cpu : Conçu pour les environnements sans accélération graphique dédiée.

Dockerfile.gpu : Optimisé pour tirer parti des GPUs NVIDIA avec CUDA.