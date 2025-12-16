"""
main.py - Main application entry point
Assembles FastAPI, FastHTML, and Dash into a unified application
"""

import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.wsgi import WSGIMiddleware

# Import custom modules
from data_loader import load_triples_from_neo4j
from filters import extract_filter_values
from api_routes import router as api_router, set_data
from pages import create_pages
from dash_app import create_dash_app


# ==========================================
# Create FastAPI Application
# ==========================================

app = FastAPI(title="Oahu Community Knowledge Graph API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# Data Loading
# ==========================================

triples_df = None
filter_values = None


@app.on_event("startup")
async def startup_event():
    """Load data from Neo4j on startup"""
    global triples_df, filter_values
    
    print("Loading data from Neo4j...")
    triples_df = load_triples_from_neo4j()
    triples_df['predicate'] = triples_df['predicate'].str.upper()
    print(f"Loaded {len(triples_df)} triples")
    
    filter_values = extract_filter_values(triples_df)
    print("Extracted filter values")
    
    # Share data with API routes module
    set_data(triples_df, filter_values)


# ==========================================
# Include API Routes
# ==========================================

app.include_router(api_router)


# ==========================================
# Test Route
# ==========================================

@app.get("/test-routes")
async def test_routes():
    """Debug endpoint to list all routes"""
    return [route.path for route in app.routes]


# ==========================================
# Mount Static Files
# ==========================================

static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# ==========================================
# Create and Mount Dash App
# ==========================================

print("Creating Dash application...")
dash_app = create_dash_app()
app.mount("/dash", WSGIMiddleware(dash_app.server))
print("Dash app mounted at /dash/")


# ==========================================
# Create and Mount FastHTML Pages
# ==========================================

print("Creating FastHTML pages...")
fasthtml_app = create_pages()
app.mount("/", fasthtml_app)
print("FastHTML pages mounted at /")


# ==========================================
# Run Server
# ==========================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("Oahu Community Knowledge Graph - FULL HYBRID")
    print("   FastAPI + FastHTML + Dash")
    print("="*70)
    print("\nAccess Points:")
    print("   Landing Page (FastHTML): http://localhost:8000/")
    print("   About (FastHTML):        http://localhost:8000/about")
    print("   Dash App:                http://localhost:8000/dash/")
    print("   API Root:                http://localhost:8000/api")
    print("   API Filters:             http://localhost:8000/api/filters")
    print("   API Docs (Swagger):      http://localhost:8000/docs")
    print("\nAll three frameworks running on ONE server (port 8000)!\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)