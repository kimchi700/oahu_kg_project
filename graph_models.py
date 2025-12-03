# graph_models.py

from __future__ import annotations
from pydantic import BaseModel
from typing import Any, Dict, ClassVar
from neo4j import Driver


class NodeModel(BaseModel):
    primary_key: ClassVar[str] = "name"
    label: ClassVar[str] | None = None

    name: str

    def get_label(self) -> str:
        return self.label or self.__class__.__name__

    def pk_value(self):
        return getattr(self, self.primary_key)

    def to_properties(self) -> Dict[str, Any]:
        return self.model_dump(exclude={self.primary_key})

    def merge(self, driver: Driver):
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
    rel_type: ClassVar[str] | None = None

    def get_rel_type(self):
        return self.rel_type or self.__class__.__name__.upper()

    def connect(self, driver: Driver, a: NodeModel, b: NodeModel):
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
