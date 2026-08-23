import re
from pathlib import Path
from typing import Dict, List

import yaml

from .models import Dimension, ExtraQuestion, Option, Questionnaire, Question, ScoreRule

_FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
_OPTION_EQ_RE = re.compile(r"^(\d+)\s*=\s*(.+)$")
_OPTION_PAREN_RE = re.compile(r"^(.+?)\s*\(\s*(\d+)\s*\)$")


def parse_options(text: str) -> List[Option]:
    normalized = text.replace(" / ", ", ").replace("/", ",")
    tokens = [t.strip() for t in normalized.split(",") if t.strip()]
    options: List[Option] = []
    for tok in tokens:
        m = _OPTION_EQ_RE.match(tok)
        if m:
            options.append(Option(score=int(m.group(1)), desc=m.group(2).strip()))
            continue
        m = _OPTION_PAREN_RE.match(tok)
        if m:
            options.append(Option(score=int(m.group(2)), desc=m.group(1).strip()))
            continue
        raise ValueError(f"无法解析选项: {tok!r}")
    return options


def _expand_items(items) -> List[int]:
    if isinstance(items, int):
        return [items]
    if isinstance(items, str):
        if "-" in items:
            lo_s, hi_s = items.split("-", 1)
            return list(range(int(lo_s), int(hi_s) + 1))
        return [int(items)]
    if isinstance(items, list):
        out = []
        for it in items:
            out.extend(_expand_items(it))
        return out
    raise ValueError(f"无法解析 dimensions.items: {items!r}")


def _parse_cell_row(line: str) -> List[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def _parse_table_rows(body_lines: List[str]) -> List[List[str]]:
    tables: List[List[str]] = []
    current = None
    for line in body_lines:
        stripped = line.strip()
        if stripped.startswith("|"):
            if current is None:
                current = []
            if re.match(r"^\|[\s\-\|:]+\|?\s*$", stripped):
                continue
            current.append(stripped)
        else:
            if current is not None and current:
                tables.append(current)
            current = None
    if current is not None and current:
        tables.append(current)
    rows: List[List[str]] = []
    for table in tables:
        for row in table[1:]:
            cells = _parse_cell_row(row)
            if len(cells) < 3:
                continue
            rows.append(cells)
    return rows


def _parse_extra_questions(body_lines: List[str]) -> List[ExtraQuestion]:
    extras: List[ExtraQuestion] = []
    quote_lines: List[str] = []
    in_quote = False
    for line in body_lines:
        if line.strip().startswith(">"):
            in_quote = True
            quote_lines.append(line.strip().lstrip(">").strip())
        else:
            if in_quote:
                extras.extend(_build_extra(quote_lines))
                quote_lines = []
                in_quote = False
    if in_quote:
        extras.extend(_build_extra(quote_lines))
    return extras


def _build_extra(quote_lines: List[str]) -> List[ExtraQuestion]:
    content_lines: List[str] = []
    options_text: str = ""
    note_lines: List[str] = []
    for line in quote_lines:
        if line.startswith("选项"):
            options_text = line[len("选项"):].lstrip("：:").strip()
        elif line.startswith("注"):
            note_lines.append(line.lstrip("注：:").strip())
        else:
            content_lines.append(line)
    if not options_text:
        return []
    try:
        options = parse_options(options_text)
    except ValueError:
        return []
    content = " ".join(c for c in content_lines if c)
    note = " ".join(n for n in note_lines if n)
    return [ExtraQuestion(content=content, options=options, note=note)]


def parse_questionnaire(path: Path) -> Questionnaire:
    text = Path(path).read_text(encoding="utf-8")
    m = _FRONT_MATTER_RE.match(text)
    if not m:
        raise ValueError(f"{path} 缺少 YAML frontmatter")
    meta = yaml.safe_load(m.group(1)) or {}
    body = text[m.end():]
    body_lines = body.splitlines()

    questions: Dict[int, Question] = {}
    for cells in _parse_table_rows(body_lines):
        try:
            seq = int(cells[0])
        except ValueError:
            continue
        content = cells[1]
        options = parse_options(cells[2])
        reverse = len(cells) > 3 and "是" in cells[3]
        questions[seq] = Question(seq=seq, content=content, options=options, reverse=reverse)

    dimensions = [
        Dimension(
            name=d["name"],
            items=_expand_items(d.get("items", [])),
            weight=int(d.get("weight", 1)),
            value_type=str(d.get("value_type", "sum")),
        )
        for d in meta.get("dimensions", [])
    ]

    scoring: Dict[str, List[ScoreRule]] = {}
    for dim_name, rules in (meta.get("scoring") or {}).items():
        scoring[dim_name] = [
            ScoreRule(lo=float(r["range"][0]), hi=float(r["range"][1]), level=r["level"], description=r["description"])
            for r in rules
        ]

    return Questionnaire(
        id=meta["id"],
        name=meta.get("name", ""),
        version=meta.get("version", ""),
        description=meta.get("description", ""),
        time_reference=meta.get("time_reference", ""),
        dimensions=dimensions,
        scoring=scoring,
        questions=questions,
        extra_questions=_parse_extra_questions(body_lines),
        meta=meta,
    )
