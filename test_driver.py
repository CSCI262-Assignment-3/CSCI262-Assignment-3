"""Simple test driver for detector.py and logger.py"""

from lib.detector import Detector
from lib.logger import Logger, URLAccessAttempt
from pathlib import Path

# Init the logger
log_file = Path("./test/logs_text.txt")
logger = Logger(log_file)

# Create a testing directory first
test_dir = Path("./test/")
test_dir.mkdir(exist_ok=True)

# Init the detector, creating a small phishing URL list
phishing_urls_file = Path("./test/phising_urls.txt")
with open(phishing_urls_file, "w") as phishing_file:
    print("Creating test phishing URLs file...")
    urls = ["sus.com\n", "weenie.live\n", "deez.nutz\n"]
    phishing_file.writelines(urls)
    print("Test phishing URL file created.")
detector = Detector(phishing_urls_file)

# Testing it out!
try:
    while True:
        # Test a URL
        url = str(input("Check URL > "))

        # Make an attempt object
        attempt = URLAccessAttempt("Test Host", url, detector.isKnownPhishingURL(url))

        # Make a log of the access attempt
        logger.log(attempt)

        # Tell us if it's a phishing link
        if attempt.is_phishing_link:
            print(f"'{url}' is sketchy!")
        else:
            print(f"'{url}' is fine.")
except KeyboardInterrupt:
    print(f"\nContents of {log_file}:")
    for log in logger.getAllLogs():
        print(log)
