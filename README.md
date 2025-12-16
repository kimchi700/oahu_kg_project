# Oahu Knowledge Graph Project
An interactive knowledge graph visualization application for exploring and understanding community connections across Oahu, Hawaii. Built with Dash, Plotly, and PyVis to transform community data into dynamic, explorable network visualizations.

## Features

Interactive Network Visualization: Dual visualization modes using Plotly and PyVis for exploring community relationships
Flexible Connection Strategies: Multiple graph construction modes (all-pairs, hub-spoke, sequential, shared values) to reveal different relationship patterns
Dynamic Filtering: Real-time filtering by relationship types and edge categories
Multiple Layout Algorithms: Spring, circular, and Kamada-Kawai layouts for optimal visualization
Community Insights: Visualize connections across locations, organizations, demographics, and social networks throughout Oahu

## Use Cases

Map relationships between community organizations and members
Explore connections across neighborhoods and regions
Analyze collaborative networks and shared resources
Identify community hubs and key connectors
Understand overlap in community initiatives and participation

## Project Structure

```
project/
├── main.py                 # Main application entry point
├── models.py              # Pydantic models for API
├── filters.py             # Filter extraction utilities
├── api_routes.py          # FastAPI REST API endpoints
├── pages.py               # FastHTML landing page
├── about_page.py          # FastHTML about page
├── dash_app.py            # Dash dashboard application
├── data_loader.py         # Neo4j data loading (existing)
├── graph_utils.py         # Graph utilities (existing)
├── callbacks.py           # Filter callbacks (existing)
├── static/                # Static files (images, etc.)
│   └── oahu_background.jpg
└── README.md              # This file
```

##  Quick Start

1. **Install dependencies**:
   ```bash
   pip install fastapi uvicorn dash python-fasthtml pandas networkx neo4j
   ```

2. **Set up static directory**:
   ```bash
   mkdir static
   # Copy your Oahu image to static/oahu_background.jpg
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

4. **Access the application**:
   - Landing Page: http://localhost:8000/
   - About: http://localhost:8000/about
   - Dashboard: http://localhost:8000/dash/
   - API: http://localhost:8000/api
   - API Docs: http://localhost:8000/docs

## Module Descriptions

### `main.py`
- Entry point for the application
- Assembles all components (FastAPI, FastHTML, Dash)
- Handles startup events and data loading
- Configures middleware and static files
- Mounts all applications

### `models.py`
- Contains Pydantic models for API requests/responses
- `GraphRequest`: Model for graph generation requests

### `filters.py`
- Utilities for extracting filter values from data
- `extract_filter_values()`: Extracts unique values for all filter categories

### `api_routes.py`
- FastAPI REST API endpoints
- `/api`: API root endpoint
- `/api/filters`: Get available filter values
- `/api/graph`: Generate graph data (POST)

### `pages.py`
- FastHTML landing page routes
- Home page with hero section and features

### `about_page.py`
- FastHTML about page
- Includes Mermaid architecture diagram
- Technology stack descriptions
- Feature list

### `dash_app.py`
- Dash dashboard application
- Interactive graph visualization
- Filter controls (community, location, religion, gender, etc.)
- Real-time statistics display
- Graph callbacks and updates

## 🔧 Configuration

### Static Files
Place images and other static assets in the `static/` directory. The application serves them at `/static/`.

### Database
The application expects Neo4j to be running and accessible via the `data_loader.py` configuration.

## Architecture

```
┌─────────────────────────────────────────────┐
│           FastAPI (Port 8000)               │
│  ┌─────────┐  ┌──────────┐  ┌───────────┐  │
│  │ FastHTML│  │   Dash   │  │ REST API  │  │
│  │  Pages  │  │Dashboard │  │ Endpoints │  │
│  └─────────┘  └──────────┘  └───────────┘  │
└─────────────────┬───────────────────────────┘
                  │
          ┌───────┴────────┐
          │  Neo4j + NetworkX  │
          └────────────────┘
```

## Key Features

1. **Modular Design**: Each component in its own file
2. **Single Server**: All frameworks on port 8000
3. **Clean Separation**: API, UI, and visualization separated
4. **Easy Maintenance**: Update components independently
5. **Scalable**: Add new pages/routes easily

##  Adding New Features

### Add a new FastHTML page:
1. Edit `pages.py` or create a new page module
2. Add route with `@rt("/your-route")`
3. Return FastHTML components

### Add a new API endpoint:
1. Edit `api_routes.py`
2. Add route with `@router.get()` or `@router.post()`
3. Return JSON data

### Modify Dash dashboard:
1. Edit `dash_app.py`
2. Update layout or callbacks
3. Changes take effect on restart

