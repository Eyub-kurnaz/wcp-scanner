from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AttackRequest:
    attack_name: str
    target_url: str
    method: str = "GET"
    headers: dict[str, str] = field(default_factory=dict)
    params: dict[str, str] = field(default_factory=dict)
    body: Optional[bytes] = None
    category_hint: Optional[str] = None
    note: Optional[str] = None


class AttackModule(ABC):
    name: str = "base"

    @abstractmethod
    def supports(self, discovered_item) -> bool:
        """
        Bu modül bu URL üzerinde çalışmalı mı bakıcaz?
        """
        raise NotImplementedError

    @abstractmethod
    def generate(self, discovered_item) -> list[AttackRequest]:
        """
        Bu URL için gönderilebilecek attack request'lerini üretir.
        """
        raise NotImplementedError