Cahier des charges  
Pipeline automatique de génération de vidéos narrées et illustrées
===============================================================

1. Contexte et objectif  
• Automatiser la création d’une vidéo à partir d’un simple transcript texte.  
• Génération séquentielle : scénario → voix-off → visuels → montage FFmpeg.  
• Réduire l’intervention humaine en sécurisant chaque étape contre les échecs.

2. Périmètre du projet  
Inclus : script CLI, extraction du scénario, TTS, génération d’images, montage, logs, gestion des erreurs, tests.  
Exclus : rédaction du transcript, hébergement des modèles, distribution de la vidéo finale.

3. Architecture cible  
• Langage : Python 3.10+.  
• Modules internes :  
  - extraction_markdown.py  
  - generate_audio.py  
  - generate_images.py  
  - montage_video_ffmpeg.py  
  - logger_setup.py  
  - make_video.py (point d’entrée).  
• Dépendances : tenacity, colorlog, tqdm, ffmpeg (binaire), TTS engine, modèle de diffusion/stable-diffusion.  
• Dossiers :  
  input/ (transcripts)  
  output/ (résultats)  
  logs/ (run.log, errors.log)  
  cache/ (modèles, checkpoints).

4. Workflow détaillé  
1) Extraction du scénario  
   • Lecture transcript .txt/.md → JSON {chapters:[{id,title,text,prompt}…]}.  
2) Génération audio  
   • TTS par chapitre, WAV mono 48 kHz.  
3) Génération images  
   • 1 image 1024×1024 par chapitre.  
4) Montage vidéo  
   • FFmpeg assemble images + voix-off + fond musical optionnel → MP4 H264 + AAC.  
5) Fin de pipeline → retour du chemin final et durée d’exécution.

5. Exigences fonctionnelles  
F1. CLI : `python make_video.py transcript.txt [-o DIR] [-v|-vv] [--skip audio,images]`.  
F2. Relance à chaud : les chapitres déjà validés sont ignorés (fichiers *.done).  
F3. Fallback images (Unsplash) ou audio (voix locale) si génération échoue.  
F4. Rapport HTML facultatif listant les chapitres, prompts, durées, erreurs.

6. Exigences non fonctionnelles  
N1. Robustesse : aucune exception non gérée ne doit arrêter le pipeline sans trace.  
N2. Traçabilité : tout événement ≥ ERROR enregistré dans logs/errors.log.  
N3. Performance : pipeline complet ≤ 1,5 × durée cumulée des audios + 30 %.  
N4. Portabilité : Linux et Windows, GPU facultatif mais recommandé.  
N5. Sécurité : aucune clé API en clair dans les sources ; utiliser variables d’environnement.

7. Gestion des erreurs  
E1. Exceptions métier : GenerationError, ImageGenerationError, AudioGenerationError.  
E2. Retry exponentiel (tenacity) : 3 tentatives images, 2 audio.  
E3. Post-condition : contrôle fichier créé, taille > 0, durée cohérente.  
E4. Circuit-breaker après N erreurs consécutives pour éviter la surcharge API.  
E5. Placeholder automatique en cas d’échec définitif.

8. Journalisation  
• Console colorée niveau INFO (ou DEBUG avec -vv).  
• logs/run.log : rotation quotidienne, niveau DEBUG.  
• logs/errors.log : niveau ERROR+.  
• Format : « L 12:34:56.789 [module] chapitre-004 Message ».  
• Capture des warnings Python et des exceptions non catchées.

9. Tests et qualité  
T1. Couverture unitaire ≥ 80 % des fonctions de haut niveau.  
T2. Mocks pour TTS, Stable-Diffusion, FFmpeg (pytest-mock).  
T3. CI GitHub Actions : lint (ruff), tests, build image Docker.  
T4. Benchmark hebdo : temps moyen par chapitre, taux d’erreurs.

10. Exploitation et monitoring  
• Métriques Prometheus (succès, échecs, latence, RAM, VRAM).  
• Alerting seuil > 5 % d’échecs sur 10 chapitres.  
• Tableau de bord Grafana prêt-à-l’emploi.

11. Livrables  
• Code source commenté.  
• Fichier requirements.txt + Dockerfile GPU et CPU.  
• Guide d’installation et d’exploitation (README).  
• Exemple de transcript + vidéo de démonstration.  
• Rapport de tests et de performance.

12. Planning indicatif  
S1 : Conception détaillée + mise en place repo CI (1 sem).  
S2 : Implémentation CLI, logging, extraction scénario (1 sem).  
S3 : Modules audio + image + retry (2 sem).  
S4 : Montage vidéo + placeholders + skip logic (1 sem).  
S5 : Tests, optimisation, documentation (1 sem).  
S6 : Recette et livraison (0,5 sem).

13. Critères d’acceptation  
✓ Lancement unique d’un transcript complet sans crash.  
✓ Vidéo MP4 lisible avec toutes les scènes.  
✓ logs/errors.log vide sur exécution nominale.  
✓ Redémarrage après plantage ne répète pas les chapitres OK.  
✓ 100 chapitres traités < 2 h sur machine cible.[{'index': 1}]