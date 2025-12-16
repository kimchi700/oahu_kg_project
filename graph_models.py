from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any, Dict, ClassVar, Optional, Union
from neo4j import Driver


class NodeModel(BaseModel):
    """Base class for all node types in the knowledge graph"""
    primary_key: ClassVar[str] = "name"
    label: ClassVar[Optional[str]] = None

    name: str

    def get_label(self) -> str:
        return self.label or self.__class__.__name__

    def pk_value(self):
        return getattr(self, self.primary_key)

    def to_properties(self) -> Dict[str, Any]:
        return self.model_dump(exclude={self.primary_key})

    def merge(self, driver: Driver):
        """Create or update this node in Neo4j"""
        cypher = f"""
        MERGE (n:{self.get_label()} {{{self.primary_key}: $pk}})
        SET n += $props
        """
        params = {
            "pk": self.pk_value(),
            "props": self.to_properties()
        }

        with driver.session() as session:
            session.run(cypher, params)


class RelationshipModel(BaseModel):
    """Base class for all relationship types in the knowledge graph"""
    rel_type: ClassVar[Optional[str]] = None

    def get_rel_type(self):
        return self.rel_type or self.__class__.__name__.upper()

    def connect(self, driver: Driver, a: NodeModel, b: NodeModel):
        """Create or update this relationship between two nodes"""
        cypher = f"""
        MATCH (x:{a.get_label()} {{name: $a_name}})
        MATCH (y:{b.get_label()} {{name: $b_name}})
        MERGE (x)-[r:{self.get_rel_type()}]->(y)
        SET r += $props
        """

        with driver.session() as session:
            session.run(cypher, {
                "a_name": a.name,
                "b_name": b.name,
                "props": self.model_dump()
            })


# Specific Node Models
class Person(NodeModel):
    label: ClassVar[str] = "Person"
    name: str
    gender: Optional[str] = None
    education_level: Optional[str] = None
    religious_view: Optional[str] = None


class Community(NodeModel):
    label: ClassVar[str] = "Community"
    name: str
    description: Optional[str] = None


class Location(NodeModel):
    label: ClassVar[str] = "Location"
    name: str
    region: Optional[str] = None


class Religion(NodeModel):
    label: ClassVar[str] = "Religion"
    name: str


class EducationLevel(NodeModel):
    label: ClassVar[str] = "EducationLevel"
    name: str


class Gender(NodeModel):
    label: ClassVar[str] = "Gender"
    name: str


class Sexuality(NodeModel):
    label: ClassVar[str] = "Sexuality"
    name: str


# Specific Relationship Models
class AlsoInvolvedIn(RelationshipModel):
    rel_type: ClassVar[str] = "ALSO_INVOLVED_IN"
    level: Optional[str] = None


class AssociatedWith(RelationshipModel):
    rel_type: ClassVar[str] = "ASSOCIATED_WITH"


class LivesIn(RelationshipModel):
    rel_type: ClassVar[str] = "LIVES_IN"


class OriginallyFrom(RelationshipModel):
    rel_type: ClassVar[str] = "ORIGINALLY_FROM"


class HasReligiousView(RelationshipModel):
    rel_type: ClassVar[str] = "HAS_RELIGIOUS_VIEW"


class HasEducationLevel(RelationshipModel):
    rel_type: ClassVar[str] = "HAS_EDUCATION_LEVEL"


class HasTheGender(RelationshipModel):
    rel_type: ClassVar[str] = "HAS_THE_GENDER"


class LevelOfInvolvement(RelationshipModel):
    rel_type: ClassVar[str] = "LEVEL_OF_INVOLVEMENT"
    level: Optional[str] = None