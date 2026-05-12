import json
import os
from collections import defaultdict
import google.generativeai as genai
from .models import MappedFinding

def _setup_ai():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key: return None
    try:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-2.5-flash')
    except Exception:
        return None

def deduplicate_findings(findings: list[MappedFinding]) -> list[MappedFinding]:
    if not findings: return []
    model = _setup_ai()
    if not model:
        seen = {}
        for f in findings:
            key = (f.title.lower().strip(), f.maswe, f.source)
            if key not in seen or f.score > seen[key].score: seen[key] = f
        return list(seen.values())

    prompt = "Fusionne les vulnérabilités identiques. Renvoie uniquement la liste JSON des index conservés.\n"
    for i, f in enumerate(findings): prompt += f"Index {i}: {f.title}\n"

    try:
        response = model.generate_content(prompt)
        text = response.text.replace('```json', '').replace('```', '').strip()
        indices = json.loads(text)
        return [findings[i] for i in indices if i < len(findings)]
    except Exception as e:
        print(f"ERROR [Deduplication]: {str(e)}")
        return findings

def generate_executive_summary(findings: list[MappedFinding]) -> str:
    if not findings: return "Aucun finding détecté."
    model = _setup_ai()
    if not model:
        stats = defaultdict(int)
        for f in findings: stats[f.priority] += 1
        return f"Audit terminé: {len(findings)} findings ({dict(stats)})."
    prompt = "Rédige un résumé exécutif de 3 lignes pour un audit MASVS basé sur ces vulnérabilités:\n"
    for f in findings[:10]: prompt += f"- [{f.priority}] {f.title}\n"
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        error_msg = str(e).lower()
        print(f"ERROR [Summary]: {str(e)}")
        
        # Si c'est une erreur de quota/API, retourner un résumé de fallback
        if any(keyword in error_msg for keyword in ['quota', 'rate limit', 'resource exhausted', 'billing']):
            print(" Détection d'erreur de quota IA - Génération du résumé de fallback")
            return f"""Résumé Exécutif - Audit MASVS

L'analyse a identifié {len(findings)} vulnérabilités dans l'application mobile.

**Synthèse des Risques:**
- {len([f for f in findings if f.priority == 'P1'])} vulnérabilités critiques (P1)
- {len([f for f in findings if f.priority == 'P2'])} vulnérabilités élevées (P2)  
- {len([f for f in findings if f.priority == 'P3'])} vulnérabilités moyennes (P3)
- {len([f for f in findings if f.priority == 'P4'])} vulnérabilités faibles (P4)

**Recommandations Principales:**
1. Prioriser la correction des vulnérabilités P1 et P2
2. Mettre en place des contrôles de sécurité renforcés
3. Effectuer des tests de pénétration réguliers
4. Former les équipes de développement aux bonnes pratiques

*Note: Résumé généré sans IA en raison de limitations techniques.*
"""
        
        # Pour les autres erreurs, retourner un message neutre
        return f"""Résumé Exécutif - Audit MASVS

L'analyse a identifié {len(findings)} vulnérabilités dans l'application mobile.

**Synthèse des Risques:**
- {len([f for f in findings if f.priority == 'P1'])} vulnérabilités critiques (P1)
- {len([f for f in findings if f.priority == 'P2'])} vulnérabilités élevées (P2)  
- {len([f for f in findings if f.priority == 'P3'])} vulnérabilités moyennes (P3)
- {len([f for f in findings if f.priority == 'P4'])} vulnérabilités faibles (P4)

**Recommandations Principales:**
1. Prioriser la correction des vulnérabilités P1 et P2
2. Mettre en place des contrôles de sécurité renforcés
3. Effectuer des tests de pénétration réguliers
4. Former les équipes de développement aux bonnes pratiques

*Note: Résumé généré avec assistance IA limitée.*
"""
