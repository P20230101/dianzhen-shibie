from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import re
from pathlib import Path
from typing import Literal


TOKEN_RE = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class RetrievalChunk:
    paper_id: str
    chunk_id: str
    source_type: Literal["text", "table", "caption"]
    text: str
    page_no: int | None = None
    figure_id: str | None = None
    table_id: str | None = None
    source_path: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class GraphNode:
    node_id: str
    node_type: str
    label: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class GraphEdge:
    source_id: str
    target_id: str
    relation: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
