import os

API_KEY = os.getenv("VALENCE_API_KEY")
VALENCE_DISCRETE_URL = os.getenv(
    "VALENCE_DISCRETE_URL",
    "https://xc8n2bo4f0.execute-api.us-west-2.amazonaws.com/emotionprediction",
)
VALENCE_ASYNCH_URL = os.getenv(
    "VALENCE_ASYNCH_URL", "https://wsgol61783.execute-api.us-west-2.amazonaws.com/prod"
)
