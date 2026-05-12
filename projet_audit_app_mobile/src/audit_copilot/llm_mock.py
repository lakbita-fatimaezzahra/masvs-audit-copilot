"""Mock pour l'IA Gemini quand la clé API est invalide"""
from typing import List
from .models import MappedFinding, AuditReport

def mock_deduplicate_findings(findings: List[MappedFinding]) -> List[MappedFinding]:
    """Mock de dédoublonnage"""
    print("🤖 Mock: Dédoublonnage simulé")
    return findings

def mock_generate_executive_summary(findings: List[MappedFinding]) -> str:
    """Mock de génération de résumé"""
    high_count = len([f for f in findings if f.severity == 'high'])
    medium_count = len([f for f in findings if f.severity == 'medium'])
    
    summary = f"""
    ## Résumé Exécutif (Mode Mock)
    
    L'analyse a révélé {len(findings)} vulnérabilités au total :
    - {high_count} vulnérabilités critiques
    - {medium_count} vulnérabilités moyennes
    
    **Recommandations principales :**
    1. Corriger les vulnérabilités critiques en priorité
    2. Mettre en place des contrôles de sécurité renforcés
    3. Effectuer des tests réguliers de sécurité
    
    *Note: Ceci est un résumé généré en mode démonstration*
    """
    return summary
