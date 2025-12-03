import os
from openai import OpenAI
from neo4j import GraphDatabase

# ===========================
# OPENAI CONFIGURATION
# ===========================
os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", "YOUR API KEY HERE")

try:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except Exception as e:
    print(f"⚠️ OpenAI initialization failed: {e}")
    client = None

KG_FILE = 'data/kg_pairs_list.txt'

# ===========================
# NEO4J AURA CONFIGURATION
# ===========================
# Example Aura credentials (replace with your own)

# URI = "neo4j+s://33f70fbd.databases.neo4j.io"
# AUTH = ("neo4j", "IEHBh2DpL5FMxfT6-p5QDz7GK2GIxh3cTIcxNJMErNY")

URI = "neo4j+s://33f70fbd.databases.neo4j.io"
PASSWORD = "YOUR PASSWORD HERE"


NEO4J_URI = os.getenv("NEO4J_URI", URI)
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", PASSWORD)

# Initialize Neo4j driver
try:
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    print("✅ Connected to Neo4j Aura successfully.")
except Exception as e:
    driver = None
    print(f"⚠️ Neo4j connection failed: {e}")
