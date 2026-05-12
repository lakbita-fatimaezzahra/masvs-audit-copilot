import json
from collections import Counter
from pathlib import Path
from .models import AuditReport

def _generate_html(report: AuditReport) -> str:
    rows = []
    for f in sorted(report.findings, key=lambda x: x.score, reverse=True):
        p_color = {"P1": "#ef4444", "P2": "#f59e0b", "P3": "#3b82f6", "P4": "#10b981"}.get(f.priority, "#6b7280")
        
        mastg_badges = "".join([f'<span class="badge badge-mastg">{s}</span>' for s in f.mastg_sections])
        
        rows.append(f"""
            <tr>
                <td><span class="priority-dot" style="background-color: {p_color}"></span>{f.priority}</td>
                <td class="text-center font-bold">{f.score}</td>
                <td>
                    <div class="finding-title">{f.title}</div>
                    <div class="finding-source">{f.source}</div>
                </td>
                <td><span class="badge badge-we">{f.maswe}</span></td>
                <td><span class="badge badge-vs">{f.masvs}</span></td>
                <td>{mastg_badges}</td>
                <td class="recommendation">{f.recommendation}</td>
            </tr>
        """)

    p1_count = report.metrics.get('priority_counts', {}).get('P1', 0)
    p2_count = report.metrics.get('priority_counts', {}).get('P2', 0)

    return f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Rapport Audit MASVS - {report.project_name}</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #2563eb;
            --bg: #f8fafc;
            --card: #ffffff;
            --text: #1e293b;
            --border: #e2e8f0;
        }}
        body {{ font-family: 'Plus Jakarta Sans', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 40px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: var(--card); padding: 48px; border-radius: 24px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }}
        h1 {{ font-size: 32px; font-weight: 800; margin-bottom: 8px; color: var(--primary); }}
        .subtitle {{ color: #64748b; margin-bottom: 40px; font-weight: 600; }}
        
        .summary-card {{ background: #f1f5f9; padding: 24px; border-radius: 16px; border-left: 6px solid var(--primary); margin-bottom: 40px; line-height: 1.6; font-size: 18px; }}
        
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 24px; margin-bottom: 48px; }}
        .stat-box {{ background: white; border: 1px solid var(--border); padding: 24px; border-radius: 16px; text-align: center; }}
        .stat-val {{ font-size: 36px; font-weight: 800; color: var(--primary); }}
        .stat-label {{ font-size: 14px; font-weight: 600; color: #64748b; text-transform: uppercase; margin-top: 4px; }}
        
        table {{ width: 100%; border-collapse: collapse; margin-top: 24px; }}
        th {{ text-align: left; padding: 16px; border-bottom: 2px solid var(--border); color: #64748b; font-size: 12px; text-transform: uppercase; }}
        td {{ padding: 20px 16px; border-bottom: 1px solid var(--border); vertical-align: top; font-size: 14px; }}
        
        .priority-dot {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 8px; }}
        .finding-title {{ font-weight: 700; margin-bottom: 4px; }}
        .finding-source {{ font-size: 12px; color: #64748b; }}
        .badge {{ padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; display: inline-block; margin: 2px; }}
        .badge-we {{ background: #f1f5f9; color: #475569; }}
        .badge-vs {{ background: #dbeafe; color: #1e40af; }}
        .badge-mastg {{ background: #dcfce7; color: #166534; }}
        .recommendation {{ font-style: italic; color: #334155; }}
        .font-bold {{ font-weight: 800; }}
        .text-center {{ text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Rapport d'Audit Mobile</h1>
        <div class="subtitle">Analyse Standards MASVS / MASTG • {report.project_name}</div>
        
        <div class="summary-card">
            {report.executive_summary}
        </div>
        
        <div class="stats-grid">
            <div class="stat-box">
                <div class="stat-val">{len(report.findings)}</div>
                <div class="stat-label">Total Findings</div>
            </div>
            <div class="stat-box">
                <div class="stat-val" style="color: #ef4444;">{p1_count}</div>
                <div class="stat-label">Priorité P1</div>
            </div>
            <div class="stat-box">
                <div class="stat-val" style="color: #f59e0b;">{p2_count}</div>
                <div class="stat-label">Priorité P2</div>
            </div>
            <div class="stat-box">
                <div class="stat-val">{report.metrics.get('mapping_coverage', 0)}%</div>
                <div class="stat-label">Couverture Mapping</div>
            </div>
        </div>
        
        <h2>Registre des Vulnérabilités</h2>
        <table>
            <thead>
                <tr>
                    <th style="width: 100px;">Priorité</th>
                    <th style="width: 60px;">Score</th>
                    <th>Titre & Source</th>
                    <th>MASWE</th>
                    <th>MASVS</th>
                    <th>MASTG</th>
                    <th>Recommandation</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

def write_outputs(report: AuditReport, out_dir: str) -> dict:
    path = Path(out_dir)
    path.mkdir(parents=True, exist_ok=True)
    
    html_content = _generate_html(report)
    html_file = path / "report.html"
    html_file.write_text(html_content, encoding="utf-8")
    
    json_content = json.dumps(report.to_dict(), indent=2, ensure_ascii=False)
    json_file = path / "report.json"
    json_file.write_text(json_content, encoding="utf-8")
    
    return {
        "html": str(html_file),
        "json": str(json_file)
    }

def build_metrics(findings: list) -> dict:
    counts = Counter([f.priority for f in findings])
    mapped = sum(1 for f in findings if f.masvs != "MASVS-UNKNOWN")
    coverage = round((mapped / len(findings) * 100), 1) if findings else 0
    return {
        "priority_counts": dict(counts),
        "mapping_coverage": coverage
    }
