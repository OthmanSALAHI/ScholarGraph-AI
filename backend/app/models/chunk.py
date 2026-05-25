from dataclasses import dataclass


@dataclass
class Chunk:
    paper_id: str
    text: str