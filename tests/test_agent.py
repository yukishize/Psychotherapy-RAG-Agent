from pathlib import Path

import numpy as np

from agent.prompts import build_system_prompt
from agent.session import Session, profile_to_query, profile_summary_text, severity_from_level
from qengine.models import AssessmentProfile, ScoreResult
from qengine.parser import parse_questionnaire
from qengine.scorer import score_questionnaire
from rag.store import Document, VectorStore

DATA_DIR = Path(__file__).resolve().parent.parent / "questionaire"


def make_profile(qid, dimension, value, level, desc="", flags=None):
    return AssessmentProfile(
        questionnaire_id=qid,
        name=qid,
        results=[ScoreResult(dimension=dimension, value=value, level=level, description=desc)],
        flags=flags or [],
    )


def test_severity_from_level():
    assert severity_from_level("无抑郁") is None
    assert severity_from_level("正常") is None
    assert severity_from_level("轻度焦虑") == ["mild"]
    assert severity_from_level("中度抑郁") == ["moderate"]
    assert severity_from_level("中重度抑郁") == ["severe", "moderate"]
    assert severity_from_level("重度焦虑") == ["severe"]
    assert severity_from_level("风险") == ["mild", "moderate"]


def test_profile_to_query_combines_tags():
    profiles = [
        make_profile("phq9", "phq9_total", 12, "中度抑郁"),
        make_profile("gad7", "total", 6, "轻度焦虑"),
        make_profile("scl90", "somatization", 1.0, "正常"),  # 正常不计入
    ]
    tags, severities = profile_to_query(profiles)
    assert set(tags) == {"depression", "anxiety"}
    assert set(severities) == {"moderate", "mild"}


def test_profile_to_query_normal_falls_back_general():
    profiles = [make_profile("phq9", "phq9_total", 2, "无抑郁")]
    tags, severities = profile_to_query(profiles)
    assert tags == ["general"]
    assert severities is None


def test_profile_summary_text():
    p = make_profile("phq9", "phq9_total", 12, "中度抑郁", "建议咨询心理医生")
    text = profile_summary_text([p])
    assert "中度抑郁" in text and "建议咨询心理医生" in text


def test_build_system_prompt_with_self_harm():
    prompt = build_system_prompt("画像摘要", "话术指引", "治疗方法池", self_harm_risk=True)
    assert "12356" in prompt
    safety_block = prompt.split("【安全优先】")[1]
    assert "不要推荐任何自愈方法" in safety_block


def test_phq9_to_profile_integration():
    q = parse_questionnaire(DATA_DIR / "phq9.md")
    answers = {seq: 1 for seq in q.questions}  # 前 9 项各 1 分 → 总分 9，轻微抑郁
    answers[9] = 2
    answers[14] = 0  # 测谎题选第一项"符合"
    p = score_questionnaire(q, answers)
    tags, severities = profile_to_query([p])
    assert "depression" in tags
    assert "self_harm_risk" in p.flags
    assert "lie_suspicion" in p.flags


class FakeLLM:
    def __init__(self):
        self.last_messages = None

    def chat(self, messages):
        self.last_messages = messages
        return iter(["（模拟回复）"])


class FakeEmbedding:
    def embed(self, texts):
        return np.ones((len(texts), 4), dtype="float32")


def test_session_reply_retrieves_and_prompts():
    store = VectorStore()
    store.add(Document(id="s1", category="script", target="agent", tags=["depression"], severity=["mild"], title="话术", text="敏感点：避免说教", embedding=np.ones(4, dtype="float32")))
    store.add(Document(id="t1", category="treatment", target="user", tags=["depression"], severity=["mild"], title="方法", text="正念呼吸练习", embedding=np.ones(4, dtype="float32")))

    profiles = [make_profile("phq9", "phq9_total", 6, "轻度抑郁")]
    llm = FakeLLM()
    session = Session(llm, store, FakeEmbedding(), profiles)
    chunks = list(session.reply("我今天很难受"))
    assert chunks == ["（模拟回复）"]
    assert llm.last_messages
    system = llm.last_messages[0]["content"]
    assert "轻度抑郁" in system
    assert "敏感点：避免说教" in system
    assert "正念呼吸练习" in system
    assert llm.last_messages[-1]["content"] == "我今天很难受"


def test_session_self_harm_prompt_injected():
    store = VectorStore()
    profiles = [make_profile("phq9", "phq9_total", 10, "中度抑郁", flags=["self_harm_risk"])]
    llm = FakeLLM()
    session = Session(llm, store, None, profiles)
    list(session.reply("我有点想不开"))
    system = llm.last_messages[0]["content"]
    assert "12356" in system
    assert "不要推荐任何自愈方法" in system


def test_build_system_prompt_anti_mechanical_rules():
    prompt = build_system_prompt("画像摘要", "话术指引", "方法池", self_harm_risk=False)
    assert "每轮不要重复相同的句式" in prompt
    assert "禁止照搬" in prompt
    assert "不要每轮都以提问结尾" in prompt
    assert "回复控制在 2-4 句" in prompt
    assert "开头不要总是情绪反射式" in prompt
