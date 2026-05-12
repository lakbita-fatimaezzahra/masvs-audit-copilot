import json
import re
from pathlib import Path
from typing import Any, List

from .models import Finding

def _safe_read(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def _map_mobsf_severity(stat: str) -> str:
    s = str(stat).lower()
    if s == "high":
        return "high"
    if s in ["warning", "medium"]:
        return "medium"
    if s in ["info", "secure"]:
        return "info"
    return "medium"

def _is_mobsf_finding(obj: Any) -> bool:
    if not isinstance(obj, dict):
        return False
    has_title = any(k in obj for k in ["title", "ruleid", "name", "issue", "msg", "pattern"])
    has_desc = any(k in obj for k in ["description", "desc", "details", "info", "stat", "severity", "level"])
    return has_title or (has_desc and len(obj) < 20)

def _item_to_finding(issue: dict, tag: str) -> Finding:
    title = (issue.get("title") or issue.get("issue") or issue.get("ruleid") or 
             issue.get("findings") or issue.get("name") or 
             issue.get("msg") or f"MobSF {tag.capitalize()} Finding")
    desc = issue.get("description") or issue.get("desc") or issue.get("info") or issue.get("details") or ""
    stat = issue.get("stat") or issue.get("severity") or issue.get("level") or "info"
    
    if "secret" in issue:
        title = "Hardcoded Secret found"
        desc = f"Secret: {issue['secret']}"
        stat = "high"

    return Finding(
        source="MobSF",
        title=str(title),
        details=str(desc),
        severity=_map_mobsf_severity(stat),
        evidence=issue,
        tags=[tag.lower()],
    )

def _extract_findings_recursively(data: Any, tag: str = "general") -> List[Finding]:
    findings = []
    if isinstance(data, list):
        for item in data:
            if _is_mobsf_finding(item):
                findings.append(_item_to_finding(item, tag))
            else:
                findings.extend(_extract_findings_recursively(item, tag))
    elif isinstance(data, dict):
        analysis_keys = {
            "manifest_analysis": "manifest", "certificate_analysis": "certificate",
            "binary_analysis": "binary", "code_analysis": "code",
            "static_analysis": "static", "niap_analysis": "niap",
            "file_analysis": "file", "dynamic_analysis": "dynamic", "findings": "general"
        }
        for key, val in data.items():
            current_tag = analysis_keys.get(key, tag)
            if _is_mobsf_finding(val):
                findings.append(_item_to_finding(val, current_tag))
            else:
                findings.extend(_extract_findings_recursively(val, current_tag))
    return findings

def ingest_mobsf_json(path: str) -> List[Finding]:
    content = _safe_read(path)
    if not content: return []
    try:
        data = json.loads(content)
        findings = []
        scan_summary = data.get("scan_summary", {})
        score = data.get("security_score") or scan_summary.get("app_security_score") or data.get("app_security_score")
        if score is not None:
            findings.append(Finding(source="MobSF", title="MobSF Security Score", details=f"Overall score: {score}", severity="info", evidence={"score": score}, tags=["score"]))
        
        findings.extend(_extract_findings_recursively(data))
        
        seen = set()
        unique_findings = []
        for f in findings:
            slug = f"{f.title.lower()}|{f.details.lower()}"
            if slug not in seen:
                unique_findings.append(f)
                seen.add(slug)
        return unique_findings
    except Exception:
        return []

def ingest_jadx_export(path: str) -> List[Finding]:
    text = _safe_read(path)
    if not text: return []
    findings = []
    patterns = [
        (r"(?i)hardcoded\s+api[_\s-]?key", "Hardcoded API key", "high", ["secrets"]),
        (r"(?i)allowBackup\s*=\s*true", "Android backup enabled", "medium", ["manifest"]),
        (r"(?i)usesCleartextTraffic\s*=\s*true", "Cleartext traffic allowed", "high", ["network"]),
        (r"(?i)webview.*setJavaScriptEnabled\s*\(\s*true", "WebView JavaScript enabled", "medium", ["webview"]),
    ]
    for pattern, title, severity, tags in patterns:
        for m in re.finditer(pattern, text):
            snippet = text[max(0, m.start() - 120) : m.end() + 120]
            findings.append(Finding(source="JADX", title=title, details=snippet.strip(), severity=severity, evidence={"match": m.group(0)}, tags=tags))
    return findings

def ingest_burp_log(path: str) -> List[Finding]:
    text = _safe_read(path)
    if not text: return []
    findings = []
    rules = [
        (r"(?i)http://", "Unencrypted endpoint observed", "high", ["network", "endpoint"]),
        (r"(?i)token=.*", "Token in URL or logs", "high", ["auth", "leak"]),
        (r"(?i)certificate\s+pinning\s+not\s+enforced", "Missing certificate pinning", "medium", ["tls"]),
    ]
    for pattern, title, severity, tags in rules:
        for m in re.finditer(pattern, text):
            snippet = text[max(0, m.start() - 120) : m.end() + 120]
            findings.append(Finding(source="Burp", title=title, details=snippet.strip(), severity=severity, evidence={"match": m.group(0)}, tags=tags))
    return findings
