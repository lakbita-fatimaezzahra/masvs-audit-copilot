import json
import os
from pathlib import Path
import google.generativeai as genai

from .models import Finding, MappedFinding

def load_rules(path: str | None = None) -> dict:
    if not path:
        path = str(Path(__file__).resolve().parent.parent.parent / "config" / "masvs_mastg.json")
    p = Path(path)
    if not p.exists(): return {}
    return json.loads(p.read_text(encoding="utf-8"))

def _setup_ai():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key: return None
    try:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-2.5-flash')
    except Exception:
        return None

def map_all(findings: list[Finding], kb: dict) -> list[MappedFinding]:
    model = _setup_ai()
    if not model or not kb:
        return [MappedFinding(**f.__dict__) for f in findings]

    # Préparation du prompt groupé
    findings_list = []
    for i, f in enumerate(findings):
        findings_list.append({"id": i, "title": f.title, "details": f.details[:200]})

    prompt = f"""Tu es un expert en sécurité mobile. Mappe ces vulnérabilités aux standards MASVS/MASTG.
Base de connaissance: {json.dumps(kb)}
Findings: {json.dumps(findings_list)}

Réponds UNIQUEMENT avec un tableau JSON d'objets contenant:
- "id": (l'ID fourni)
- "maswe": (le code MASWE)
- "masvs": (le code MASVS)
- "mastg_sections": (liste de codes MASTG)
- "recommendation": (texte clair)
"""

    try:
        response = model.generate_content(prompt)
        text = response.text.replace('```json', '').replace('```', '').strip()
        results = json.loads(text)
        
        mapped = []
        # Création d'un dictionnaire pour accès rapide
        res_map = {r['id']: r for r in results if 'id' in r}
        
        for i, f in enumerate(findings):
            res = res_map.get(i, {})
            mf = MappedFinding(
                **f.__dict__,
                maswe=res.get("maswe", "MASWE-UNKNOWN"),
                masvs=res.get("masvs", "MASVS-UNKNOWN"),
                mastg_sections=res.get("mastg_sections", []),
                recommendation=res.get("recommendation", "Analyser manuellement.")
            )
            mapped.append(mf)
        return mapped
        
    except Exception as e:
        error_msg = str(e).lower()
        print(f"ERROR [Mapping Batch]: {str(e)}")
        
        # Détecter les erreurs de quota/rate limit
        if any(keyword in error_msg for keyword in ['quota', 'rate limit', 'resource exhausted', 'billing']):
            print("🔄 Détection d'erreur de quota IA - Utilisation du mapping de fallback")
            # Utiliser le mapping de fallback sans IA
            from .mapping_fallback import map_all_fallback
            return map_all_fallback(findings, kb)
        else:
            return [MappedFinding(**f.__dict__, recommendation="Erreur lors du mapping.") for f in findings]
