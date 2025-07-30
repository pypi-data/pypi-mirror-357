import os, math, time, requests
from tqdm import tqdm
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
from .config import API_KEY, VALENCE_DISCRETE_URL, VALENCE_ASYNCH_URL
from .logger import get_logger
from .exceptions import ValenceSDKException, UploadError, PredictionError

logger = get_logger()

class DiscreteClient:
    """Client for discrete (short) audio processing."""
    
    def __init__(self, headers):
        self.headers = headers
    
    def emotions(self, file_path: str, model: str = "4emotions"):
        """Get emotions for discrete (short) audio files.
        
        Args:
            file_path (str): Path to the audio file
            model (str): Model type ('4emotions' or '7emotions')
            
        Returns:
            dict: Emotion prediction results
        """
        with open(file_path, "rb") as f:
            files = {"file": f}
            params = {"model": model}
            logger.info(f"Getting emotions for discrete audio: {file_path} with model={model}")
            response = requests.post(VALENCE_DISCRETE_URL, headers=self.headers, files=files, params=params)
            response.raise_for_status()
            return response.json()

class AsyncClient:
    """Client for async (long) audio processing."""
    
    def __init__(self, headers, part_size=5*1024*1024, show_progress=True, max_threads=3):
        self.headers = headers
        self.part_size = part_size
        self.show_progress = show_progress
        self.max_threads = max_threads
    
    def upload(self, file_path: str):
        """Upload async (long) audio files using multipart upload.
        
        Args:
            file_path (str): Path to the audio file
            
        Returns:
            str: Request ID for tracking the upload
        """
        file_size = os.path.getsize(file_path)
        part_count = math.ceil(file_size / self.part_size)
        init_url = f"{VALENCE_ASYNCH_URL}/upload/initiate"
        params = {"file_name": os.path.basename(file_path), "part_count": part_count}
        response = requests.get(init_url, headers=self.headers, params=params)
        response.raise_for_status()
        data = response.json()
        upload_id, request_id, presigned_urls = data["upload_id"], data["request_id"], data["presigned_urls"]

        parts = []
        with open(file_path, "rb") as f, ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = []
            for part in presigned_urls:
                part_number = part["part_number"]
                data = f.read(self.part_size)
                future = executor.submit(self._upload_part, part["url"], data, part_number)
                futures.append(future)
            if self.show_progress:
                for f in tqdm(as_completed(futures), total=len(futures), desc="Uploading parts"):
                    part_result = f.result()
                    if part_result:
                        parts.append(part_result)
            else:
                for f in as_completed(futures):
                    part_result = f.result()
                    if part_result:
                        parts.append(part_result)

        complete_payload = OrderedDict([
            ("request_id", request_id),
            ("upload_id", upload_id),
            ("parts", sorted(parts, key=lambda x: x['PartNumber']))
        ])
        comp_url = f"{VALENCE_ASYNCH_URL}/upload/complete"
        complete_resp = requests.post(comp_url, json=complete_payload, headers=self.headers)
        complete_resp.raise_for_status()
        logger.info(f"Async upload completed. Request ID: {request_id}")
        return request_id
    
    def _upload_part(self, url, data, part_number):
        """Upload a single part of a multipart upload."""
        try:
            headers = {"Content-Length": str(len(data))}
            resp = requests.put(url, data=data, headers=headers)
            resp.raise_for_status()
            return {"ETag": resp.headers["ETag"], "PartNumber": part_number}
        except Exception as e:
            logger.error(f"Upload failed on part {part_number}")
            raise UploadError(e)
    
    def emotions(self, request_id: str, max_attempts: int = 20, interval_seconds: int = 5):
        """Get emotion prediction results for async audio.
        
        Args:
            request_id (str): Request ID from upload method
            max_attempts (int): Maximum polling attempts
            interval_seconds (int): Seconds between polling attempts
            
        Returns:
            dict: Emotion prediction results
        """
        url = f"{VALENCE_ASYNCH_URL}/prediction"
        for _ in range(max_attempts):
            time.sleep(interval_seconds)
            resp = requests.get(url, headers=self.headers, params={"request_id": request_id})
            if resp.status_code == 200:
                logger.info(f"Emotions retrieved for request ID: {request_id}")
                return resp.json()
        raise PredictionError("Failed to fetch prediction after retries.")

class ValenceClient:
    """Main client for Valence API with nested discrete and async clients."""
    
    def __init__(self, api_key: str = None, part_size=5*1024*1024, show_progress=True, max_threads=3):
        self.api_key = api_key or API_KEY
        if not self.api_key:
            raise ValenceSDKException("API key not provided and not set in environment.")
        self.headers = {"x-api-key": self.api_key}
        
        # Initialize nested clients
        self.discrete = DiscreteClient(self.headers)
        self.asynch = AsyncClient(self.headers, part_size, show_progress, max_threads)
        