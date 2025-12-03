# load_kg_from_file.py

import ast
import math
from neo4j import GraphDatabase

# --------------------------------------------------------
# Neo4j connection
# --------------------------------------------------------

USER = "neo4j"                 
URI = "neo4j+s://33f70fbd.databases.neo4j.io"
PASSWORD = "IEHBh2DpL5FMxfT6-p5QDz7GK2GIxh3cTIcxNJMErNY"

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))


# --------------------------------------------------------
# Helpers
# --------------------------------------------------------
def clean_value(v):
    """Normalize subject/object values (remove nan, strip spaces)."""
    # True NaN (float nan from pandas)
    if isinstance(v, float) and math.isnan(v):
        return None

    if v is None:
        return None

    if isinstance(v, str):
        s = v.strip()
        if s.lower() == "nan" or s == "":
            return None
        # Strip quotes inside the name for safety
        s = s.replace("'", "").replace('"', "")
        return s

    # ints/floats (Likert scores etc.)
    return v


def detect_community_names_from_lines(lines):
    """
    First pass: find all names that appear in 'also_involved_in' or 'associated_with'
    so we can confidently treat them as Communities.
    """
    community_names: set[str] = set()

    for raw in lines:
        raw = raw.strip()
        if not raw:
            continue

        try:
            triple = ast.literal_eval(raw)
        except Exception:
            # Skip malformed lines
            continue

        if not isinstance(triple, tuple) or len(triple) != 3:
            continue

        subj, pred, obj = triple
        subj = clean_value(subj)
        pred = clean_value(pred)
        obj = clean_value(obj)

        if subj is None or pred is None or obj is None:
            continue

        pred_lower = str(pred).lower()
        if ("also_involved_in" in pred_lower or
            "associated_with" in pred_lower or
            "community" in pred_lower):
            if isinstance(subj, str):
                community_names.add(subj)
            if isinstance(obj, str):
                community_names.add(obj)

    return community_names


def choose_labels(subject, relation, obj, community_names):
    """
    Decide labels for subject and object based on:
      - relation type
      - whether subject/object are in the community set
      - whether object is numeric (Likert score)
    """
    rel = str(relation).lower()

    # Is the object a numeric Likert score (1–7)?
    is_obj_numeric = isinstance(obj, (int, float)) and not (
        isinstance(obj, float) and math.isnan(obj)
    )

    # Helper: is this name a known community?
    def is_community(name):
        return isinstance(name, str) and name in community_names

    # ATTRIBUTE-LIKE RELATIONS
    if ("gender" in rel or
        "education" in rel or
        "religious" in rel or
        "feels_aloha_spirit" in rel or
        "hawaiian_culture" in rel):
        subj_label = "Community" if is_community(subject) else "Attribute"
        obj_label = "Attribute"
        return subj_label, obj_label

    # SPECIAL: level_of_involvement
    if "level_of_involvement" in rel:
        # Subject can be a community ("Acroyoga") or an attribute ("Almost Always")
        subj_label = "Community" if is_community(subject) else "Attribute"
        obj_label = "Attribute"   # numeric score node
        return subj_label, obj_label

    # LOCATION RELATIONS
    if "lives_in" in rel or "originally_from" in rel:
        # In your dataset, subject is a community/activity
        subj_label = "Community" if is_community(subject) else "Attribute"
        obj_label = "Location"
        return subj_label, obj_label

    # COMMUNITY RELATIONS
    if ("associated" in rel or "involved" in rel or "community" in rel):
        # Both sides are communities
        return "Community", "Community"

    # DEFAULT / FALLBACK:
    # - if it looks like a known community, keep Community
    # - otherwise treat as Attribute
    subj_label = "Community" if is_community(subject) else "Attribute"
    obj_label = "Community" if is_community(obj) else "Attribute"
    return subj_label, obj_label


def create_relation(tx, subject, relation, obj, community_names):
    """
    Create nodes + relationship with label rules and numeric handling.
    """

    subj_label, obj_label = choose_labels(subject, relation, obj, community_names)

    # Normalize node names
    subj_name = subject if isinstance(subject, str) else str(subject)

    # Handle numeric object as an Attribute node with name like "7"
    if isinstance(obj, (int, float)) and not (isinstance(obj, float) and math.isnan(obj)):
        if isinstance(obj, float) and obj.is_integer():
            obj_name = str(int(obj))
        else:
            obj_name = str(obj)
    else:
        obj_name = obj if isinstance(obj, str) else str(obj)

    rel_type = str(relation).replace(" ", "_").upper()

    query = f"""
    MERGE (a:{subj_label} {{name: $subject}})
    MERGE (b:{obj_label} {{name: $object}})
    MERGE (a)-[r:{rel_type}]->(b)
    """

    tx.run(query, subject=subj_name, object=obj_name)


# --------------------------------------------------------
# Load KG file
# --------------------------------------------------------
def load_kg_from_file(path: str):

    # FIX: allow Windows-encoded files safely
    with open(path, "r", encoding="cp1252", errors="replace") as f:
        lines = f.readlines()

    # First pass: detect community-like names from 'also_involved_in' / 'associated_with'
    community_names = detect_community_names_from_lines(lines)
    print(f"Detected {len(community_names)} community names.")

    # Second pass: actually create nodes + relations
    for raw in lines:
        raw = raw.strip()
        if not raw:
            continue

        try:
            triple = ast.literal_eval(raw)
        except Exception:
            print("Skipping invalid line:", raw)
            continue

        if not isinstance(triple, tuple) or len(triple) != 3:
            print("Skipping malformed triple:", triple)
            continue

        subj, pred, obj = triple

        subj = clean_value(subj)
        pred = clean_value(pred)
        obj = clean_value(obj)

        if subj is None or pred is None or obj is None:
            # Skip incomplete triples (nan, empty, etc.)
            continue

        with driver.session() as session:
            session.execute_write(create_relation, subj, pred, obj, community_names)

        print(f"Loaded: {subj} -[{pred}]-> {obj}")


# --------------------------------------------------------
# Run loader
# --------------------------------------------------------
if __name__ == "__main__":
    load_kg_from_file("data/kg_pairs_list.txt")  # adjust path as needed
    print("\n✓ Knowledge Graph Loaded Successfully!")