import os
from pathlib import Path

import pytest

from config import load_config


@pytest.fixture(autouse=True)
def _no_real_dotenv(monkeypatch):
    monkeypatch.setattr("config._load_dotenv", lambda p: None)


def _write_cfg(tmp_path, text):
    p = tmp_path / "config.yaml"
    p.write_text(text, encoding="utf-8")
    return p


def test_split_config(tmp_path, monkeypatch):
    monkeypatch.setenv("DEEPSEEK_KEY", "sk-chat")
    monkeypatch.setenv("SILICONFLOW_KEY", "sk-embed")
    cfg_path = _write_cfg(
        tmp_path,
        """
llm:
  chat:
    base_url: https://api.deepseek.com
    api_key_env: DEEPSEEK_KEY
    model: deepseek-v4-flash
    temperature: 0.7
  embedding:
    base_url: https://api.siliconflow.cn/v1
    api_key_env: SILICONFLOW_KEY
    model: BAAI/bge-m3
questionnaire_dir: questionaire
""",
    )
    cfg = load_config(str(cfg_path))
    chat = cfg["llm"]["chat"]
    embed = cfg["llm"]["embedding"]
    assert chat == {"base_url": "https://api.deepseek.com", "api_key": "sk-chat", "model": "deepseek-v4-flash", "temperature": 0.7}
    assert embed == {"base_url": "https://api.siliconflow.cn/v1", "api_key": "sk-embed", "model": "BAAI/bge-m3", "temperature": 0.8}
    assert cfg["questionnaire_dir"] == Path("questionaire")


def test_old_flat_config_compat(tmp_path, monkeypatch):
    monkeypatch.setenv("MY_KEY", "sk-old")
    cfg_path = _write_cfg(
        tmp_path,
        """
llm:
  base_url: https://api.deepseek.com
  api_key_env: MY_KEY
  chat_model: deepseek-v4-flash
  embedding_model: text-embedding-3-small
""",
    )
    cfg = load_config(str(cfg_path))
    chat = cfg["llm"]["chat"]
    embed = cfg["llm"]["embedding"]
    assert chat["base_url"] == "https://api.deepseek.com"
    assert chat["api_key"] == "sk-old"
    assert chat["model"] == "deepseek-v4-flash"
    assert embed["model"] == "text-embedding-3-small"
    assert embed["base_url"] == "https://api.deepseek.com"  # 回退到 chat base_url


def test_embedding_api_key_fallback_to_chat(tmp_path, monkeypatch):
    monkeypatch.setenv("ONLY_KEY", "sk-only")
    monkeypatch.delenv("EMBEDDING_API_KEY", raising=False)
    cfg_path = _write_cfg(
        tmp_path,
        """
llm:
  chat:
    base_url: https://api.deepseek.com
    api_key_env: ONLY_KEY
    model: deepseek-v4-flash
  embedding:
    base_url: https://api.siliconflow.cn/v1
    model: BAAI/bge-m3
""",
    )
    cfg = load_config(str(cfg_path))
    embed = cfg["llm"]["embedding"]
    assert embed["api_key"] == "sk-only"
    assert embed["base_url"] == "https://api.siliconflow.cn/v1"


def test_env_override(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "https://override.example.com")
    monkeypatch.setenv("CHAT_MODEL", "override-model")
    monkeypatch.setenv("MY_KEY2", "sk-x")
    cfg_path = _write_cfg(
        tmp_path,
        """
llm:
  chat:
    api_key_env: MY_KEY2
    model: ""
""",
    )
    cfg = load_config(str(cfg_path))
    chat = cfg["llm"]["chat"]
    assert chat["base_url"] == "https://override.example.com"
    assert chat["model"] == "override-model"


def test_temperature_default_and_invalid(tmp_path, monkeypatch):
    monkeypatch.setenv("K", "sk-x")
    cfg_path = _write_cfg(
        tmp_path,
        """
llm:
  chat:
    api_key_env: K
    temperature: not-a-number
""",
    )
    cfg = load_config(str(cfg_path))
    assert cfg["llm"]["chat"]["temperature"] == 0.8
    assert cfg["llm"]["embedding"]["temperature"] == 0.8


def test_api_key_env_literal_key_warns_and_falls_back(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-real")
    monkeypatch.delenv("sk-fake", raising=False)
    cfg_path = _write_cfg(
        tmp_path,
        """
llm:
  chat:
    api_key_env: "sk-fake-key-value"
    model: deepseek-v4-flash
""",
    )
    cfg = load_config(str(cfg_path))
    assert cfg["llm"]["chat"]["api_key"] == "sk-real"
    assert "[警告]" in capsys.readouterr().out
