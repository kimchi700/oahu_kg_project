# data_loader.py
"""
Data loading utilities for the Oahu Community Knowledge Graph.

Knowledge Graph Structure:
--------------------------
Node Types:
- Main_Community: Primary community nodes (with ID property)
- Community: Secondary/involved communities
- Attribute: Demographic and characteristic values

Edge Types:
- Community-to-Community: ALSO_INVOLVED_IN, ASSOCIATED_WITH, ALSO_ASSOCIATED_WITH
- Community-to-Attribute: HAS_THE_GENDER, HAS_EDUCATION_LEVEL, LIVES_IN, etc.
- Attribute/Community-to-Main_Community: HAS_MAIN_COMMUNITY (reverse relationships)
- Main_Community-to-ID: HAS_ID (stored as property, not relationship)

All edge types are CAPITALIZED with underscores (e.g., HAS_THE_GENDER, YEARS_ON_ISLAND).
"""

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
# Additional Utility Functions
# ==========================================

def get_all_edge_types() -> List[str]:
    """
    Returns a list of all supported edge types in the knowledge graph.
    """
    return [
        # Community-to-Community edges
        'ALSO_INVOLVED_IN',
        'ASSOCIATED_WITH',
        
        # Attribute edges
        'FEELS_ALOHA_SPIRIT',
        'HAS_EDUCATION_LEVEL',
        'HAS_RELIGIOUS_VIEW',
        'HAS_THE_GENDER',
        'HAWAIIAN_CULTURE_KNOWLEDGE',
        'LIVES_IN',
        'ORIGINALLY_FROM',
        'US_BORN_STATUS',
        'FROM_COUNTRY',
        'YEARS_ON_ISLAND',
        'PLANS_TO_STAY',
        'HAS_SEXUALITY',
        'RELATIONSHIP_STATUS',
        'IN_AGE_RANGE_OF',
        'HAS_OCCUPATION',
        'LEVEL_OF_INVOLVEMENT',
        
        # Reverse edges
        'HAS_MAIN_COMMUNITY',
        'HAS_ID'
    ]


def get_node_types() -> List[str]:
    """
    Returns a list of all node types in the knowledge graph.
    """
    return ['Main_Community', 'Community', 'Attribute']


def detect_community_names(triples: List[Tuple[str, str, str]]) -> set:
    """
    Detect community names from triples by finding subjects and objects
    in community-to-community relationships.
    
    Args:
        triples: List of (subject, predicate, object) tuples
    
    Returns:
        Set of community names
    """
    community_names = set()
    
    for subject, predicate, obj in triples:
        pred_upper = str(predicate).upper()
        
        if ("ALSO_INVOLVED_IN" in pred_upper or
            "ASSOCIATED_WITH" in pred_upper or
            "COMMUNITY" in pred_upper):
            if isinstance(subject, str):
                community_names.add(subject)
            if isinstance(obj, str):
                community_names.add(obj)
    
    return community_names


def import_triple_to_neo4j(subject: str, predicate: str, obj: str, previous_relation: str = None) -> None:
    """
    Import a single triple into Neo4j using the knowledge graph structure.
    Automatically determines node labels based on predicate.
    
    Args:
        subject: Subject node name
        predicate: Relationship type
        obj: Object node name/value
        previous_relation: Previous relationship in sequence (for HAS_MAIN_COMMUNITY logic)
    """
    if driver is None:
        raise ConnectionError("Neo4j driver not initialized.")
    
    # Special handling for HAS_ID - store as property
    if predicate.upper() == 'HAS_ID':
        query = """
        MERGE (a:Main_Community {name: $subject})
        SET a.id = $id_value
        """
        with driver.session() as session:
            session.run(query, subject=subject, id_value=obj)
        return
    
    # Determine node labels
    subject_label, object_label = _determine_labels(subject, predicate, obj, previous_relation)
    
    # Create nodes and relationship
    rel_type = predicate.replace(" ", "_").upper()
    
    query = f"""
    MERGE (a:{subject_label} {{name: $subject}})
    MERGE (b:{object_label} {{name: $object}})
    MERGE (a)-[r:{rel_type}]->(b)
    """
    
    with driver.session() as session:
        session.run(query, subject=subject, object=str(obj))


def _determine_labels(subject: str, predicate: str, obj: str, previous_relation: str = None) -> Tuple[str, str]:
    """
    Determine node labels based on predicate type.
    Matches the logic from load_kg_from_file.py
    
    Returns:
        Tuple of (subject_label, object_label)
    """
    pred_upper = predicate.upper()
    
    # Define edge type categories
    attribute_object_edges = {
        'FEELS_ALOHA_SPIRIT',
        'HAS_EDUCATION_LEVEL', 
        'HAS_RELIGIOUS_VIEW',
        'HAS_THE_GENDER',
        'HAWAIIAN_CULTURE_KNOWLEDGE',
        'LIVES_IN',
        'ORIGINALLY_FROM',
        'US_BORN_STATUS',
        'FROM_COUNTRY',
        'YEARS_ON_ISLAND',
        'PLANS_TO_STAY',
        'HAS_SEXUALITY',
        'RELATIONSHIP_STATUS',
        'IN_AGE_RANGE_OF',
        'HAS_OCCUPATION',
        'LEVEL_OF_INVOLVEMENT'
    }
    
    community_to_community_edges = {
        'ALSO_INVOLVED_IN',
        'ASSOCIATED_WITH'
    }
    
    # Helper function to check if predicate matches edge set
    def matches_edge_set(rel_str, edge_set):
        rel_normalized = rel_str.replace('_', '').replace(' ', '').upper()
        for edge in edge_set:
            edge_normalized = edge.replace('_', '').replace(' ', '').upper()
            if edge_normalized in rel_normalized or rel_normalized in edge_normalized:
                return True
        return False
    
    # CASE 1: Object is Attribute, Subject is Community
    if matches_edge_set(pred_upper, attribute_object_edges):
        return "Community", "Attribute"
    
    # CASE 2: Both Subject and Object are Community
    if matches_edge_set(pred_upper, community_to_community_edges):
        return "Community", "Community"
    
    # CASE 3: HAS_MAIN_COMMUNITY - Object is Main_Community
    if "HAS_MAIN_COMMUNITY" in pred_upper:
        # Determine subject label based on previous relation
        if previous_relation:
            prev_rel_upper = previous_relation.upper()
            if matches_edge_set(prev_rel_upper, community_to_community_edges):
                subj_label = "Community"
            else:
                subj_label = "Attribute"
        else:
            # Default to Attribute if no previous relation
            subj_label = "Attribute"
        
        return subj_label, "Main_Community"
    
    # DEFAULT / FALLBACK
    return "Community", "Attribute"


def bulk_import_triples(triples: List[Tuple[str, str, str]]) -> None:
    """
    Import multiple triples into Neo4j.
    Tracks previous relation for proper HAS_MAIN_COMMUNITY label assignment.
    
    Args:
        triples: List of (subject, predicate, object) tuples
    """
    print(f"Importing {len(triples)} triples...")
    
    previous_relation = None
    for i, (subject, predicate, obj) in enumerate(triples):
        try:
            import_triple_to_neo4j(subject, predicate, obj, previous_relation)
            previous_relation = predicate  # Track for next iteration
            
            if (i + 1) % 100 == 0:
                print(f"  Imported {i + 1}/{len(triples)} triples")
        except Exception as e:
            print(f"  WARNING: Error importing triple #{i+1} ({subject}, {predicate}, {obj}): {e}")
    
    print(f"Import complete: {len(triples)} triples processed")


def validate_triple(subject: str, predicate: str, obj: str, previous_relation: str = None) -> bool:
    """
    Validate a triple before importing.
    Checks that labels can be determined and values are non-empty.
    
    Args:
        subject: Subject node name
        predicate: Relationship type
        obj: Object node name/value
        previous_relation: Previous relationship in sequence
    
    Returns:
        True if valid, False otherwise
    """
    try:
        # Check for empty values
        if not subject or not predicate or not obj:
            print(f"ERROR: Empty value in triple ({subject}, {predicate}, {obj})")
            return False
        
        # Check for None/nan values
        if subject is None or predicate is None or obj is None:
            print(f"ERROR: None value in triple ({subject}, {predicate}, {obj})")
            return False
        
        # Try to determine labels
        subject_label, object_label = _determine_labels(subject, predicate, obj, previous_relation)
        
        # Verify labels are valid
        valid_labels = {'Main_Community', 'Community', 'Attribute'}
        if subject_label not in valid_labels or object_label not in valid_labels:
            print(f"ERROR: Invalid labels for ({subject}, {predicate}, {obj}): {subject_label}, {object_label}")
            return False
        
        return True
    except Exception as e:
        print(f"ERROR: Validation failed for ({subject}, {predicate}, {obj}): {e}")
        return False


# ==========================================
# Usage Examples
# ==========================================

def example_usage():
    """
    Example usage of the data_loader functions.
    Run this to see how to load and import triples into Neo4j.
    """
    print("=== Data Loader Usage Examples ===\n")
    
    # Example 1: Load triples from a text file
    print("Example 1: Load triples from file")
    # triples = load_triples('data/kg_pairs_list.txt')
    # print(f"Loaded {len(triples)} triples\n")
    
    # Example 2: Load triples from Neo4j
    print("Example 2: Load existing triples from Neo4j")
    # df = load_triples_from_neo4j()
    # print(f"Loaded {len(df)} triples from Neo4j")
    # print(df.head())
    
    # Example 3: Import single triple
    print("\nExample 3: Import single triple")
    # import_triple_to_neo4j("Surfing Community", "HAS_THE_GENDER", "Male")
    
    # Example 4: Bulk import with validation
    print("\nExample 4: Bulk import with validation")
    example_triples = [
        ("Surfing Community", "ALSO_INVOLVED_IN", "Environmental Community"),
        ("Environmental Community", "HAS_MAIN_COMMUNITY", "Surfing Community"),
        ("Surfing Community", "HAS_THE_GENDER", "Male"),
        ("Male", "HAS_MAIN_COMMUNITY", "Surfing Community"),
    ]
    
    # Validate before import
    # valid_triples = [t for t in example_triples if validate_triple(t[0], t[1], t[2])]
    # print(f"{len(valid_triples)}/{len(example_triples)} triples are valid")
    
    # Import
    # bulk_import_triples(valid_triples)
    
    # Example 5: Get supported edge types
    print("\nExample 5: Get all edge types")
    edge_types = get_all_edge_types()
    print(f"Total edge types: {len(edge_types)}")
    print("Community-to-Community edges:")
    for edge in edge_types[:3]:
        print(f"  - {edge}")
    
    # Example 6: Detect communities from triples
    print("\nExample 6: Detect community names")
    # communities = detect_community_names(example_triples)
    # print(f"Found {len(communities)} communities: {communities}")


if __name__ == "__main__":
    # Uncomment to run examples
    example_usage()