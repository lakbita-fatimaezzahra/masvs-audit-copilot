#!/usr/bin/env python3
"""
Script de test pour l'intégration MOBSF
Ce script permet de tester les différentes fonctionnalités de la plateforme
"""

import os
import sys
import json
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.audit_copilot.mobsf_agent import MobSFAgent
from src.audit_copilot.pipeline import run_audit_pipeline
from src.audit_copilot.ingestors import ingest_mobsf_json

def test_mobsf_connection():
    """Test la connexion à MOBSF"""
    print("🔍 Test de connexion à MOBSF...")
    
    mobsf_url = os.getenv('MOBSF_URL', 'http://localhost:8000')
    mobsf_api_key = os.getenv('MOBSF_API_KEY')
    
    if not mobsf_api_key or mobsf_api_key == 'your_mobsf_api_key_here':
        print("❌ Clé API MOBSF non configurée. Veuillez configurer MOBSF_API_KEY dans .env")
        return False
    
    agent = MobSFAgent(mobsf_url=mobsf_url, api_key=mobsf_api_key)
    
    if agent.test_connection():
        print(f"✅ Connexion réussie à MOBSF ({mobsf_url})")
        return True
    else:
        print(f"❌ Impossible de se connecter à MOBSF ({mobsf_url})")
        print("   Vérifiez que MOBSF est en cours d'exécution")
        return False

def test_gemini_connection():
    """Test la connexion à l'API Gemini"""
    print("\n🔍 Test de connexion à Gemini...")
    
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    
    if not gemini_api_key:
        print("❌ Clé API Gemini non configurée. Veuillez configurer GEMINI_API_KEY dans .env")
        return False
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content("Test connection")
        print("✅ Connexion réussie à Gemini API")
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion à Gemini: {e}")
        return False

def test_pipeline_with_sample_data():
    """Test le pipeline avec des données de test"""
    print("\n🔍 Test du pipeline avec données de test...")
    
    # Créer un fichier JSON de test MOBSF
    sample_mobsf_data = {
        "scan_summary": {
            "app_security_score": 65
        },
        "findings": [
            {
                "title": "Hardcoded Secret",
                "description": "Hardcoded API key found in source code",
                "severity": "high",
                "stat": "high"
            },
            {
                "title": "Cleartext Traffic",
                "description": "Application allows cleartext traffic",
                "severity": "medium",
                "stat": "warning"
            }
        ]
    }
    
    # Sauvegarder les données de test
    test_file = "test_mobsf_sample.json"
    with open(test_file, 'w') as f:
        json.dump(sample_mobsf_data, f, indent=2)
    
    try:
        # Tester l'ingestion
        findings = ingest_mobsf_json(test_file)
        print(f"✅ Ingestion réussie: {len(findings)} findings trouvés")
        
        # Nettoyer
        os.remove(test_file)
        return True
    except Exception as e:
        print(f"❌ Erreur lors du test du pipeline: {e}")
        if os.path.exists(test_file):
            os.remove(test_file)
        return False

def test_file_structure():
    """Vérifie la structure des fichiers"""
    print("\n🔍 Vérification de la structure des fichiers...")
    
    required_files = [
        'app.py',
        'requirements.txt',
        '.env',
        'src/audit_copilot/mobsf_agent.py',
        'src/audit_copilot/pipeline.py',
        'src/audit_copilot/ingestors.py',
        'templates/index.html'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Fichiers manquants: {', '.join(missing_files)}")
        return False
    else:
        print("✅ Structure des fichiers valide")
        return True

def test_dependencies():
    """Test les dépendances Python"""
    print("\n🔍 Vérification des dépendances...")
    
    required_modules = [
        'flask',
        'requests',
        'google.generativeai',
        'werkzeug',
        'dotenv'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Modules manquants: {', '.join(missing_modules)}")
        print("   Lancez: pip install -r requirements.txt")
        return False
    else:
        print("✅ Toutes les dépendances sont installées")
        return True

def main():
    """Fonction principale de test"""
    print("🚀 Démarrage des tests d'intégration MASVS Audit Copilot")
    print("=" * 60)
    
    tests = [
        ("Structure des fichiers", test_file_structure),
        ("Dépendances Python", test_dependencies),
        ("Connexion Gemini", test_gemini_connection),
        ("Connexion MOBSF", test_mobsf_connection),
        ("Pipeline avec données test", test_pipeline_with_sample_data),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur inattendue lors du test '{test_name}': {e}")
            results.append((test_name, False))
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Résultat: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés ! La plateforme est prête à être utilisée.")
        return 0
    else:
        print("⚠️ Certains tests ont échoué. Veuillez corriger les problèmes avant d'utiliser la plateforme.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
