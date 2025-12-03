import os
from openai import OpenAI

# Knowledge Graph data path
KG_FILE = 'data/kg_pairs_list.txt'

# Configure OpenAI client
os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", "YOUR API KEY HERE")

try:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except Exception as e:
    print(f"Warning: OpenAI client initialization failed: {e}")
    client = None
