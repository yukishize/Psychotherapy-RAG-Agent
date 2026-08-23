import re
from pathlib import Path
from typing import List

import yaml

from .store import Document

_FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)


def _split_sections(body: str) -> List[str]:
    lines = body.splitlines()
    sections: List[str] = []
    current: List[str] = []
    for line in lines:
        if line.startswith("##"):
            if current:
                sections.append("\n".join(current).strip())
                current = []
        current.append(line)
    if current:
        sections.append("\n".join(current).strip())
    return [s for s in sections if s.strip()]


def parse_knowledge_file(path: Path) -> List[Document]:
    text = Path(path).read_text(encoding="utf-8")
    m = _FRONT_MATTER_RE.match(text)
    if not m:
        raise ValueError(f"{path} 缺少 YAML frontmatter")
    meta = yaml.safe_load(m.group(1)) or {}
    body = text[m.end():].strip()

    doc_id = str(meta.get("id") or path.stem)
    category = str(meta.get("category", "treatment"))
    target = str(meta.get("target", "user"))
    tags = [str(t) for t in meta.get("tags", [])]
    severity = [str(s) for s in meta.get("severity", [])]
    title = str(meta.get("title") or path.stem)

    sections = _split_sections(body)
    if not sections:
        return []

    docs: List[Document] = []
    for i, sec in enumerate(sections, start=1):
        docs.append(
            Document(
                id=f"{doc_id}#{i}",
                category=category,
                target=target,
                tags=tags,
                severity=severity,
                title=title,
                text=sec,
            )
        )
    return docs


def load_knowledge(directory: Path) -> List[Document]:
    docs: List[Document] = []
    if not directory.exists():
        return docs
    seen_bases: set = set()
    for path in sorted(directory.rglob("*.md")):
        if path.name.startswith("_"):
            continue
        try:
            parsed = parse_knowledge_file(path)
        except ValueError as exc:
            print(f"[跳过] {path}: {exc}")
            continue
        if not parsed:
            print(f"[跳过] {path}: 正文为空")
            continue
        base, _, suffix = parsed[0].id.rpartition("#")
        if base in seen_bases:
            base = f"{base}-{path.stem}"
        seen_bases.add(base)
        for doc in parsed:
            _, _, suffix = doc.id.rpartition("#")
            doc.id = f"{base}#{suffix}"
        docs.extend(parsed)
    return docs
