# SFTP Auto Sync

Un petit outil Python pour synchroniser, analyser et valider des plugins pmmp via SFTP.  
Premier vrai projet Python, pour sortir de ma zone de confort.

---

## Objectif

- Se connecter automatiquement à un serveur via SFTP
- Récupérer les plugins d’un répertoire distant
- Vérifier qu’ils sont valides, qu’ils t’appartiennent, qu’ils sont sur GitHub, etc.
- Gérer ça proprement avec configuration YAML, .env

---

## Fonctionnalités

✅ Connexion SFTP automatique (avec retry, timeout, gestion des erreurs)  
✅ Analyse des plugins distante  
✅ Update des plugins via leur repository github `(clone, pull, etc.)`
✅ Intégration GitHub (via `plugin.yml` + token)  
✅ Logs stylés grâce à `rich`  
✅ Config YAML + .env pour garder ton code propre  
✅ Prise en compte des signals système (`Ctrl+C`) pour fermer proprement

---

## Dépendances

- `paramiko`
- `GitPython`
- `python-dotenv`
- `PyYAML`
- `rich`
- `pytest` pour les tests unitaires (bientôt)

Installe-les avec :

```bash
pip install -r requirements.txt