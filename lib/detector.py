import pathlib

from .model import phishing_model


class Detector:
    """Class for checking URLs against a phishing list."""

    def __init__(self, phishing_urls_path: pathlib.Path) -> None:
        self.phishing_urls = []

        try:
            with open(phishing_urls_path) as urls_file:
                for url in urls_file.readlines():
                    self.phishing_urls.append(url.strip())
        except FileNotFoundError:
            print(f"File '{phishing_urls_path}' does not exist!")

    def normalise_URL(self, url: str):
        """Normalises URLs by removing http/https prefixes."""
        url = url.lower().strip()
        for prefix in ("http://", "https://"):
            if url.startswith(prefix):
                url = url[len(prefix) :]
        return url.removeprefix("www.").rstrip("/")

    def isKnownPhishingURL(self, url: str) -> bool:
        """Checks URL against known phishing URLs"""

        # Normalise URL first
        url = self.normalise_URL(url)

        if url in self.phishing_urls:
            return True

        print(phishing_model.score(url))

        return False
