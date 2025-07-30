import os, math, time, requests
from tqdm import tqdm
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
from .client import ValenceClient
from .logger import get_logger
from .config import VALENCE_ASYNCH_URL
from .exceptions import UploadError, PredictionError

logger = get_logger()

class AsyncAPI(ValenceClient):
    def __init__(self, *args, part_size=5*1024*1024, show_progress=True, max_threads=3, **kwargs):
        super().__init__(*args, **kwargs)
        self.part_size = part_size
        self.show_progress = show_progress
        self.max_threads = max_threads

    def upload_file(self, file_path):
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
                future = executor.submit(self.upload_part, part["url"], data, part_number)
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
        return request_id

    def upload_part(self, url, data, part_number):
        try:
            headers = {"Content-Length": str(len(data))}
            resp = requests.put(url, data=data, headers=headers)
            resp.raise_for_status()
            return {"ETag": resp.headers["ETag"], "PartNumber": part_number}
        except Exception as e:
            logger.error(f"Upload failed on part {part_number}")
            raise UploadError(e)

    def get_emotions(self, request_id, wait_sec=5, retries=20):
        url = f"{VALENCE_ASYNCH_URL}/prediction"
        for _ in range(retries):
            time.sleep(wait_sec)
            resp = requests.get(url, headers=self.headers, params={"request_id": request_id})
            if resp.status_code == 200:
                return resp.json()
        raise PredictionError("Failed to fetch prediction after retries.")