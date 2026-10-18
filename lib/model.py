import pathlib
import warnings

import joblib
from huggingface_hub import hf_hub_download

REPO_ID = "pirocheto/phishing-url-detection"
MODEL_FILE = "model.pkl"


class MLDetector:
    """ML phishing detecting using the pirocheto LinearSVM scikit-learn model."""

    def __init__(self, _repo_id: str = REPO_ID, _filename: str = MODEL_FILE) -> None:
        self.repo_id = _repo_id
        self.filename = _filename
        self.repo_dir = (
            pathlib.Path(__file__).resolve().parent.parent / "models" / self.repo_id
        )
        self.local_path = self.repo_dir / self.filename
        self.model = None
        self._cache: dict[str, float | None] = {}

    def download_model(self) -> None:
        """One-time ONLINE fetch (also used by a setup step)."""
        hf_hub_download(
            repo_id=self.repo_id, filename=self.filename, local_dir=self.repo_dir
        )

    def _ensure_loaded(self) -> bool:
        if self.model is not None:
            return True
        if not self.local_path.exists():
            print(f"Model missing at {self.local_path}, downloading...")
            try:
                self.download_model()
            except Exception as e:
                print(f"Download failed: {e}")
                return False
        try:
            # The model was pickled with an older scikit-learn, so ignore the
            # version mismatch warning it prints while loading.
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.model = joblib.load(self.local_path)
        except Exception as e:
            print(f"Model load error: {e}")
            return False
        return True

    def score(self, url: str) -> float | None:
        """Phishing probability in [0, 1], or None if the model can't answer."""
        if url in self._cache:
            return self._cache[url]
        if not self._ensure_loaded():
            self._cache[url] = None
            return None

        try:
            probas = self.model.predict_proba([url])[0]
            result = float(probas[1])  # column 1 = phishing
        except Exception as e:
            print(f"Classification error for {url}: {e}")
            result = None

        self._cache[url] = result
        return result


phishing_model = MLDetector()
