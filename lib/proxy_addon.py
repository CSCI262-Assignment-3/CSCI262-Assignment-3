"""mitmproxy addon that blocks phishing URLs using the Detector class."""

import pathlib
import sys

from mitmproxy import http

# mitmdump loads this file as a standalone script, so add the project root
# to sys.path first to be able to import the lib package.
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from lib.detector import Detector
from lib.logger import Logger, URLAccessAttempt
from lib.model import phishing_model

BLOCK_PAGE = """
<!DOCTYPE html>
<html>
  <head><title>Phishing blocked</title></head>
  <body>
    <h1>This site has been blocked</h1>
    <p>The Phishing Prevention Proxy flagged this URL as a phishing link.</p>
  </body>
</html>
"""

HTTPS_UNSUPPORTED_PAGE = """
<!DOCTYPE html>
<html>
  <head><title>HTTPS not supported</title></head>
  <body>
    <h1>HTTPS is not inspected</h1>
    <p>This demo proxy only inspects plain HTTP URLs. Try an http:// URL instead.</p>
  </body>
</html>
"""

HTML_HEADERS = {"Content-Type": "text/html; charset=utf-8"}


class PhishingBlocker:
    """mitmproxy addon that checks every request against the Detector."""

    def __init__(self) -> None:
        blocklist_path = PROJECT_ROOT / "data" / "phishing_urls.txt"
        self.detector = Detector(blocklist_path, phishing_model)
        self.logger = Logger(PROJECT_ROOT / "logs.txt")

    def request(self, flow: http.HTTPFlow) -> None:
        """Check each URL and block it if it looks like phishing."""
        url = flow.request.pretty_url
        is_phishing = self.detector.isKnownPhishingURL(url)

        # Record the attempt in the log file
        self.logger.log(URLAccessAttempt(flow.request.host, url, is_phishing))

        if is_phishing:
            print(f"BLOCKED {url}")
            flow.response = http.Response.make(403, BLOCK_PAGE, HTML_HEADERS)
        # Otherwise leave flow.response unset: mitmproxy forwards the request
        # to the server and relays its response back to the client for us.

    def http_connect(self, flow: http.HTTPFlow) -> None:
        """Reject HTTPS tunnels, this demo only inspects plain HTTP URLs."""
        flow.response = http.Response.make(403, HTTPS_UNSUPPORTED_PAGE, HTML_HEADERS)


# mitmproxy finds hooks on module-level functions or in an "addons" list,
# so hand it an instance of our class.
addons = [PhishingBlocker()]
