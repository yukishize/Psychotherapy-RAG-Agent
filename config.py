import os
from pathlib import Path
from typing import Optional

import yaml


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def _read_section(
    raw: Optional[dict],
    prefix: str,
    api_key_env_default: str,
    chat_api_key: str = "",
    legacy_model_key: str = "",
    model_env: str = "",
) -> dict:
    raw = raw or {}
    base_url = raw.get("base_url") or os.getenv(f"{prefix}_BASE_URL", "")
    api_key_env = raw.get("api_key_env") or api_key_env_default
    if str(api_key_env).startswith("sk-"):
        print(
            f"[警告] {prefix} 的 api_key_env 看起来填的是密钥本身（以 sk- 开头），"
            f"应填环境变量名；已回退到默认变量名 {api_key_env_default}"
        )
        api_key_env = api_key_env_default
    api_key = os.getenv(api_key_env, "") or os.getenv("OPENAI_API_KEY", "")
    model = raw.get("model")
    if not model and legacy_model_key:
        model = raw.get(legacy_model_key)
    if not model:
        model = os.getenv(model_env, "")
    if not api_key and chat_api_key:
        api_key = chat_api_key
    temperature = raw.get("temperature", 0.8)
    try:
        temperature = float(temperature)
    except (TypeError, ValueError):
        temperature = 0.8
    return {"base_url": base_url, "api_key": api_key, "model": model or "", "temperature": temperature}


def load_config(path: str = "config.yaml") -> dict:
    cfg_path = Path(path)
    if cfg_path.exists():
        cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    else:
        cfg = {}
    _load_dotenv(Path(".env"))

    llm = cfg.get("llm") or {}

    if "chat" in llm and isinstance(llm.get("chat"), dict):
        chat = _read_section(
            llm["chat"], "LLM", "OPENAI_API_KEY", legacy_model_key="chat_model", model_env="CHAT_MODEL"
        )
        embedding = _read_section(
            llm.get("embedding"),
            "EMBEDDING",
            "EMBEDDING_API_KEY",
            chat_api_key=chat["api_key"],
            legacy_model_key="embedding_model",
            model_env="EMBEDDING_MODEL",
        )
    else:
        chat = _read_section(
            llm, "LLM", "OPENAI_API_KEY", legacy_model_key="chat_model", model_env="CHAT_MODEL"
        )
        embedding = _read_section(
            llm,
            "EMBEDDING",
            "EMBEDDING_API_KEY",
            chat_api_key=chat["api_key"],
            legacy_model_key="embedding_model",
            model_env="EMBEDDING_MODEL",
        )

    return {
        "llm": {"chat": chat, "embedding": embedding},
        "questionnaire_dir": Path(cfg.get("questionnaire_dir", "questionaire")),
        "knowledge_dir": Path(cfg.get("knowledge_dir", "rag/knowledge")),
        "index_path": cfg.get("index_path", "rag/index.json"),
        "index_npz": cfg.get("index_npz", "rag/index.npz"),
    }
