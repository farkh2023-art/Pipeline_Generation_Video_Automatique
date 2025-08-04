Spécifier des bornes de version dans pyproject.toml (Poetry)
===========================================================

1. Emplacement  
Toutes les contraintes se placent sous :

```toml
[tool.poetry.dependencies]
```

ou, depuis Poetry 1.7, sous un groupe :

```toml
[tool.poetry.group.dev.dependencies]
```

2. Syntaxe PEP 440 reconnue par Poetry  
• >=1.2,<2.0 intervalle explicite  
• ^1.2.3   caret ⇒ >=1.2.3,<2.0.0  
• ~1.2.3   tilde ⇒ >=1.2.3,<1.3.0  
• 1.2.*   joker patch ⇒ >=1.2.0,<1.3.0  
• ==1.2.5  version exacte  
• !=1.2.8  exclusion

3. Exemples complets  

```toml
[tool.poetry.dependencies]
python       = ">=3.10,<3.13"        # borne haute pour anticiper les ruptures
torch        = { version = ">=2.2,<3.0",  extras = ["cuda"], optional = true }
tenacity     = "^8.2"                # >=8.2,<9.0
colorlog     = "~6.8"                # >=6.8,<6.9
requests     = ">=2.32,!=2.33.0"     # exclut une version boguée
```

4. Autoriser les pré-versions  
```toml
diffusers = { version = ">=0.27,<0.30", allow-prereleases = true }
```

5. Contraintes dépendantes de la plate-forme / Python  
```toml
pywin32 = { version = ">=306,<307", markers = "sys_platform == 'win32'" }
uvloop  = { version = "^0.19",       markers = "sys_platform != 'win32'" }
```

6. Extras optionnels  
Déclarez-les puis combinez avec les bornes :

```toml
[tool.poetry.extras]
gpu = ["torch"]

# Installation :
poetry install --extras gpu
```

7. Pourquoi fixer une borne haute ?  
• Bibliothèques à l’API instable (Torch, Stable-Diffusion).  
• Éviter qu’une future major *breaking* casse le pipeline sans prévenir.  
• Vous resterez malgré tout figé par `poetry.lock`, mais la CI détectera d’éventuels conflits avant qu’une mise à jour volontaire ne dépasse la borne.

8. Mettre à jour les bornes  
```bash
poetry add tenacity@^9.0    # élève la borne min → >=9.0,<10.0
poetry add torch@">=2.3,<4.0"
```
Le lockfile est régénéré automatiquement.

Récapitulatif rapide
--------------------
• Utilisez `>=min,<max` pour un contrôle total.  
• Utilisez `^` (caret) pour rester dans la même version majeure.  
• Combinez `extras`, `optional`, `markers` au besoin.  
• `poetry.lock` fige les versions précises ; les bornes servent à définir *où* vous acceptez de les faire évoluer.[{'index': 1}]