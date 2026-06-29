from typing import Protocol, List, Dict
from app.core.models import PhoneNumber

class Scraper(Protocol):
    def fetch_new_numbers(self, seen_numbers: Dict[str, dict]) -> List[PhoneNumber]:
        """
        Fetch new numbers from the source.
        Returns a list of newly found PhoneNumber objects.
        """
        ...

class Storage(Protocol):
    def load_seen(self) -> Dict[str, dict]:
        """
        Load seen numbers from storage.
        """
        ...

    def save_seen(self, seen: Dict[str, dict]) -> None:
        """
        Save seen numbers to storage.
        """
        ...

class Notifier(Protocol):
    def notify(self, phone: PhoneNumber) -> None:
        """
        Send a notification for the newly found phone number.
        """
        ...
