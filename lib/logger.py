import pathlib
from datetime import datetime


class URLAccessAttempt:
    """Class for recording URL access attempt information."""

    def __init__(
        self,
        _host_name: str = "Unknown",
        _url: str = "Unknown",
        _is_phishing_link: bool = False,
        _access_time: datetime = datetime.now(),
    ) -> None:
        self.host_name = _host_name
        self.url = _url
        self.is_phishing_link = _is_phishing_link
        self.access_time = _access_time

    def __str__(self) -> str:
        formatted_time = self.access_time
        url_type = "!!!" if self.is_phishing_link else "..."

        return (
            f"[{url_type}] [{formatted_time}]: '{self.host_name}' accessed '{self.url}'"
        )


class Logger:
    """Class for logging URL access attempts."""

    def __init__(
        self, _log_file_path: pathlib.Path = pathlib.Path("./logs.txt")
    ) -> None:
        if not _log_file_path.exists():
            print(f"Path {_log_file_path} does not exists, creating...")
            with open(_log_file_path, "x") as log_file:
                log_file.close()
                print(f"Created log file at {_log_file_path}")

        self.log_file_path = _log_file_path

    def log(self, access_attempt: URLAccessAttempt):
        """Write a URL access attempt to the log file."""
        with open(self.log_file_path, "a") as log_file:
            log_file.write(f"{access_attempt}\n")

    def getAllLogs(self) -> list[str]:
        """Return a list of strings with all human-readable logs"""
        with open(self.log_file_path, "r") as log_file:
            return log_file.readlines()
