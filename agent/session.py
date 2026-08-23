from typing import Iterator, List, Optional

from qengine.models import AssessmentProfile
from rag.embeddings import EmbeddingClient
from rag.retriever import search
from rag.store import VectorStore

from .llm import LLMClient
from .prompts import build_system_prompt

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


class Session:
    def __init__(
        self,
        llm: LLMClient,
        store: Optional[VectorStore],
        embedding_client: Optional[EmbeddingClient],
        profiles: List[AssessmentProfile],
    ):
        self.llm = llm
        self.store = store
        self.embedding_client = embedding_client
        self.profiles = profiles
        self.messages: List[dict] = []
        self.self_harm = any("self_harm_risk" in p.flags for p in profiles)
        self.tags, self.severities = profile_to_query(profiles)

    def update_profiles(self, profiles: List[AssessmentProfile]) -> None:
        self.profiles = profiles
        self.self_harm = any("self_harm_risk" in p.flags for p in profiles)
        self.tags, self.severities = profile_to_query(profiles)
        self.messages = []

    def _retrieve(self, user_text: str):
        script_text = ""
        treatment_text = ""
        if self.store and self.store.documents:
            query_emb = None
            if self.embedding_client is not None:
                try:
                    query_emb = self.embedding_client.embed([user_text])[0]
                except Exception:
                    query_emb = None
            kwargs = {"tags": self.tags, "severities": self.severities}
            scripts = search(self.store, query_emb, target="agent", top_k=3, **kwargs)
            treats = search(self.store, query_emb, target="user", top_k=3, **kwargs)
            script_text = "\n\n".join(d.text for d, _ in scripts)
            treatment_text = "\n\n".join(d.text for d, _ in treats)
        return script_text, treatment_text

    def reply(self, user_text: str) -> Iterator[str]:
        script_text, treatment_text = self._retrieve(user_text)
        system = build_system_prompt(
            profile_summary_text(self.profiles), script_text, treatment_text, self.self_harm
        )
        self.messages = [m for m in self.messages if m["role"] != "system"]
        history = self.messages[-16:]
        self.messages = [{"role": "system", "content": system}] + history
        self.messages.append({"role": "user", "content": user_text})
        return self.llm.chat(self.messages)
