Voici un modèle « prêt-à-coller » pour obtenir :

• un log lisible dans la console (niveau INFO par défaut, couleurs)  
• un fichier `run.log` complet (DEBUG)  
• un fichier `errors.log` dédié aux messages ≥ ERROR, rotation quotidienne  
• le chapitrage et l’horodatage milliseconde  
• la capture automatique des exceptions non interceptées

```python
# logger_setup.py
import logging, logging.config, pathlib, sys
from datetime import datetime

LOG_DIR = pathlib.Path("logs")
LOG_DIR.mkdir(exist_ok=True)

def build_logging_config(verbose: int = 0) -> dict:
    level_console = (logging.WARNING, logging.INFO, logging.DEBUG)[min(verbose, 2)]

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "plain": {
                "format": "%(levelname).1s %(asctime)s [%(name)s] %(message)s",
                "datefmt": "%H:%M:%S.%f",
            },
            "color": {   # nécessite `pip install colorlog`
                "()": "colorlog.ColoredFormatter",
                "format": "%(log_color)s%(levelname).1s "
                          "%(asctime)s %(reset)s%(blue)s%(message)s",
                "datefmt": "%H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "color",
                "level": level_console,
            },
            "run_file": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "formatter": "plain",
                "filename": LOG_DIR / "run.log",
                "when": "midnight",
                "backupCount": 7,
                "encoding": "utf-8",
                "level": "DEBUG",
            },
            "error_file": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "formatter": "plain",
                "filename": LOG_DIR / "errors.log",
                "when": "midnight",
                "backupCount": 14,
                "encoding": "utf-8",
                "level": "ERROR",
            },
        },
        "root": {
            "handlers": ["console", "run_file", "error_file"],
            "level": "DEBUG",
        },
    }

def configure_logging(verbose: int = 0):
    logging.config.dictConfig(build_logging_config(verbose))

    # Capte toute exception non gérée → logger.error(...)
    def _excepthook(exc_type, exc, tb):
        logging.getLogger("UNCAUGHT").exception("Exception non interceptée :", exc_info=(exc_type, exc, tb))
        sys.__excepthook__(exc_type, exc, tb)

    sys.excepthook = _excepthook
```

Intégration dans `make_video.py` :

```python
from logger_setup import configure_logging
import logging

def main():
    args = build_parser().parse_args()
    configure_logging(args.verbose)
    log = logging.getLogger(__name__)

    log.info("Pipeline démarré à %s", datetime.now().isoformat(timespec='seconds'))

    try:
        safe_call(generate_video_config, args.transcript, cfg_file)
        ...
    except Exception:
        log.exception("Arrêt inhabituel du pipeline")
        raise
```

Bonnes pratiques supplémentaires :

1. Contexte dynamique  
   Ajoutez `extra={"chapter": chap["id"]}` lors du log ; puis, dans le formatter : `%(chapter)s`.

2. Propagation des warnings Python  
   ```python
   import warnings, logging
   logging.captureWarnings(True)
   ```

3. Logs des bibliothèques tierces  
   Exemple : `logging.getLogger("urllib3").setLevel(logging.WARNING)`.

4. Mesures de temps  
   ```python
   t0 = perf_counter()
   ...  # étape
   log.info("Étape terminée en %.1fs", perf_counter() - t0)
   ```

5. Vérifier que le dossier logs est inscriptible au démarrage.

Avec cette configuration, tout incident critique atterrit dans `errors.log`, les détails complets restent dans `run.log`, et la console reste concise mais colorée.[{'index': 1}]