import os
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

API_URL = os.getenv("HINDSIGHT_API_URL")
API_KEY = os.getenv("HINDSIGHT_API_KEY")
BANK_ID = os.getenv("HINDSIGHT_BANK_ID")

if not API_KEY:
    raise RuntimeError("HINDSIGHT_API_KEY is missing from .env")

if not BANK_ID:
    raise RuntimeError("HINDSIGHT_BANK_ID is missing from .env")

client = Hindsight(
    base_url=API_URL,
    api_key=API_KEY
)

print("1. Storing incident in Hindsight...")

client.retain(
    bank_id=BANK_ID,
    content=(
        "Incident INC-001 affected the Payment API. "
        "The Payment API returned 503 errors because Redis memory usage "
        "exceeded 95 percent. "
        "The incident was resolved by increasing Redis memory and adding "
        "Redis memory monitoring."
    )
)

print("Memory stored successfully.")

print("\n2. Asking Hindsight to recall the incident...")

result = client.recall(
    bank_id=BANK_ID,
    query="What happened previously when the Payment API returned 503 errors?"
)

print("\n--- HINDSIGHT RECALL ---")

if not result.results:
    print("No memories returned.")
else:
    for i, memory in enumerate(result.results, 1):
        print(f"{i}. [{memory.type}] {memory.text}")

client.close()