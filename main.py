import sys
from pathlib import Path

import click

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from agent.llm import LLMClient
from agent.prompts import CRISIS_TEXT
from agent.session import Session
from config import load_config
from qengine.cli_flow import print_profile, run_questionnaire
from qengine.registry import load_all
from qengine.scorer import score_questionnaire
from rag.embeddings import EmbeddingClient
from rag.store import VectorStore

QUICK_SCREEN = ["phq9", "gad7"]
HELP_TEXT = """可用命令：
  /quiz   重新进行问卷评估
  /help   显示本帮助
  /quit   退出"""


def select_questionnaires(registry: dict, ask=input):
    print("\n请选择评估方式：")
    print("  1. 快速筛查（PHQ-9 抑郁 + GAD-7 焦虑）")
    print("  2. 选择具体问卷")
    print("  3. 跳过评估，直接开始聊天")
    while True:
        choice = ask("请输入 1-3：").strip()
        if choice == "1":
            return [registry[qid] for qid in QUICK_SCREEN if qid in registry]
        if choice == "2":
            ids = sorted(registry)
            for i, qid in enumerate(ids, start=1):
                print(f"  {i}. {registry[qid].name}")
            while True:
                raw = ask("请输入问卷编号（可多个，用逗号分隔）：").strip()
                try:
                    picks = [int(x) for x in raw.replace("，", ",").split(",") if x.strip()]
                    if picks and all(1 <= x <= len(ids) for x in picks):
                        return [registry[ids[x - 1]] for x in picks]
                except ValueError:
                    pass
                print("输入无效，请重试。")
        if choice == "3":
            return []
        print("输入无效，请重试。")


def assess(questionnaires, ask=input):
    profiles = []
    for q in questionnaires:
        profile = run_questionnaire(q, ask=ask)
        print_profile(profile)
        profiles.append(profile)
        if "self_harm_risk" in profile.flags:
            print("\n" + CRISIS_TEXT)
    return profiles


def load_store(cfg):
    index_path = Path(cfg["index_path"])
    if not index_path.exists():
        return None
    return VectorStore.load(index_path, cfg["index_npz"])


def chat_loop(session: Session, ask=input):
    print("\n评估完成，可以开始聊天了。输入 /help 查看命令。")
    while True:
        try:
            text = ask("\n你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见，照顾好自己。")
            return False
        if not text:
            continue
        if text == "/quit":
            print("再见，照顾好自己。")
            return False
        if text == "/help":
            print(HELP_TEXT)
            continue
        if text == "/quiz":
            return True
        print("agent: ", end="", flush=True)
        try:
            for chunk in session.reply(text):
                print(chunk, end="", flush=True)
            print()
        except Exception as e:
            print(f"\n[调用失败] {e}")
            print("请检查 config.yaml 中的 LLM 配置与 API key。")


@click.command()
@click.option("--config", default="config.yaml", show_default=True)
def main(config: str) -> None:
    cfg = load_config(config)
    chat_cfg = cfg["llm"]["chat"]
    embed_cfg = cfg["llm"]["embedding"]

    registry = load_all(cfg["questionnaire_dir"])
    print("=== 心理治疗 Agent ===")
    print("本工具提供心理状态评估与基于知识的陪伴式对话，不替代专业诊断。")

    profiles = assess(select_questionnaires(registry))

    store = load_store(cfg)
    if store is None:
        print("\n[提示] 未找到索引文件，请先运行：py -3 -m rag.build_index 以启用 RAG 检索。")

    if not chat_cfg["api_key"] or not chat_cfg["model"]:
        print("\n[提示] 尚未配置 chat LLM（config.yaml 的 llm.chat 或 .env 中的 API key / model）。")
        print("配置后重新运行即可聊天；评估功能不受影响。")
        return

    embedding_client = None
    if embed_cfg["api_key"] and embed_cfg["model"]:
        embedding_client = EmbeddingClient(
            base_url=embed_cfg["base_url"], api_key=embed_cfg["api_key"], model=embed_cfg["model"]
        )

    llm = LLMClient(
        base_url=chat_cfg["base_url"],
        api_key=chat_cfg["api_key"],
        model=chat_cfg["model"],
        temperature=chat_cfg.get("temperature", 0.8),
    )
    session = Session(llm, store, embedding_client, profiles)

    while True:
        requiz = chat_loop(session)
        if not requiz:
            return
        profiles = assess(select_questionnaires(registry))
        session.update_profiles(profiles)


if __name__ == "__main__":
    main()
