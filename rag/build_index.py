import sys

import click

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from config import load_config
from rag.embeddings import EmbeddingClient
from rag.loader import load_knowledge
from rag.store import VectorStore


@click.command()
@click.option("--config", default="config.yaml", show_default=True)
def build_index(config: str) -> None:
    cfg = load_config(config)
    embed = cfg["llm"]["embedding"]
    knowledge_dir = cfg["knowledge_dir"]
    index_path = cfg["index_path"]
    npz_path = cfg["index_npz"]

    docs = load_knowledge(knowledge_dir)
    if not docs:
        click.echo("未在知识库目录中找到任何 .md 文档，请先填充 rag/knowledge/。")
        return

    if not embed["api_key"] or not embed["model"]:
        click.echo("未配置 embedding（config.yaml 的 llm.embedding 或 .env 中的 API key / model）。")
        return

    click.echo(f"加载 {len(docs)} 个分块，开始生成向量...")
    client = EmbeddingClient(base_url=embed["base_url"], api_key=embed["api_key"], model=embed["model"])
    batch_size = 32
    store = VectorStore()
    for i in range(0, len(docs), batch_size):
        batch = docs[i : i + batch_size]
        embs = client.embed([d.text for d in batch])
        for doc, emb in zip(batch, embs):
            doc.embedding = emb
            store.add(doc)
        click.echo(f"  已完成 {min(i + batch_size, len(docs))}/{len(docs)}")

    store.save(index_path, npz_path)
    click.echo(f"索引已保存: {index_path} (+ {npz_path})")


if __name__ == "__main__":
    build_index()
