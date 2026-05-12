# MASVS/MASTG Audit Copilot - Documentation 

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.x-lightgrey.svg)
![Gemini](https://img.shields.io/badge/AI-Gemini_2.5_Flash-orange.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**Plateforme d'Audit de Sécurité Mobile Automatisée** - Transforme les analyses brutes en rapports professionnels conformes OWASP MASVS/MASTG

---

##  Table des Matières

1. [Vue d'ensemble](#-vue-densemble)
2. [Architecture Technique](#-architecture-technique)
3. [Installation Complète](#-installation-complète)
4. [Commandes Utilitaires](#-commandes-utilitaires)
5. [Guide d'Utilisation](#-guide-dutilisation)
6. [Configuration Avancée](#-configuration-avancée)
7. [Dépannage](#-dépannage)
8. [API Documentation](#-api-documentation)
9. [Contributions](#-contributions)

---

##  Vue d'ensemble

### Mission
Automatiser et standardiser l'audit de sécurité mobile en transformant les résultats bruts d'outils SAST/DAST en rapports exploitables conformes aux standards OWASP.

### Cas d'Usage
- **Entreprises** : Intégration CI/CD pour audits automatiques
- **Consultants** : Génération rapide de rapports clients
- **Développeurs** : Validation sécurité avant déploiement
- **Pentesters** : Standardisation des findings

---

##  Architecture Technique

### Stack Technologique
```
Frontend: HTML5 + TailwindCSS + JavaScript
Backend: Python 3.10+ + Flask
IA: Google Gemini 2.5 Flash
Analyse: MOBSF (Docker)
Base: JSON local (MASVS/MASTG)
```

### Flux de Données
```
APK/Scan → Pipeline d'Ingestion → IA (Mapping/Scoring) → Rapport HTML/JSON
```

### Composants Principaux
- **Pipeline Central** (`src/audit_copilot/pipeline.py`)
- **Agents d'Ingestion** (`ingestors.py`, `mobsf_agent.py`)
- **Moteur IA** (`mapping.py`, `llm.py`, `scoring.py`)
- **Modèles de Données** (`models.py`)

---

##  Installation Complète

### Prérequis Système
```bash
# Vérification Python
python --version  # >= 3.10

# Vérification Docker
docker --version  # >= 20.10

# Mémoire RAM recommandée
# Minimum: 4GB
# Optimal: 8GB+
```

### 1. Clonage et Dépendances
```bash
# Cloner le projet
git clone <repository-url>
cd projet_audit_app_mobile

# Créer environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installation des dépendances
pip install -r requirements.txt
```

### 2. Configuration Docker MOBSF
```bash
# Lancement MOBSF (mode détaché)
docker run -d -p 8000:8000 --name mobsf opensecurity/mobile-security-framework-mobsf

# Vérification du statut
docker ps | grep mobsf

# Logs MOBSF (optionnel)
docker logs -f mobsf
```

### 3. Configuration Variables d'Environnement
```bash
# Création du fichier .env
cat > .env << EOF
# Configuration IA Gemini
GEMINI_API_KEY=votre_clé_api_gemini_ici

# Configuration MOBSF
MOBSF_URL=http://localhost:8000
MOBSF_API_KEY=votre_clé_api_mobsf_ici

# Configuration Flask
FLASK_ENV=development
FLASK_DEBUG=True
EOF
```

**Obtention Clés API :**
- **Gemini** : [Google AI Studio](https://aistudio.google.com/)
- **MOBSF** : `http://localhost:8000` → Tools → API Key

---

##  Commandes Utilitaires

### Gestion des Services
```bash
# Démarrage complet (MOBSF + Flask)
docker start mobsf && python app.py

# Arrêt des services
docker stop mobsf
# Ctrl+C pour Flask

# Redémarrage MOBSF
docker restart mobsf
```

### Tests et Validation
```bash
# Test API Gemini
python test_gemini_api.py

# Test d'intégration complet
python test_integration.py

# Test avec APK réel
python test_real_apk.py

# Test IA isolé
python test_ai.py
```

### Maintenance
```bash
# Nettoyage conteneurs Docker
docker system prune -f

# Mise à jour dépendances
pip install -r requirements.txt --upgrade

# Logs application
tail -f flask.log  # si configuré
```

### Développement
```bash
# Mode debug Flask
export FLASK_DEBUG=True
python app.py

# Rechargement automatique
pip install watchdog
python app.py  # support auto-reload
```

---

##  Guide d'Utilisation

### Démarrage Rapide
```bash
# 1. Démarrer MOBSF
docker run -d -p 8000:8000 opensecurity/mobile-security-framework-mobsf

# 2. Démarrer l'application
python app.py

# 3. Accéder à l'interface
# http://localhost:5000
```

### Mode 1 : Analyse APK Directe (Recommandé)
```bash
# Via interface web:
# 1. Sélectionner "Analyse APK Directe"
# 2. Uploader fichier APK
# 3. Cliquer "Lancer l'Audit"
# 4. Attendre traitement automatique

# Via API (optionnel):
curl -X POST -F "apk=@app.apk" -F "project_name=Test" http://localhost:5000/audit
```

### Mode 2 : Import Rapports Externes
```bash
# Fichiers supportés:
# - MobSF JSON (v4.x)
# - JADX export texte
# - Burp Suite logs

# Via interface web:
# 1. Sélectionner "Import Rapports Externes"
# 2. Uploader fichiers correspondants
# 3. Lancer l'audit
```

### Résultats Obtenus
- **Rapport HTML** : Dashboard interactif avec graphiques
- **Données JSON** : Structuré pour intégration CI/CD
- **Métriques** : Scores de risque, priorisation P1-P4
- **Recommandations** : Actions correctives détaillées

---

##  Configuration Avancée

### Personnalisation Mapping
```python
# Dans config/masvs_mastg.json
{
  "custom_mappings": {
    "Cleartext Traffic": {
      "maswe": "MASWE-CRYPTO-1",
      "masvs": ["MASVS-CRYPTO-1"],
      "mastg": ["MASTG-TEST-0045"]
    }
  }
}
```

### Configuration Scoring
```python
# Dans src/audit_copilot/scoring.py
RISK_WEIGHTS = {
    "impact": 0.4,
    "exploitability": 0.3,
    "exposure": 0.3
}
```

### Limites et Performance
```python
# Dans app.py
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
REQUEST_TIMEOUT = 300  # 5 minutes
```

### Intégration CI/CD
```yaml
# .github/workflows/security-audit.yml
name: Security Audit
on: [push]
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Security Audit
        run: |
          docker run -d -p 8000:8000 mobsf
          python app.py &
          curl -X POST -F "apk=@app.apk" http://localhost:5000/audit
```

---

##  Dépannage

### Erreurs Communes

#### MOBSF Connexion Failed
```bash
# Diagnostic
curl -I http://localhost:8000
docker ps | grep mobsf
docker logs mobsf | tail -20

# Solutions
docker restart mobsf
# ou
docker run -d -p 8000:8000 --name mobsf-new opensecurity/mobile-security-framework-mobsf
```

#### API Gemini Quota
```bash
# Test quota
python test_gemini_api.py

# Solutions
# 1. Attendre reset quota (1h pour free tier)
# 2. Upgrader plan Gemini
# 3. Utiliser fallback mapping
```

#### Mapping Errors
```bash
# Vérifier configuration
cat .env | grep GEMINI
cat config/masvs_mastg.json | head -20

# Debug mode
export FLASK_DEBUG=True
python app.py
```

#### Performance Issues
```bash
# Monitoring ressources
docker stats mobsf
htop  # CPU/RAM usage

# Optimisation
# 1. Limiter taille APK
# 2. Utiliser batch processing
# 3. Cache results
```

### Logs et Debug
```bash
# Logs application
tail -f /var/log/flask/app.log

# Logs MOBSF
docker logs -f mobsf

# Mode verbose
export FLASK_ENV=development
python app.py --verbose
```

---

##  API Documentation

### Endpoints Principaux

#### POST /audit
```bash
# Analyse APK
curl -X POST \
  -F "apk=@app.apk" \
  -F "project_name=MonApp" \
  http://localhost:5000/audit

# Import rapports
curl -X POST \
  -F "mobsf=@report.json" \
  -F "project_name=MonApp" \
  http://localhost:5000/audit
```

#### GET /reports/{filename}
```bash
# Télécharger rapport HTML
curl -O http://localhost:5000/reports/report.html

# Télécharger données JSON
curl -O http://localhost:5000/reports/report.json
```

### Réponses API
```json
{
  "status": "success",
  "findings_count": 15,
  "files": {
    "html": "reports/report.html",
    "json": "reports/report.json"
  },
  "metrics": {
    "p1": 2,
    "p2": 5,
    "p3": 6,
    "p4": 2,
    "coverage": "87.5%"
  }
}
```

---

##  Contributions

### Développement Local
```bash
# Installation dev dependencies
pip install -r requirements-dev.txt

# Linting
flake8 src/
black src/

# Tests
pytest tests/
coverage run -m pytest
```

### Soumission Contributions
1. Forker le projet
2. Créer branche feature
3. Commits avec messages clairs
4. Pull request avec description

### Standards de Code
- Python PEP 8
- Comments docstrings
- Tests unitaires
- Documentation mise à jour

---


##  License

MIT License - Voir fichier `LICENSE` pour détails

---

**Développé  pour la communauté de sécurité mobile**

*Version: 3.0.0 | Dernière mise à jour: $(date)*
