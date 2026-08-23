from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Option:
    score: int
    desc: str


@dataclass
class Question:
    seq: int
    content: str
    options: List[Option]
    reverse: bool = False


@dataclass
class ExtraQuestion:
    content: str
    options: List[Option]
    note: str = ""


@dataclass
class Dimension:
    name: str
    items: List[int]
    weight: int = 1
    value_type: str = "sum"


@dataclass
class ScoreRule:
    lo: float
    hi: float
    level: str
    description: str

    def matches(self, value: float) -> bool:
        return self.lo <= value <= self.hi


@dataclass
class Questionnaire:
    id: str
    name: str
    version: str
    description: str
    time_reference: str
    dimensions: List[Dimension]
    scoring: Dict[str, List[ScoreRule]]
    questions: Dict[int, Question] = field(default_factory=dict)
    extra_questions: List[ExtraQuestion] = field(default_factory=list)
    meta: dict = field(default_factory=dict)

    def sorted_questions(self) -> List[Question]:
        return [self.questions[s] for s in sorted(self.questions)]


@dataclass
class ScoreResult:
    dimension: str
    value: float
    level: str
    description: str

    def to_dict(self) -> dict:
        return {
            "dimension": self.dimension,
            "value": self.value,
            "level": self.level,
            "description": self.description,
        }


@dataclass
class AssessmentProfile:
    questionnaire_id: str
    name: str
    results: List[ScoreResult] = field(default_factory=list)
    flags: List[str] = field(default_factory=list)
    alerts: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "questionnaire_id": self.questionnaire_id,
            "name": self.name,
            "results": [r.to_dict() for r in self.results],
            "flags": self.flags,
            "alerts": self.alerts,
        }
