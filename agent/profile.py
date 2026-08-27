from typing import List, Optional

from qengine.models import AssessmentProfile

DIM_TAGS = {
    ("phq9", "phq9_total"): ["depression"],
    ("sds", "total"): ["depression"],
    ("gad7", "total"): ["anxiety"],
    ("sas", "total"): ["anxiety"],
    ("mental_health_12", "total"): ["general"],
    ("scl90", "somatization"): ["somatization"],
    ("scl90", "obsessive_compulsive"): ["obsessive_compulsive"],
    ("scl90", "interpersonal_sensitivity"): ["interpersonal"],
    ("scl90", "depression"): ["depression"],
    ("scl90", "anxiety"): ["anxiety"],
    ("scl90", "hostility"): ["hostility"],
    ("scl90", "phobic_anxiety"): ["phobia"],
    ("scl90", "paranoid_ideation"): ["paranoia"],
    ("scl90", "psychoticism"): ["psychoticism"],
}

NORMAL_LEVELS = ("无", "正常")


def severity_from_level(level: str) -> Optional[List[str]]:
    if any(k in level for k in NORMAL_LEVELS):
        return None
    if "中重度" in level:
        return ["severe", "moderate"]
    if "重度" in level:
        return ["severe"]
    if "中度" in level:
        return ["moderate"]
    if "风险" in level:
        return ["mild", "moderate"]
    if any(k in level for k in ("轻度", "轻微")):
        return ["mild"]
    return None


def profile_to_query(profiles: List[AssessmentProfile]):
    tags = set()
    severities = set()
    for p in profiles:
        for r in p.results:
            for t in DIM_TAGS.get((p.questionnaire_id, r.dimension), []):
                if not any(k in r.level for k in NORMAL_LEVELS):
                    tags.add(t)
            sev = severity_from_level(r.level)
            if sev:
                severities.update(sev)
    return (list(tags) or ["general"]), (list(severities) or None)


def profile_summary_text(profiles: List[AssessmentProfile]) -> str:
    lines = []
    for p in profiles:
        for r in p.results:
            lines.append(f"- {p.name} / {r.dimension}：{r.value} 分，等级【{r.level}】。{r.description}")
        for alert in p.alerts:
            lines.append(f"- [提示] {alert}")
    return "\n".join(lines) or "（暂无评估数据）"
