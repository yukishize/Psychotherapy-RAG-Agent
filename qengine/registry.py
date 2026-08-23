from pathlib import Path
from typing import Dict, List

from .models import Questionnaire
from .parser import parse_questionnaire


def load_all(directory: Path) -> Dict[str, Questionnaire]:
    result: Dict[str, Questionnaire] = {}
    for f in sorted(directory.glob("*.md")):
        q = parse_questionnaire(f)
        result[q.id] = q
    return result


def list_ids(directory: Path) -> List[str]:
    return sorted(p.stem for p in directory.glob("*.md"))
