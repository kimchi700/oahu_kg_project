"""
models.py - Pydantic models for API requests/responses
"""

from pydantic import BaseModel
from typing import List, Optional


class GraphRequest(BaseModel):
    """Request model for graph generation"""
    layout: str = "spring"
    communities: Optional[List[str]] = []
    locations: Optional[List[str]] = []
    residences: Optional[List[str]] = []
    religions: Optional[List[str]] = []
    education_levels: Optional[List[str]] = []
    genders: Optional[List[str]] = []
    sexualities: Optional[List[str]] = []
