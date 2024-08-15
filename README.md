# Projet de Scraping, Reformulation, Filtrage et Traduction de Nouvelles

Ce projet automatise le scraping de nouvelles à partir de différents sites web, les reformule, les filtre, et les traduit avant de les stocker dans Google Drive. Il est basé sur l'utilisation de Selenium pour le scraping et utilise des modules Python pour la reformulation, le filtrage, et l'interaction avec Google Drive.

## Structure du Projet

- **`principale.py`** : Fichier principal qui orchestre les tâches quotidiennes de scraping, reformulation, filtrage, et sauvegarde.
- **`filtrage.py`** : Contient des fonctions pour filtrer les données obtenues lors du scraping.
- **`reformulation.py`** : Gère la reformulation des textes extraits.
- **`googledrive.py`** : Interagit avec Google Drive pour stocker les fichiers.
- **`script1_selenium.py` à `script20_selenium.py`** : Scripts Selenium pour le scraping de données à partir de différents sites web.
- **`scraping_news.py`** : Module lié au scraping des nouvelles.
- **`scraping_schedule.py`** : Planifie les tâches de scraping à exécuter périodiquement.
- **`import.ipynb`** : Notebook Jupyter contenant des imports et configurations.
- **`keyword.txt`** : Contient des mots-clés utilisés dans le processus de scraping ou de filtrage.
- **`information.py`** : Contient des informations générales ou des fonctions d'assistance.

## Fonctionnement

1. **Configuration de Selenium** : Le fichier principal utilise Selenium avec le navigateur Firefox en mode headless pour le scraping des sites web.

2. **Scraping des Nouvelles** : Le script principal (`principale.py`) est configuré pour exécuter quotidiennement les fonctions de scraping sur plusieurs sites web définis dans une liste. Chaque fonction de scraping est associée à une URL spécifique.

3. **Traitement des Données** : 
   - Les données extraites sont sauvegardées dans un fichier Excel.
   - Le fichier Excel est ensuite filtré en utilisant les fonctions du module `filtrage.py`.
   - Les données filtrées sont reformulées grâce aux fonctions du module `reformulation.py`.

4. **Sauvegarde et Téléversement** :
   - Les fichiers Excel traités sont supprimés du répertoire local.
   - Les fichiers finaux sont téléversés sur Google Drive à l'aide du module `googledrive.py`.

5. **Planification** : Le script `principale.py` utilise la bibliothèque `schedule` pour exécuter la tâche de scraping tous les jours à 00:02.

## Installation et Exécution

1. **Prérequis** :
   - Python 3.x
   - Les bibliothèques Python suivantes : `selenium`, `tqdm`, `pendulum`, etc.
   - [Geckodriver](https://github.com/mozilla/geckodriver/releases) pour Firefox.

2. **Installation des Dépendances** :
   Exécutez la commande suivante pour installer les dépendances :
   ```bash
   pip install -r requirements.txt
