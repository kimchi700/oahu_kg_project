"""
api_routes.py - FastAPI REST API endpoints
"""

from fastapi import APIRouter
import networkx as nx
# from models import GraphRequest
from graph_utils import create_network_graph


# Create router
router = APIRouter(prefix="/api", tags=["api"])

# Global data storage (will be set from main app)
triples_df = None
filter_values = None


def set_data(df, filters):
    """Set the global data references"""
    global triples_df, filter_values
    triples_df = df
    filter_values = filters


@router.get("")
async def api_root():
    """API root endpoint"""
    return {
        "message": "Oahu Community Knowledge Graph API",
        "version": "3.0",
        "endpoints": {
            "filters": "/api/filters",
            "graph": "/api/graph (POST)",
            "docs": "/api/docs"
        }
    }


@router.get("/filters")
async def get_filters():
    """Get all available filter values"""
    if filter_values is None:
        return {"error": "Data not loaded yet"}
    
    predicates = sorted(triples_df['predicate'].dropna().unique().astype(str))
    
    return {
        "communities": filter_values['communities'],
        "locations": filter_values['locations'],
        "residences": filter_values['residence'],
        "religions": filter_values['religions'],
        "education_levels": filter_values['education_levels'],
        "genders": filter_values['genders'],
        "sexualities": filter_values['sexualities'],
        "predicates": predicates
    }

