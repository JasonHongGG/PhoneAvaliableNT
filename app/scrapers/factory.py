from typing import Dict, Type, Callable
from app.core.interfaces import Scraper
from app.core.browser import BrowserManager

class ScraperFactory:
    _scrapers: Dict[str, Callable[[BrowserManager], Scraper]] = {}

    @classmethod
    def register(cls, name: str):
        def wrapper(scraper_cls: Type[Scraper]):
            cls._scrapers[name] = scraper_cls
            return scraper_cls
        return wrapper

    @classmethod
    def create(cls, name: str, browser_manager: BrowserManager) -> Scraper:
        scraper_cls = cls._scrapers.get(name)
        if not scraper_cls:
            raise ValueError(f"Scraper '{name}' not found. Available scrapers: {list(cls._scrapers.keys())}")
        return scraper_cls(browser_manager)

    @classmethod
    def create_all(cls, browser_manager: BrowserManager) -> list[Scraper]:
        return [scraper_cls(browser_manager) for scraper_cls in cls._scrapers.values()]
