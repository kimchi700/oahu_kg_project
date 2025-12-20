# graph_models.py
"""
Pydantic-based graph data models for Knowledge Graph ingestion.

These models:
- Validate node and relationship data
- Infer node labels based on predicate semantics
- Produce Neo4j-ready triples
"""

from typing import Optional, Tuple, Literal
from pydantic import BaseModel, Field, validator


# --------------------------------------------------
# Node Models
# --------------------------------------------------

class Node(BaseModel):
    name: str = Field(..., description="Node display name")
    label: Literal["Community", "Main_Community", "Attribute"]

    class Config:
        frozen = True


class Community(Node):
    label: Literal["Community"] = "Community"


class MainCommunity(Node):
    label: Literal["Main_Community"] = "Main_Community"


class Attribute(Node):
    label: Literal["Attribute"] = "Attribute"


# --------------------------------------------------
# Relationship Model
# --------------------------------------------------

class Relationship(BaseModel):
    subject: Node
    predicate: str
    object: Node

    @validator("predicate")
    def normalize_predicate(cls, v: str) -> str:
        return v.replace(" ", "_").upper()

    def to_triple(self) -> Tuple[str, str, str]:
        """
        Neo4j-ready triple
        """
        return (
            self.subject.name,
            self.predicate,
            self.object.name
        )

    class Config:
        frozen = True


# --------------------------------------------------
# Predicate Semantics (mirrors loader)
# --------------------------------------------------

ATTRIBUTE_EDGES = {
    "FEELS_ALOHA_SPIRIT",
    "HAS_EDUCATION_LEVEL",
    "HAS_RELIGIOUS_VIEW",
    "HAS_THE_GENDER",
    "HAWAIIAN_CULTURE_KNOWLEDGE",
    "LIVES_IN",
    "ORIGINALLY_FROM",
    "US_BORN_STATUS",
    "FROM_COUNTRY",
    "YEARS_ON_ISLAND",
    "PLANS_TO_STAY",
    "HAS_SEXUALITY",
    "RELATIONSHIP_STATUS",
    "IN_AGE_RANGE_OF",
    "HAS_OCCUPATION",
    "LEVEL_OF_INVOLVEMENT",
}

COMMUNITY_EDGES = {
    "ALSO_INVOLVED_IN",
    "ASSOCIATED_WITH",
}

MAIN_COMMUNITY_EDGE = "HAS_MAIN_COMMUNITY"


# --------------------------------------------------
# Label Inference Logic
# --------------------------------------------------

def infer_nodes(
    subject: str,
    predicate: str,
    obj: str,
    previous_predicate: Optional[str] = None
) -> Tuple[Node, Node]:
    """
    Infer node labels based on relationship semantics.
    Matches logic in load_kg_from_file.py
    """
    pred = predicate.replace(" ", "_").upper()

    # Community → Attribute
    if pred in ATTRIBUTE_EDGES:
        return (
            Community(name=subject),
            Attribute(name=str(obj))
        )

    # Community → Community
    if pred in COMMUNITY_EDGES:
        return (
            Community(name=subject),
            Community(name=obj)
        )

    # HAS_MAIN_COMMUNITY logic
    if MAIN_COMMUNITY_EDGE in pred:
        if previous_predicate and previous_predicate.upper() in COMMUNITY_EDGES:
            return (
                Community(name=subject),
                MainCommunity(name=obj)
            )
        return (
            Attribute(name=subject),
            MainCommunity(name=obj)
        )

    # Fallback
    return (
        Community(name=subject),
        Attribute(name=str(obj))
    )


# --------------------------------------------------
# Factory Function (Loader-facing)
# --------------------------------------------------

def build_relationship(
    subject: str,
    predicate: str,
    obj: str,
    previous_predicate: Optional[str] = None
) -> Relationship:
    """
    Build a validated Relationship object from raw triple data.
    """
    subj_node, obj_node = infer_nodes(
        subject=subject,
        predicate=predicate,
        obj=obj,
        previous_predicate=previous_predicate
    )

    return Relationship(
        subject=subj_node,
        predicate=predicate,
        object=obj_node
    )
