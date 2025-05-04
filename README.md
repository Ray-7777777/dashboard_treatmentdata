# Dashboard Dentaire - Analyse des Données de Traitement

Ce projet est un tableau de bord interactif développé avec Streamlit permettant d’explorer et d’analyser des données de traitement dentaire issues d’un fichier CSV.

## Démarrage

### Prérequis

- Python 3.x
- pip
- Avoir le fichier DataScienceTreatmentData.csv dans le même répertoire que le code

### Installation

```bash
git clone https://github.com/Ray-7777777/dashboard-dentaire.git
cd dashboard-dentaire
pip install -r requirements.txt
streamlit run dashboard.py
```

L'application devrait s'ouvrir automatiquement dans votre navigateur à l'adresse :
http://localhost:8501

### Configuration
Placez votre fichier de données CSV dans le dossier racine et modifiez le nom dans dashboard.py ligne 507 si nécessaire :

python
dashboard = DentalTreatmentDashboard("votre_fichier.csv")
