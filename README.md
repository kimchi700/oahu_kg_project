# Oahu Community Knowledge Graph

A full-stack web application for visualizing and exploring community connections across Oahu, Hawaii using modern web technologies, graph databases, and AI-powered semantic search.

## Overview

This application combines FastAPI, FastHTML, and Dash to create an interactive platform for exploring community relationships through network visualizations and AI-powered search. The system uses Neo4j graph database with vector indexes for semantic search, reducing AI API costs by 71% through Retrieval-Augmented Generation (RAG).

## Key Features

- **Interactive Network Visualization**: Multiple layout algorithms (Spring, Circular, Kamada-Kawai) with Plotly and NetworkX
- **AI-Powered Search**: RAG system using Neo4j vector indexes and Claude API for semantic question answering
- **Real-Time Filtering**: 18 different demographic and structural filters for precise data exploration
- **Professional Architecture**: Object-oriented design with SOLID principles and design patterns
- **Single Server Deployment**: All frameworks running on a single port (8000) for simplified deployment
- **RESTful API**: FastAPI endpoints for programmatic access to graph data and filters

## Technology Stack

### Core Frameworks
- **FastAPI**: High-performance web framework serving as the main application server
- **FastHTML**: Lightweight framework for server-side rendered landing pages
- **Dash by Plotly**: Interactive analytical web applications and dashboards

### Data Layer
- **Neo4j Graph Database**: Graph storage with vector indexes for semantic search
- **NetworkX**: Graph analysis and manipulation
- **Pandas**: Data processing and transformation

### AI/ML
- **Claude API (Anthropic Sonnet 4)**: Advanced language model for question answering
- **Sentence Transformers**: Vector embeddings (all-MiniLM-L6-v2 model)
- **Neo4j Vector Indexes**: Semantic search over relationships and communities

### Visualization
- **Plotly**: Interactive graphs with zoom, pan, and hover interactions
- **Mermaid.js**: Architecture diagrams on about page

## Project Structure

```
project/
├── main.py                 # FastAPI entry point, application assembly
├── config.py              # Configuration (Neo4j, API credentials)
│
├── Frontend & Pages
│   ├── pages.py           # FastHTML landing page
│   ├── about_page.py      # FastHTML about page with architecture diagrams
│   └── dash_app.py        # Dash dashboard (1,377 lines)
│
├── API Layer
│   ├── api_routes.py      # REST API endpoints (/api/*)
│   ├── data_loader.py     # Neo4j data loading utilities
│   └── filters.py         # Filter extraction and validation
│
├── Core Logic (Object-Oriented)
│   ├── neo4j_queries.py   # Neo4jQueryEngine class (533 lines)
│   ├── neo4j_rag.py       # Neo4jRAG class for semantic search (429 lines)
│   └── graph_utils.py     # GraphVisualizer class for network visualization
│
├── Data & Scripts
│   ├── data/              # CSV files with survey data
│   ├── static/            # Static assets (images, CSS)
│   └── scripts/           # Data ingestion scripts (kg_ingest.py, graph_models.py)
│
└── Documentation
    ├── README.md          # This file
    ├── QUICK_START.md     # Quick start guide
    └── PROJECT_SUMMARY.md # Project summary
```

## Architecture

### System Components

```
User (Browser)
    |
    v
FastAPI Server (Port 8000)
    |
    ├── FastHTML Pages (/, /about)
    ├── Dash Dashboard (/dash/)
    └── REST API (/api/*)
        |
        v
Core Business Logic
    |
    ├── Neo4jQueryEngine    - Database queries
    ├── Neo4jRAG            - Semantic search with RAG
    ├── GraphVisualizer     - Network visualization
    └── FilterManager       - Filter management
        |
        v
Data Layer
    |
    ├── Neo4j Graph DB      - Nodes, relationships, vector indexes
    └── Survey CSV Files    - Demographics data
        |
        v
AI Layer
    |
    ├── Sentence Transformers - Generate embeddings
    └── Claude API           - Answer generation
```

### Main Classes

The application uses object-oriented design with 8 main classes:

1. **FastAPIApp** (main.py) - Application entry point and routing
2. **DashApp** (dash_app.py) - Dashboard with filters and visualizations
3. **Neo4jQueryEngine** (neo4j_queries.py) - Database query management
4. **Neo4jRAG** (neo4j_rag.py) - RAG system with vector search
5. **GraphVisualizer** (graph_utils.py) - Network graph visualization
6. **FilterManager** (filters.py) - Filter extraction and validation
7. **Neo4jDatabase** (External) - Graph database
8. **ClaudeAPI** (External) - AI language model

### Design Patterns

- **Facade Pattern**: Simplified interfaces to complex subsystems
- **Strategy Pattern**: Swappable layout algorithms for visualizations
- **Singleton Pattern**: Single RAG instance for resource efficiency
- **Dependency Injection**: Database connections passed to class constructors

## Installation

### Prerequisites

- Python 3.8+
- Neo4j Database (4.4+)
- Anthropic API Key (for Claude)

### Install Dependencies

```bash
pip install fastapi uvicorn dash python-fasthtml pandas networkx neo4j
pip install plotly sentence-transformers anthropic
pip install --break-system-packages python-pptx openpyxl python-docx
```

### Configure Environment

Edit `config.py` with your credentials:

```python
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "your_password"
ANTHROPIC_API_KEY = "sk-ant-api03-..."
```

### Load Data (First Time Only)

```bash
# Optional: Load data into Neo4j
python scripts/kg_ingest.py
```

## Usage

### Start the Application

```bash
python main.py
```

### Access Points

- **Landing Page**: http://localhost:8000/
- **About Page**: http://localhost:8000/about
- **Dashboard**: http://localhost:8000/dash/
- **API Root**: http://localhost:8000/api
- **API Filters**: http://localhost:8000/api/filters
- **API Docs (Swagger)**: http://localhost:8000/docs

### Using the Dashboard

1. Navigate to http://localhost:8000/dash/
2. Apply filters (communities, locations, demographics)
3. Select graph layout algorithm
4. View interactive network visualization
5. Use AI Search Agent to ask questions about the data

### Using the API

```bash
# Get available filter values
curl http://localhost:8000/api/filters

# API returns JSON:
{
  "communities": ["Surfing", "Rock Climbing", ...],
  "locations": ["Hawaii", "California", ...],
  "genders": ["Male", "Female", "Non-binary"],
  ...
}
```

## Features in Detail

### Network Visualization
- Multiple layout algorithms for optimal node positioning
- Interactive zoom, pan, and hover information
- Color-coded nodes by type (Main_Community vs Community)
- Edge labels showing relationship types
- Real-time statistics (nodes, edges, density, average degree)

### AI Search Agent
- Natural language queries about communities and relationships
- Semantic search using Neo4j vector indexes
- Context-aware responses powered by Claude API
- 71% cost reduction through RAG vs. full-context API calls
- Persistent embeddings stored in Neo4j for fast retrieval

### Filtering System
18 different filter categories:
- Communities (19 types)
- Original Location (24 states)
- Current Residence (5 Oahu regions)
- Religion (5 categories)
- Education Level (6 levels)
- Gender (3 options)
- Sexuality (LGBTQ+ identifiers)
- Plus 11 additional demographic filters

## Development

### Adding New Features

**Add a new page:**
```python
# In pages.py or new file
@rt("/new-page")
def get():
    return Titled("New Page", H1("Content"))
```

**Add a new API endpoint:**
```python
# In api_routes.py
@router.get("/new-endpoint")
async def new_endpoint():
    return {"data": "value"}
```

**Modify dashboard:**
```python
# In dash_app.py
# Update layout or add new callbacks
```

### Code Quality

- **Lines of Code**: ~3,330 lines across 11 core files
- **Test Coverage**: Unit tests for core classes
- **Type Hints**: Comprehensive type annotations
- **Documentation**: Docstrings for all public methods
- **SOLID Principles**: Applied throughout
- **Design Patterns**: Facade, Strategy, Singleton, Dependency Injection

## Performance

- **RAG System**: 71% reduction in AI API costs
- **Vector Search**: Sub-second semantic queries over 1000+ relationships
- **Single Server**: All frameworks on one port for efficient deployment
- **Caching**: Filter values and embeddings cached for fast retrieval

## Troubleshooting

### Neo4j Connection Error
```bash
# Verify Neo4j is running
# Check credentials in config.py
# Test connection:
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password')); driver.verify_connectivity()"
```

### Dashboard Not Loading
- Ensure all dependencies are installed
- Check that Neo4j has data loaded
- Verify port 8000 is not in use

### RAG System Not Working
- Verify Anthropic API key is set in config.py
- Check that vector indexes are created in Neo4j
- Run reindexing if needed (see neo4j_rag.py)

## Contributing

1. Follow existing code structure and naming conventions
2. Add docstrings to new functions and classes
3. Use type hints for function parameters and return values
4. Write unit tests for new features
5. Update documentation as needed

## License

This project is for educational and community research purposes.

## Support

For issues, questions, or feature requests, please refer to the project documentation or contact the development team.

## Acknowledgments

Built with modern Python frameworks and best practices for graph database visualization and AI-powered semantic search.
