from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

@dataclass
class Finding:
    source: str
    title: str
    details: str
    severity: str
    evidence: Any = None
    tags: List[str] = field(default_factory=list)

@dataclass
class MappedFinding(Finding):
    maswe: str = "MASWE-UNKNOWN"
    masvs: str = "MASVS-UNKNOWN"
    mastg_sections: List[str] = field(default_factory=list)
    recommendation: str = ""
    impact: int = 1
    exploitability: int = 1
    exposure: int = 1
    score: int = 1
    priority: str = "P4"

@dataclass
class AuditReport:
    project_name: str
    findings: List[MappedFinding] = field(default_factory=list)
    executive_summary: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)
