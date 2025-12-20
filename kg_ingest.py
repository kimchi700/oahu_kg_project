# kg_ingest.py
"""
Unified KG ingestion script.

- Preprocesses survey CSV
- Builds KG relationships
- Validates via graph_models (Pydantic)
- Loads directly into Neo4j
"""

import math
import pandas as pd
from neo4j import GraphDatabase

from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from graph_models import build_relationship


# --------------------------------------------------
# Neo4j driver (NO credentials hardcoded)
# --------------------------------------------------

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def clean_value(v):
    if isinstance(v, float) and math.isnan(v):
        return None
    if v is None:
        return None
    if isinstance(v, str):
        s = v.strip()
        if s.lower() == "nan" or s == "":
            return None
        return s.replace("'", "").replace('"', "")
    return v


def preprocess_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    All preprocessing logic previously in create_graph_from_df.py
    """

    df = df.copy()

    # Normalize community text
    df['Community Involvement'] = (
        df['Community Involvement']
        .str.replace(r'\s*\([^)]*\)', '', regex=True)
        .str.strip()
    )

    df['Associated Communities'] = (
        df['Associated Communities']
        .str.replace(r'\s*\([^)]*\)', '', regex=True)
        .str.strip()
    )

    # Map Aloha Spirit
    df['Feel Aloha Spirit'] = df['Feel Aloha Spirit'].map({
        'Almost always. Most people around me prioritize love, kindness, humility, respect, and community.': 'Almost Always',
        "Sometimes when I'm around the right people": 'Sometimes',
        'Almost half of the time  / on a sunny day': 'Half of the time'
    })

    # Map Residence
    df['Residence'] = df['Residence'].map({
        'Honolulu (Diamond Head, Hawaii Kai, Ala Moana, Kaimuki, Manoa, Palolo)': 'Honolulu',
        'Central Oahu (Waipahu, Pearl City, Miliani)': 'Central Oahu',
        'North Shore (Haleiwa and Waimea)': 'North Shore',
        'Windward Coast': 'East Side',
        'Leeward Coast': 'West Side'
    })

    return df


# --------------------------------------------------
# Relationship extraction
# --------------------------------------------------

def extract_relationships(df: pd.DataFrame):
    """
    Yield raw (subject, predicate, object) triples
    """

    for _, row in df.iterrows():
        main = clean_value(row['Main Community'])
        if not main:
            continue

        # ID
        if pd.notna(row.get('ID')):
            yield main, "HAS_ID", row['ID']
            yield row['ID'], "HAS_MAIN_COMMUNITY", main

        # Community involvement
        for val in str(row.get('Community Involvement', '')).split(','):
            val = clean_value(val)
            if val and val != main:
                yield main, "ALSO_INVOLVED_IN", val
                yield val, "HAS_MAIN_COMMUNITY", main

        for val in str(row.get('Associated Communities', '')).split(','):
            val = clean_value(val)
            if val and val != main:
                yield main, "ASSOCIATED_WITH", val
                yield val, "HAS_MAIN_COMMUNITY", main

        # Attribute mappings
        attr_map = {
            "HAS_THE_GENDER": "Gender",
            "LEVEL_OF_INVOLVEMENT": "Community Scale",
            "FEELS_ALOHA_SPIRIT": "Feel Aloha Spirit",
            "HAWAIIAN_CULTURE_KNOWLEDGE": "Hawaiian Culture",
            "HAS_EDUCATION_LEVEL": "Education",
            "HAS_RELIGIOUS_VIEW": "Religious View",
            "LIVES_IN": "Residence",
            "ORIGINALLY_FROM": "State",
            "FROM_COUNTRY": "Country",
            "US_BORN_STATUS": "U.S. Born",
            "YEARS_ON_ISLAND": "Years on Island:",
            "PLANS_TO_STAY": "Stay on Island:",
            "HAS_SEXUALITY": "Sexuality",
            "RELATIONSHIP_STATUS": "Relationship Status ",
            "IN_AGE_RANGE_OF": "Age",
            "HAS_OCCUPATION": "Occupation",
        }

        for rel, col in attr_map.items():
            val = clean_value(row.get(col))
            if val:
                yield main, rel, val
                yield val, "HAS_MAIN_COMMUNITY", main


# --------------------------------------------------
# Neo4j write
# --------------------------------------------------

def create_relation(tx, rel):
    query = f"""
    MERGE (a:{rel.subject.label} {{name: $subject}})
    MERGE (b:{rel.object.label} {{name: $object}})
    MERGE (a)-[:{rel.predicate}]->(b)
    """
    tx.run(
        query,
        subject=rel.subject.name,
        object=rel.object.name
    )


# --------------------------------------------------
# Main loader
# --------------------------------------------------

def load_kg_from_csv(csv_path: str):
    df = pd.read_csv(csv_path)
    df = preprocess_df(df)

    previous_pred = None

    with driver.session() as session:
        for s, p, o in extract_relationships(df):
            rel = build_relationship(s, p, o, previous_pred)
            session.execute_write(create_relation, rel)
            previous_pred = p

    print("✓ Knowledge Graph successfully loaded")


# --------------------------------------------------
# CLI
# --------------------------------------------------

if __name__ == "__main__":
    load_kg_from_csv("data/data_preprcd_12_18.csv")
