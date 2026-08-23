from typing import Dict

from .models import AssessmentProfile, Questionnaire, ScoreResult


def _question_value(q: Questionnaire, seq: int, answer_index: int) -> int:
    question = q.questions[seq]
    option = question.options[answer_index]
    value = option.score
    if question.reverse:
        scores = [o.score for o in question.options]
        value = (max(scores) + min(scores)) - value
    return value


def _transform(q: Questionnaire, dimension_name: str, value: float) -> float:
    scoring_method = q.meta.get("scoring_method")
    if isinstance(scoring_method, dict) and scoring_method.get("type") == "percent":
        max_score = float(scoring_method.get("max_score", 100))
        if max_score > 0:
            return round(value / max_score * 100)
    transform = q.meta.get("scoring_transform")
    if isinstance(transform, dict) and transform.get("type") == "linear":
        factor = float(transform.get("factor", 1.0))
        value = value * factor
        if transform.get("round", False):
            value = round(value)
    return value


def score_questionnaire(q: Questionnaire, answers: Dict[int, int]) -> AssessmentProfile:
    profile = AssessmentProfile(questionnaire_id=q.id, name=q.name)

    raw_by_dim: Dict[str, float] = {}
    for dim in q.dimensions:
        values = [_question_value(q, seq, answers[seq]) for seq in dim.items if seq in answers]
        if not values:
            continue
        if dim.value_type == "mean":
            raw = round(sum(values) / len(values), 2)
        else:
            raw = sum(values)
        raw_by_dim[dim.name] = raw

        value = _transform(q, dim.name, raw)
        rules = q.scoring.get(dim.name, [])
        rule = next((r for r in rules if r.matches(value)), None)
        if rule is None:
            rule = max(rules, key=lambda r: r.hi) if rules else None
        if rule is not None:
            profile.results.append(
                ScoreResult(dimension=dim.name, value=value, level=rule.level, description=rule.description)
            )

    _check_special_items(q, answers, profile)
    return profile


def _check_special_items(q: Questionnaire, answers: Dict[int, int], profile: AssessmentProfile) -> None:
    critical = q.meta.get("critical_item")
    if critical is not None and int(critical) in answers:
        value = _question_value(q, int(critical), answers[int(critical)])
        if value > 1:
            profile.flags.append("self_harm_risk")
            profile.alerts.append(
                f"关键项（题{critical}）得分 {value}>1，提示存在自伤/自残意念风险，需高度关注。"
            )

    lie = q.meta.get("lie_item")
    if lie is not None and int(lie) in answers:
        if answers[int(lie)] == 0:
            profile.flags.append("lie_suspicion")
            profile.alerts.append(
                f"测谎题（全局题号{lie}）被选为第一项，问卷结果存疑，建议择时重测。"
            )

    total_positive = q.meta.get("total_positive_threshold")
    if total_positive is not None:
        threshold = float(q.meta.get("positive_item_threshold", 2))
        positive_count = sum(1 for seq, idx in answers.items() if _question_value(q, seq, idx) >= threshold)
        if positive_count > int(total_positive):
            profile.flags.append("positive_symptoms")
            profile.alerts.append(f"阳性项目数 {positive_count} > {total_positive}，提示存在阳性症状。")
