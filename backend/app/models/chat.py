from dataclasses import dataclass


@dataclass
class ChatMessage:
    paper_id: str
    message: str