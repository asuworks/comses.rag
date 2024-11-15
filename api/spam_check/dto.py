from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LLMSpamReport:
    is_spam: bool
    spam_indicators: list[str]
    reasoning: str
    confidence: float


@dataclass
class SpamReport:
    object_id: int
    is_spam: bool
    spam_indicators: list[str]
    reasoning: str
    confidence: float


@dataclass
class ContentObject:
    id: int
    title: str
    summary: str
    description: str
    externalUrl: Optional[str] = field(default="")


@dataclass
class SpamCheckModel:
    id: int
    contentType: str
    objectId: int
    contentObject: ContentObject
