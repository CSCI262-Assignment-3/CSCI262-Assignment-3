import pathlib

from .model import MLDetector


class Detector:
    """Class for checking URLs against a phishing list."""

    def __init__(
        self,
        phishing_urls_path: pathlib.Path,
        model: MLDetector,
        threshold: float = 0.9,
    ) -> None:
        self.phishing_urls = []
        self.model = model
        self.threshold = threshold

        try:
            with open(phishing_urls_path) as urls_file:
                for url in urls_file:
                    self.phishing_urls.append(url.strip())
        except FileNotFoundError:
            print(f"File '{phishing_urls_path}' does not exist!")

    def normalise_URL(self, url: str):
        """Normalises URLs by removing http/https prefixes."""
        url = url.lower().strip()
        for prefix in ("http://", "https://"):
            url = url.removeprefix(prefix)
        return url.removeprefix("www.").rstrip("/")

    def isKnownPhishingURL(self, url: str) -> bool:
        """Checks URL against known phishing URLs"""

        # Normalise URL first
        url = self.normalise_URL(url)

        # Check blacklist first
        if url in self.phishing_urls:
            return True

        # Check with model
        score: float | None = self.model.score(url)
        if score:
            return score >= self.threshold

        return False
