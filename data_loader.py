# data_loader.py

import pandas as pd
import ast
import re
from config import driver
from typing import List, Tuple

def load_triples(filepath):
    """Load triples from a text or CSV file"""
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


def load_triples_from_neo4j() -> pd.DataFrame:
    """
    Queries Neo4j Aura for triples (subject, predicate, object) along with node labels.
    Returns a DataFrame with columns: subject, subject_label, predicate, object, object_label
    """
    if driver is None:
        raise ConnectionError("Neo4j driver not initialized. Check your config.py.")

    query = """
    MATCH (a)-[r]->(b)
    RETURN DISTINCT 
        a.name AS subject, 
        labels(a)[0] AS subject_label,
        type(r) AS predicate, 
        b.name AS object,
        labels(b)[0] AS object_label
    """

    with driver.session() as session:
        results = session.run(query)
        data = [
            (
                record["subject"], 
                record["subject_label"],
                record["predicate"], 
                record["object"],
                record["object_label"]
            ) 
            for record in results
        ]

    if not data:
        print("WARNING: No triples found in Neo4j - check your graph data.")
    
    return pd.DataFrame(data, columns=["subject", "subject_label", "predicate", "object", "object_label"])


# ==========================================
# Pydantic Model Integration (Optional)
# ==========================================

# Only import if graph_models exists
try:
    from graph_models import (
        Person, Community, Location, Religion, EducationLevel, Gender, Sexuality,
        AlsoInvolvedIn, AssociatedWith, LivesIn, OriginallyFrom,
        HasReligiousView, HasEducationLevel, HasTheGender, LevelOfInvolvement
    )
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False
    print("WARNING: graph_models.py not found - Pydantic import functions disabled")


def import_triple_to_neo4j(subject: str, predicate: str, obj: str) -> None:
    """
    Import a single triple into Neo4j using Pydantic models.
    Automatically determines node and relationship types based on predicate.
    
    Requires: graph_models.py
    """
    if not MODELS_AVAILABLE:
        raise ImportError("graph_models.py required for this function")
    
    if driver is None:
        raise ConnectionError("Neo4j driver not initialized.")
    
    # Determine node types and create nodes
    subject_node = _create_node_from_predicate(subject, predicate, is_subject=True)
    object_node = _create_node_from_predicate(obj, predicate, is_subject=False)
    
    # Create nodes in Neo4j
    subject_node.merge(driver)
    object_node.merge(driver)
    
    # Create relationship
    relationship = _create_relationship_from_predicate(predicate)
    relationship.connect(driver, subject_node, object_node)


def _create_node_from_predicate(name: str, predicate: str, is_subject: bool):
    """Determine the appropriate node type based on predicate"""
    if not MODELS_AVAILABLE:
        raise ImportError("graph_models.py required for this function")
    
    predicate_upper = predicate.upper()
    
    # Map predicates to node types
    if is_subject:
        # Subjects are typically Person nodes
        if predicate_upper in ['ALSO_INVOLVED_IN', 'ASSOCIATED_WITH', 'LEVEL_OF_INVOLVEMENT',
                               'LIVES_IN', 'ORIGINALLY_FROM', 'HAS_RELIGIOUS_VIEW', 
                               'HAS_EDUCATION_LEVEL', 'HAS_THE_GENDER']:
            return Person(name=name)
        else:
            return Community(name=name)
    else:
        # Objects vary based on predicate
        if predicate_upper in ['ALSO_INVOLVED_IN', 'ASSOCIATED_WITH', 'LEVEL_OF_INVOLVEMENT']:
            # Check if it's LGBTQ-related
            if 'LGBTQ' in name.upper():
                return Sexuality(name=name)
            return Community(name=name)
        elif predicate_upper in ['LIVES_IN', 'ORIGINALLY_FROM']:
            return Location(name=name)
        elif predicate_upper == 'HAS_RELIGIOUS_VIEW':
            return Religion(name=name)
        elif predicate_upper == 'HAS_EDUCATION_LEVEL':
            return EducationLevel(name=name)
        elif predicate_upper == 'HAS_THE_GENDER':
            return Gender(name=name)
        else:
            return Community(name=name)


def _create_relationship_from_predicate(predicate: str):
    """Create the appropriate relationship model based on predicate"""
    if not MODELS_AVAILABLE:
        raise ImportError("graph_models.py required for this function")
    
    predicate_upper = predicate.upper()
    
    relationship_map = {
        'ALSO_INVOLVED_IN': AlsoInvolvedIn(),
        'ASSOCIATED_WITH': AssociatedWith(),
        'LIVES_IN': LivesIn(),
        'ORIGINALLY_FROM': OriginallyFrom(),
        'HAS_RELIGIOUS_VIEW': HasReligiousView(),
        'HAS_EDUCATION_LEVEL': HasEducationLevel(),
        'HAS_THE_GENDER': HasTheGender(),
        'LEVEL_OF_INVOLVEMENT': LevelOfInvolvement()
    }
    
    return relationship_map.get(predicate_upper, AssociatedWith())


def bulk_import_triples(triples: List[Tuple[str, str, str]]) -> None:
    """
    Import multiple triples into Neo4j using Pydantic models.
    
    Args:
        triples: List of (subject, predicate, object) tuples
    
    Requires: graph_models.py
    """
    if not MODELS_AVAILABLE:
        raise ImportError("graph_models.py required for this function")
    
    print(f"Importing {len(triples)} triples...")
    
    for i, (subject, predicate, obj) in enumerate(triples):
        try:
            import_triple_to_neo4j(subject, predicate, obj)
            if (i + 1) % 100 == 0:
                print(f"  Imported {i + 1}/{len(triples)} triples")
        except Exception as e:
            print(f"  WARNING: Error importing triple #{i+1} ({subject}, {predicate}, {obj}): {e}")
    
    print(f"Import complete: {len(triples)} triples processed")


def validate_triple(subject: str, predicate: str, obj: str) -> bool:
    """
    Validate a triple using Pydantic models before importing.
    
    Returns:
        True if valid, False otherwise
    
    Requires: graph_models.py
    """
    if not MODELS_AVAILABLE:
        print("WARNING: graph_models.py not available - skipping validation")
        return True
    
    try:
        subject_node = _create_node_from_predicate(subject, predicate, is_subject=True)
        object_node = _create_node_from_predicate(obj, predicate, is_subject=False)
        relationship = _create_relationship_from_predicate(predicate)
        return True
    except Exception as e:
        print(f"ERROR: Validation failed for ({subject}, {predicate}, {obj}): {e}")
        return False