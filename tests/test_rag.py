from pathlib import Path

import numpy as np
import pytest

from rag.loader import load_knowledge, parse_knowledge_file
from rag.retriever import search
from rag.store import Document, VectorStore

KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "rag" / "knowledge"


def test_retriever_metadata_filter():
    store = VectorStore()
    store.add(
        Document(
            id="t1",
            category="treatment",
            target="user",
            tags=["depression"],
            severity=["mild"],
            title="a",
            text="正念呼吸练习",
            embedding=np.array([1.0, 0.0], dtype="float32"),
        )
    )
    store.add(
        Document(
            id="s1",
            category="script",
            target="agent",
            tags=["depression"],
            severity=["severe"],
            title="b",
            text="自伤风险危机话术",
            embedding=np.array([0.0, 1.0], dtype="float32"),
        )
    )
    q = np.array([1.0, 0.0], dtype="float32")

    res = search(store, q, target="user", tags=["depression"], top_k=5)
    assert [d.id for d, _ in res] == ["t1"]

    res = search(store, q, target="agent", severities=["severe"], top_k=5)
    assert [d.id for d, _ in res] == ["s1"]

    res = search(store, q, severities=["mild"], top_k=5)
    assert [d.id for d, _ in res] == ["t1"]


def test_retriever_no_embedding_fallback():
    store = VectorStore()
    store.add(Document(id="x", category="treatment", target="user", tags=[], severity=[], title="", text="文本"))
    res = search(store, None, top_k=3)
    assert [d.id for d, _ in res] == ["x"]


def test_store_roundtrip(tmp_path):
    store = VectorStore()
    store.add(Document(id="x", category="treatment", target="user", tags=["a"], severity=["mild"], title="t", text="正文", embedding=np.array([0.1, 0.2], dtype="float32")))
    json_path = tmp_path / "index.json"
    npz_path = tmp_path / "index.npz"
    store.save(json_path, npz_path)
    loaded = VectorStore.load(json_path, npz_path)
    assert len(loaded.documents) == 1
    d = loaded.documents[0]
    assert d.id == "x" and d.text == "正文"
    assert d.embedding is not None and np.allclose(d.embedding, [0.1, 0.2])


def test_parse_knowledge_file_chunks():
    path = KNOWLEDGE_DIR / "treatment" / "_template.md"
    docs = parse_knowledge_file(path)
    assert len(docs) >= 3
    assert all("cbt" in d.id for d in docs)


def test_load_knowledge_skips_underscore_and_empty(tmp_path):
    treatment = tmp_path / "treatment"
    treatment.mkdir()
    (treatment / "_template.md").write_text(
        "---\nid: template_x\ncategory: treatment\ntarget: user\ntags: []\nseverity: []\n---\n\n# 模板\n\n## 内容\n模板占位\n",
        encoding="utf-8",
    )
    (treatment / "empty.md").write_text("", encoding="utf-8")
    (treatment / "normal.md").write_text(
        "---\nid: normal_x\ncategory: treatment\ntarget: user\ntags: [depression]\nseverity: [mild]\n---\n\n# 正常文档\n\n## 方法\n正念呼吸练习\n",
        encoding="utf-8",
    )
    docs = load_knowledge(tmp_path)
    assert docs
    assert all("normal_x" in d.id for d in docs)
    assert not any("template_x" in d.id for d in docs)


def test_load_knowledge_dedup_ids():
    from rag.loader import parse_knowledge_file

    docs = load_knowledge(KNOWLEDGE_DIR)
    ids = [d.id for d in docs]
    assert len(ids) == len(set(ids)), "文档 id 不应重复"


def test_load_knowledge_templates():
    docs = load_knowledge(KNOWLEDGE_DIR)
    assert docs
    assert all(d.text for d in docs)
    categories = {d.category for d in docs}
    targets = {d.target for d in docs}
    assert "treatment" in categories
    assert "script" in categories
    assert {"user", "agent"} <= targets
    assert not any("template" in d.id for d in docs)
