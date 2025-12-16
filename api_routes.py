"""
api_routes.py - FastAPI REST API endpoints
"""

from fastapi import APIRouter
import networkx as nx
from models import GraphRequest
from callbacks import filter_by_node_types
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


@router.post("/graph")
async def get_graph(request: GraphRequest):
    """Generate graph data based on filters"""
    if triples_df is None:
        return {"error": "Data not loaded yet"}
    
    # Filter dataframe
    filtered_df = filter_by_node_types(
        triples_df,
        communities=request.communities,
        locations=request.locations,
        residences=request.residences,
        religions=request.religions,
        education_levels=request.education_levels,
        genders=request.genders,
        sexualities=request.sexualities
    )
    
    predicates = filtered_df['predicate'].unique()
    G = create_network_graph(filtered_df, request.layout, predicates, [])
    
    # Calculate layout positions
    if request.layout == 'spring':
        pos = nx.spring_layout(G, k=0.5, iterations=50)
    elif request.layout == 'circular':
        pos = nx.circular_layout(G)
    elif request.layout == 'kamada':
        pos = nx.kamada_kawai_layout(G)
    else:
        pos = nx.spring_layout(G)
    
    # Prepare nodes
    nodes = []
    for node in G.nodes():
        x, y = pos[node] if node in pos else (0, 0)
        nodes.append({
            "id": node,
            "label": node,
            "x": float(x),
            "y": float(y),
            "degree": G.degree(node),
            "size": 10 + G.degree(node) * 3
        })
    
    # Prepare edges
    edges = []
    for u, v, data in G.edges(data=True):
        edges.append({
            "source": u,
            "target": v,
            "edge_types": data.get('edge_types', []),
            "weight": data.get('weight', 1)
        })
    
    # Calculate stats
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    density = nx.density(G) if num_nodes > 0 else 0
    avg_degree = (2 * num_edges / num_nodes) if num_nodes > 0 else 0
    
    return {
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "nodes": num_nodes,
            "edges": num_edges,
            "density": round(density, 3),
            "avg_degree": round(avg_degree, 2)
        }
    }
