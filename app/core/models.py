from dataclasses import dataclass
from typing import Optional

@dataclass
class PhoneNumber:
    number: str
    country: str
    link: str
    added_time: str
    relative_time: str
    discovered_at: str
    source: str = ""

    def to_dict(self) -> dict:
        return {
            "number": self.number,
            "country": self.country,
            "link": self.link,
            "added_time": self.added_time,
            "relative_time": self.relative_time,
            "discovered_at": self.discovered_at,
            "source": self.source
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PhoneNumber':
        return cls(
            number=data.get("number", ""),
            country=data.get("country", ""),
            link=data.get("link", ""),
            added_time=data.get("added_time", ""),
            relative_time=data.get("relative_time", ""),
            discovered_at=data.get("discovered_at", ""),
            source=data.get("source", "")
        )
