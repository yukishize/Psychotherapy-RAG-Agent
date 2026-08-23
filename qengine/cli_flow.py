from typing import Callable, Dict, List

from .models import Questionnaire
from .scorer import score_questionnaire
from .models import AssessmentProfile


def run_questionnaire(
    q: Questionnaire,
    ask: Callable[[str], str] = input,
) -> AssessmentProfile:
    print(f"\n=== {q.name} ===")
    if q.time_reference:
        print(f"（参考时间：{q.time_reference}）")

    answers: Dict[int, int] = {}

    for question in q.sorted_questions():
        print(f"\n[{question.seq}] {question.content}")
        for i, opt in enumerate(question.options, start=1):
            marker = "（反向）" if question.reverse else ""
            print(f"  {i}. {opt.desc}{marker}")
        while True:
            raw = ask(f"请选择 1-{len(question.options)} (输入 r 重看题目, q 退出): ").strip()
            if raw.lower() in ("q", "quit"):
                raise KeyboardInterrupt
            if raw.lower() in ("r", "review"):
                print(f"[{question.seq}] {question.content}")
                continue
            if raw.isdigit() and 1 <= int(raw) <= len(question.options):
                answers[question.seq] = int(raw) - 1
                break
            print("输入无效，请重试。")

    for extra in q.extra_questions:
        if not extra.options:
            continue
        print(f"\n[附加] {extra.content}")
        for i, opt in enumerate(extra.options, start=1):
            print(f"  {i}. {opt.desc}")
        while True:
            raw = ask(f"请选择 1-{len(extra.options)} (r 重看, q 跳过): ").strip()
            if raw.lower() in ("q", "quit"):
                break
            if raw.isdigit() and 1 <= int(raw) <= len(extra.options):
                break
            print("输入无效，请重试。")

    return score_questionnaire(q, answers)


def print_profile(profile: AssessmentProfile) -> None:
    print(f"\n===== 评估结果：{profile.name} =====")
    for r in profile.results:
        print(f"· {r.dimension}: {r.value} 分 → {r.level}")
        if r.description:
            print(f"    {r.description}")
    for alert in profile.alerts:
        print(f"[提示] {alert}")
    if profile.flags:
        print(f"[标记] {', '.join(profile.flags)}")
