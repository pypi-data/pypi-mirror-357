from typing import Optional


def get_zone(marketplace: Optional[str] = None) -> str:
    if marketplace is None:
        marketplace = "de"
    zone = {
        "us": "com",
        "usa": "com",
        "uk": "co.uk",
        "gb": "co.uk",
        "de": "de",
    }
    return zone.get(marketplace.lower(), "de")
