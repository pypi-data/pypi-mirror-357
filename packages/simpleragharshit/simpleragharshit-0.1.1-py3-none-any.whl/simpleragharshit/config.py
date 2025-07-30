import os
from dotenv import load_dotenv
load_dotenv()
cohere_api_key = os.getenv("COHERE_API_KEY")
if not cohere_api_key:
    raise ValueError("COHERE_API_KEY environment variable is not set.")
embedding_model = "embed-english-v3.0"
chat_model = "command-r-plus"
default_top_k = 5
chunk_size = 300
