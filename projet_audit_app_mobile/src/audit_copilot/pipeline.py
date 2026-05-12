from typing import List
from .models import Finding, MappedFinding, AuditReport
from .ingestors import ingest_mobsf_json, ingest_jadx_export, ingest_burp_log
from .mapping import map_all, load_rules
from .scoring import score_all
from .llm import deduplicate_findings, generate_executive_summary
from .reporting import write_outputs, build_metrics

def run_audit_pipeline(project_name: str, 
                       mobsf_path: str = None, 
                       jadx_path: str = None, 
                       burp_path: str = None,
                       output_dir: str = "reports") -> dict:
    
    findings: List[Finding] = []
    
    if mobsf_path:
        findings.extend(ingest_mobsf_json(mobsf_path))
    if jadx_path:
        findings.extend(ingest_jadx_export(jadx_path))
    if burp_path:
        findings.extend(ingest_burp_log(burp_path))
        
    if not findings:
        return {"error": "Aucune vulnérabilité détectée ou fichiers invalides."}

    # 1. Mapping MASVS/MASTG
    kb = load_rules()
    mapped_findings = map_all(findings, kb)
    
    # 2. Scoring
    scored_findings = score_all(mapped_findings)
    
    # 3. AI Deduplication
    final_findings = deduplicate_findings(scored_findings)
    
    # 4. Metrics & Summary
    metrics = build_metrics(final_findings)
    summary = generate_executive_summary(final_findings)
    
    # 5. Report Object
    report = AuditReport(
        project_name=project_name,
        findings=final_findings,
        executive_summary=summary,
        metrics=metrics
    )
    
    # 6. Writing Output
    files = write_outputs(report, output_dir)
    
    return {
        "status": "success",
        "findings_count": len(final_findings),
        "files": files
    }
