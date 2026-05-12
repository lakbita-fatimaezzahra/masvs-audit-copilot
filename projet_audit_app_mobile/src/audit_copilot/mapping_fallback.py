"""Mapping de fallback quand l'IA Gemini a des problèmes de quota"""
import json
from pathlib import Path
from .models import Finding, MappedFinding

def load_rules(path: str | None = None) -> dict:
    """Charge les règles de mapping depuis le fichier JSON"""
    if not path:
        path = str(Path(__file__).resolve().parent.parent.parent / "config" / "masvs_mastg.json")
    p = Path(path)
    if not p.exists(): return {}
    return json.loads(p.read_text(encoding="utf-8"))

def map_all_fallback(findings: list[Finding], kb: dict) -> list[MappedFinding]:
    """Mapping de fallback sans IA - basé sur des règles prédéfinies"""
    print("🔄 Utilisation du mapping de fallback (sans IA)...")
    
    mapped_findings = []
    
    for finding in findings:
        # Mapping basé sur des mots-clés dans le titre et détails
        title_lower = finding.title.lower()
        details_lower = finding.details.lower()
        
        # Règles de mapping simples
        if any(keyword in title_lower for keyword in ['hardcoded', 'secret', 'password', 'key']):
            maswe = "MASWE-001"
            masvs = "MASVS-CRYPTO-2"
            mastg = ["MASTG-ARCH-2", "MASTG-STORAGE-2"]
            recommendation = "Supprimer tous les secrets codés en dur et utiliser un gestionnaire de secrets sécurisé."
        elif any(keyword in title_lower for keyword in ['cleartext', 'http', 'traffic']):
            maswe = "MASWE-002"
            masvs = "MASVS-NETWORK-1"
            mastg = ["MASTG-ARCH-3", "MASTG-NETWORK-1"]
            recommendation = "Implémenter TLS/SSL pour toutes les communications réseau et désactiver le trafic en clair."
        elif any(keyword in title_lower for keyword in ['debug', 'debuggable']):
            maswe = "MASWE-003"
            masvs = "MASVS-RESILIENCE-1"
            mastg = ["MASTG-ARCH-8", "MASTG-TEST-1"]
            recommendation = "Désactiver le mode debug en production et utiliser les builds de release."
        elif any(keyword in title_lower for keyword in ['permission', 'storage', 'camera']):
            maswe = "MASWE-004"
            masvs = "MASVS-PLATFORM-2"
            mastg = ["MASTG-ARCH-1", "MASTG-STORAGE-1"]
            recommendation = "Vérifier que toutes les permissions demandées sont nécessaires et justifiées."
        elif any(keyword in title_lower for keyword in ['encryption', 'crypto', 'cipher']):
            maswe = "MASWE-005"
            masvs = "MASVS-CRYPTO-1"
            mastg = ["MASTG-ARCH-2", "MASTG-CRYPTO-1"]
            recommendation = "Utiliser des algorithmes de chiffrement forts et modernes (AES-256, RSA-2048+)."
        elif any(keyword in title_lower for keyword in ['webview', 'javascript']):
            maswe = "MASWE-006"
            masvs = "MASVS-PLATFORM-3"
            mastg = ["MASTG-ARCH-7", "MASTG-PLATFORM-3"]
            recommendation = "Désactiver JavaScript dans les WebView ou implémenter des contrôles de sécurité stricts."
        else:
            maswe = "MASWE-UNKNOWN"
            masvs = "MASVS-UNKNOWN"
            mastg = []
            recommendation = "Analyser manuellement cette vulnérabilité avec les outils de sécurité mobile."
        
        # Calcul du score basé sur la sévérité
        if finding.severity == 'high':
            score = 3
        elif finding.severity == 'medium':
            score = 2
        elif finding.severity == 'low':
            score = 1
        else:
            score = 0
        
        mapped_finding = MappedFinding(
            source=finding.source,
            title=finding.title,
            details=finding.details,
            severity=finding.severity,
            evidence=finding.evidence,
            tags=finding.tags,
            maswe=maswe,
            masvs=masvs,
            mastg_sections=mastg,
            recommendation=recommendation,
            score=score
        )
        
        mapped_findings.append(mapped_finding)
    
    print(f"✅ Mapping fallback complété: {len(mapped_findings)} findings mappés")
    return mapped_findings
