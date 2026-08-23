from pathlib import Path

import pytest

from qengine.parser import parse_questionnaire
from qengine.scorer import score_questionnaire

DATA_DIR = Path(__file__).resolve().parent.parent / "questionaire"


def load(qid: str):
    return parse_questionnaire(DATA_DIR / f"{qid}.md")


def all_index(q, idx):
    return {q.questions[seq].seq: idx for seq in sorted(q.questions)}


def test_parse_all_questionnaires():
    for qid in ["gad7", "mental_health_12", "phq9", "sas", "scl90", "sds"]:
        q = load(qid)
        assert q.id == qid
        assert len(q.questions) > 0
        assert q.dimensions
        assert q.scoring


def test_sas_reverse_and_standard_score():
    q = load("sas")
    answers = all_index(q, 0)  # 全部选"无或很少"，正向1分/反向4分
    p = score_questionnaire(q, answers)
    total = p.results[0]
    assert total.dimension == "total"
    assert total.value == 44  # raw=35 -> round(35*1.25)=44
    assert total.level == "无焦虑"


def test_sas_high_score():
    q = load("sas")
    answers = all_index(q, 3)  # 全部选"总是"，正向4分/反向项反转为1分
    p = score_questionnaire(q, answers)
    total = p.results[0]
    assert total.value == 81  # raw=65 -> round(65*1.25)=81
    assert total.level == "重度焦虑"


def test_sds_percent_scoring():
    q = load("sds")
    answers = all_index(q, 0)  # 全部选"少有"
    p = score_questionnaire(q, answers)
    total = p.results[0]
    assert total.value == 62  # raw=50 -> round(50/80*100)=62
    assert total.level == "中度至重度抑郁"


def test_sds_normal():
    q = load("sds")
    answers = {}
    for seq, question in q.questions.items():
        answers[seq] = 3 if question.reverse else 0  # 反向项选"持续"(反转1分)，正向选"少有"(1分)
    p = score_questionnaire(q, answers)
    total = p.results[0]
    assert total.value == 25  # raw=20 -> round(20/80*100)=25
    assert total.level == "无抑郁"


def test_phq9_critical_and_lie():
    q = load("phq9")
    answers = all_index(q, 0)
    answers[9] = 2  # 项目9选"一半以上时间"（分值2）→ 自伤风险
    answers[14] = 0  # 测谎题选"符合" → 结果存疑
    p = score_questionnaire(q, answers)
    assert "self_harm_risk" in p.flags
    assert "lie_suspicion" in p.flags
    assert p.results[0].value == 2
    assert p.results[0].level == "无抑郁"


def test_gad7_total():
    q = load("gad7")
    answers = all_index(q, 0)
    p = score_questionnaire(q, answers)
    assert p.results[0].value == 0
    assert p.results[0].level == "无焦虑"
    assert len(q.extra_questions) == 1  # 附加题不计分


def test_scl90_factors_and_positive():
    q = load("scl90")
    answers = all_index(q, 2)  # 全部选"中度"（分值2）
    p = score_questionnaire(q, answers)
    by_dim = {r.dimension: r for r in p.results}
    assert by_dim["total"].value == 180
    assert by_dim["total"].level == "阳性"
    assert by_dim["somatization"].value == 2.0
    assert by_dim["somatization"].level == "轻度"
    assert "positive_symptoms" in p.flags


def test_scl90_factor_excludes_additional_items():
    q = load("scl90")
    answers = {seq: 0 for seq in q.questions}
    answers[19] = 4  # 附加题19（食欲）计入总分但不计入任何因子
    p = score_questionnaire(q, answers)
    by_dim = {r.dimension: r for r in p.results}
    assert by_dim["total"].value == 4
    for name in ["somatization", "depression", "anxiety", "hostility", "phobic_anxiety", "paranoid_ideation", "psychoticism", "interpersonal_sensitivity", "obsessive_compulsive"]:
        assert by_dim[name].value == 0.0


def test_mental_health_12_position_scoring():
    q = load("mental_health_12")
    answers = all_index(q, 0)  # 全部选第1项 → 0分
    p = score_questionnaire(q, answers)
    assert p.results[0].value == 0
    assert p.results[0].level == "正常"

    answers = all_index(q, 2)  # 全部选第3项 → 1分
    p = score_questionnaire(q, answers)
    assert p.results[0].value == 12
    assert p.results[0].level == "风险"
