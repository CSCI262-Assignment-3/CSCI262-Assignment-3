import pathlib


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

    def isKnownPhishingURL(self, url: str) -> bool:
        """Checks URL against known phishing URLs"""

        return url in self.phishing_urls
