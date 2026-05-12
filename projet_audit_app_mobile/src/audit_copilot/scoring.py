import json
import os
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

def score_all(findings: list[MappedFinding]) -> list[MappedFinding]:
    model = _setup_ai()
    if not model:
        for f in findings:
            f.score = 1; f.priority = "P4"
        return findings

    findings_list = [{"id": i, "title": f.title, "details": f.details[:200]} for i, f in enumerate(findings)]

    prompt = f"""Évalue la criticité de ces vulnérabilités mobiles (Impact, Exploitability, Exposure de 1 à 3).
Findings: {json.dumps(findings_list)}
Réponds UNIQUEMENT avec un tableau JSON d'objets: {{"id": int, "impact": 1-3, "exploitability": 1-3, "exposure": 1-3}}"""

    try:
        response = model.generate_content(prompt)
        text = response.text.replace('```json', '').replace('```', '').strip()
        results = json.loads(text)
        res_map = {r['id']: r for r in results if 'id' in r}

        for i, f in enumerate(findings):
            res = res_map.get(i, {"impact": 1, "exploitability": 1, "exposure": 1})
            f.impact = int(res.get("impact", 1))
            f.exploitability = int(res.get("exploitability", 1))
            f.exposure = int(res.get("exposure", 1))
            f.score = f.impact * f.exploitability * f.exposure
            f.priority = "P1" if f.score >= 18 else ("P2" if f.score >= 9 else ("P3" if f.score >= 4 else "P4"))
            
        return findings
    except Exception as e:
        print(f"ERROR [Scoring Batch]: {str(e)}")
        for f in findings: f.score = 1; f.priority = "P4"
        return findings
