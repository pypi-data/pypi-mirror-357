import requests
from .client import ValenceClient
from .config import VALENCE_DISCRETE_URL
from .logger import get_logger

logger = get_logger()

class DiscreteAPI(ValenceClient):
    def predict_emotion(self, file_path: str, model: str = "4emotions"):
        with open(file_path, "rb") as f:
            files = {"file": f}
            params = {"model": model}
            logger.info(f"Uploading short audio: {file_path} with model={model}")
            response = requests.post(VALENCE_DISCRETE_URL, headers=self.headers, files=files, params=params)
            response.raise_for_status()
            return response.json()
        
