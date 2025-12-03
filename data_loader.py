import pandas as pd
import ast
import re

def load_triples(filepath):
    triples = []
    if filepath.endswith('.txt'):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            try:
                triples = ast.literal_eval(content)
            except (ValueError, SyntaxError):
                pattern = r"\('([^']*)',\s*'([^']*)',\s*'([^']*)'\)"
                matches = re.findall(pattern, content)
                if not matches:
                    pattern = r'\("([^"]*)",\s*"([^"]*)",\s*"([^"]*)"\)'
                    matches = re.findall(pattern, content)
                triples = [(m[0], m[1], m[2]) for m in matches]
    elif filepath.endswith('.csv'):
        df = pd.read_csv(filepath)
        if len(df.columns) >= 3:
            triples = list(df.iloc[:, :3].itertuples(index=False, name=None))
    else:
        raise ValueError("Unsupported file format. Use .txt or .csv")
    return triples

import pandas as pd
from config import driver

def load_triples_from_neo4j():
    """
    Queries Neo4j Aura for triples (subject, predicate, object)
    and returns them as a pandas DataFrame.
    """
    if driver is None:
        raise ConnectionError("Neo4j driver not initialized. Check your config.py.")

    query = """
    MATCH (a)-[r]->(b)
    RETURN DISTINCT a.name AS subject, type(r) AS predicate, b.name AS object
    """

    with driver.session() as session:
        results = session.run(query)
        data = [(record["subject"], record["predicate"], record["object"]) for record in results]

    if not data:
        print("⚠️ No triples found in Neo4j — check your graph data.")
    return pd.DataFrame(data, columns=["subject", "predicate", "object"])
