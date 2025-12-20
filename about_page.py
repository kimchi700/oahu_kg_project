"""
about_page.py - About page content for FastHTML
Updated with current tech stack including RAG system
"""

from fasthtml.common import *


def add_about_route(rt):
    """Add the about page route to the FastHTML router"""
    
    @rt("/about")
    def get():
        """About page with architecture diagram"""
        return Titled("About This Project",
            # Mermaid.js CDN
            Script(src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"),
            Script("mermaid.initialize({ startOnLoad: true, theme: 'default' });"),
            
            Style("""
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    margin: 0; 
                    padding: 0;
                    background: #f8f9fa;
                    color: #2c3e50;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 40px 20px;
                }
                .back-link {
                    display: inline-block;
                    color: #667eea;
                    text-decoration: none;
                    font-weight: 600;
                    margin-bottom: 30px;
                    transition: color 0.3s;
                }
                .back-link:hover {
                    color: #764ba2;
                }
                h1 {
                    font-size: 48px;
                    font-weight: 800;
                    margin-bottom: 20px;
                    color: #2c3e50;
                }
                .intro {
                    font-size: 20px;
                    color: #666;
                    line-height: 1.6;
                    margin-bottom: 50px;
                }
                .section {
                    background: white;
                    padding: 40px;
                    border-radius: 20px;
                    margin-bottom: 30px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.07);
                }
                .section h2 {
                    font-size: 32px;
                    font-weight: 700;
                    margin-bottom: 20px;
                    color: #2c3e50;
                }
                .diagram-container {
                    background: white;
                    padding: 40px;
                    border-radius: 20px;
                    margin-bottom: 30px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.07);
                    text-align: center;
                }
                .mermaid {
                    background: #fafafa;
                    padding: 30px;
                    border-radius: 15px;
                }
                .tech-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-top: 30px;
                }
                .tech-card {
                    background: #f8f9fa;
                    padding: 25px;
                    border-radius: 15px;
                    border-left: 4px solid #667eea;
                }
                .tech-card h3 {
                    color: #667eea;
                    font-size: 20px;
                    margin-bottom: 10px;
                }
                .tech-card p {
                    color: #666;
                    line-height: 1.6;
                    margin: 0;
                }
                .features-list {
                    list-style: none;
                    padding: 0;
                }
                .features-list li {
                    padding: 12px 0;
                    border-bottom: 1px solid #eee;
                    display: flex;
                    align-items: center;
                }
                .features-list li:last-child {
                    border-bottom: none;
                }
                .features-list li::before {
                    content: '✓';
                    color: #667eea;
                    font-weight: bold;
                    margin-right: 15px;
                    font-size: 18px;
                }
                .stats-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-top: 20px;
                }
                .stat-card {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 25px;
                    border-radius: 15px;
                    color: white;
                    text-align: center;
                }
                .stat-card h3 {
                    font-size: 36px;
                    margin: 0 0 10px 0;
                    font-weight: 800;
                }
                .stat-card p {
                    margin: 0;
                    opacity: 0.9;
                }
            """),
            
            Div(
                A("← Back to Home", href="/", cls="back-link"),
                
                H1("🌺 About This Project"),
                
                P("A full-stack web application that visualizes Oahu community connections using modern web technologies, graph databases, and AI-powered semantic search with RAG (Retrieval-Augmented Generation).", 
                  cls="intro"),
                
                # Architecture Diagram
                Div(
                    H2("System Architecture"),
                    Div(
                        """
                        graph TB
                            subgraph Client["🌐 Client Layer"]
                                Browser["Web Browser<br/>Chrome, Safari, Firefox"]
                            end
                            
                            subgraph Server["⚙️ Application Server - Port 8000"]
                                Main["main.py<br/>FastAPI Entry Point"]
                                Pages["pages.py + about_page.py<br/>FastHTML Pages"]
                                DashApp["dash_app.py<br/>Interactive Dashboard"]
                                API["api_routes.py<br/>REST API Endpoints"]
                            end
                            
                            subgraph Core["🔧 Core Logic"]
                                Queries["neo4j_queries.py<br/>Database Queries"]
                                RAG["neo4j_rag.py<br/>RAG System"]
                                Utils["graph_utils.py<br/>Visualization"]
                                Filters["filters.py<br/>Filter Extraction"]
                                Loader["data_loader.py<br/>Data Loading"]
                            end
                            
                            subgraph Data["💾 Data Layer"]
                                Neo4j["Neo4j Graph DB<br/>+ Vector Indexes"]
                                Survey["Survey Data<br/>CSV Files"]
                            end
                            
                            subgraph AI["🤖 AI Layer"]
                                Embedding["Sentence Transformers<br/>all-MiniLM-L6-v2"]
                                Claude["Claude API<br/>Anthropic Sonnet 4"]
                            end
                            
                            subgraph Viz["📊 Visualization"]
                                Plotly["Plotly<br/>Interactive Graphs"]
                                NetworkX["NetworkX<br/>Graph Analysis"]
                            end
                            
                            %% Client connections
                            Browser -->|HTTP| Main
                            
                            %% Server routing
                            Main -->|"/ routes"| Pages
                            Main -->|"/dash routes"| DashApp
                            Main -->|"/api routes"| API
                            
                            %% Page rendering
                            Pages -.->|Static HTML| Browser
                            DashApp -.->|Interactive UI| Browser
                            
                            %% Core logic connections
                            DashApp --> Queries
                            DashApp --> RAG
                            DashApp --> Utils
                            API --> Loader
                            API --> Filters
                            
                            %% Data connections
                            Queries -->|Cypher Queries| Neo4j
                            Loader -->|Load Triples| Neo4j
                            RAG -->|Vector Search| Neo4j
                            Loader -->|Read CSV| Survey
                            
                            %% AI connections
                            RAG -->|Generate Embeddings| Embedding
                            RAG -->|Semantic Search| Neo4j
                            RAG -->|Send Context| Claude
                            Claude -.->|AI Response| DashApp
                            
                            %% Visualization
                            Utils --> NetworkX
                            Utils --> Plotly
                            Plotly -.->|Charts| Browser
                            
                            %% Styling
                            classDef mainStyle fill:#667eea,stroke:#333,stroke-width:3px,color:#fff
                            classDef pageStyle fill:#764ba2,stroke:#333,stroke-width:3px,color:#fff
                            classDef dashStyle fill:#00d4ff,stroke:#333,stroke-width:3px,color:#000
                            classDef apiStyle fill:#ff6b6b,stroke:#333,stroke-width:3px,color:#fff
                            classDef coreStyle fill:#4ecdc4,stroke:#333,stroke-width:3px,color:#000
                            classDef dbStyle fill:#008CC1,stroke:#333,stroke-width:3px,color:#fff
                            classDef aiStyle fill:#f39c12,stroke:#333,stroke-width:3px,color:#000
                            classDef vizStyle fill:#3F4F75,stroke:#333,stroke-width:3px,color:#fff
                            classDef clientStyle fill:#34495e,stroke:#333,stroke-width:3px,color:#fff
                            
                            class Main mainStyle
                            class Pages pageStyle
                            class DashApp dashStyle
                            class API apiStyle
                            class Queries,RAG,Utils,Filters,Loader coreStyle
                            class Neo4j,Survey dbStyle
                            class Embedding,Claude aiStyle
                            class Plotly,NetworkX vizStyle
                            class Browser clientStyle
                        """,
                        cls="mermaid"
                    ),
                    cls="diagram-container"
                ),
                
                # Tech Stack Stats
                Div(
                    H2("By The Numbers"),
                    Div(
                        Div(
                            H3("11"),
                            P("Core Python Files"),
                            cls="stat-card"
                        ),
                        Div(
                            H3("3,330"),
                            P("Lines of Code"),
                            cls="stat-card"
                        ),
                        Div(
                            H3("71%"),
                            P("Cost Reduction with RAG"),
                            cls="stat-card"
                        ),
                        Div(
                            H3("3"),
                            P("Frameworks (FastAPI, FastHTML, Dash)"),
                            cls="stat-card"
                        ),
                        cls="stats-grid"
                    ),
                    cls="section"
                ),
                
                # Class Relationships Diagram
                Div(
                    H2("Class Relationships & Architecture"),
                    P("Object-oriented architecture showing how the main classes interact with each other.", style="margin-bottom: 20px; color: #666;"),
                    Div(
                        """
                        classDiagram
                            class DashApp {
                                +create_dash_app()
                                +update_graph()
                                +ai_search()
                            }
                            
                            class FastAPIApp {
                                +route_to_pages()
                                +route_to_dash()
                                +route_to_api()
                            }
                            
                            class Neo4jQueryEngine {
                                -driver
                                +query_graph_with_filters()
                                +get_survey_data()
                                +prepare_context()
                            }
                            
                            class Neo4jRAG {
                                -driver
                                -model
                                +index_relationships()
                                +retrieve_relevant_context()
                                +get_stats()
                            }
                            
                            class GraphVisualizer {
                                -graph
                                -positions
                                +build_graph()
                                +calculate_layout()
                                +create_plotly_figure()
                            }
                            
                            class FilterManager {
                                -df
                                -filter_values
                                +extract_all_filters()
                                +validate_filter_values()
                            }
                            
                            class Neo4jDatabase {
                                &lt;&lt;external&gt;&gt;
                            }
                            
                            class ClaudeAPI {
                                &lt;&lt;external&gt;&gt;
                            }
                            
                            FastAPIApp --> DashApp
                            DashApp --> Neo4jQueryEngine
                            DashApp --> Neo4jRAG
                            DashApp --> GraphVisualizer
                            DashApp --> FilterManager
                            Neo4jQueryEngine --> Neo4jDatabase
                            Neo4jRAG --> Neo4jDatabase
                            Neo4jRAG --> ClaudeAPI
                            FilterManager --> Neo4jQueryEngine
                            GraphVisualizer ..> Neo4jQueryEngine
                        """,
                        cls="mermaid"
                    ),
                    cls="diagram-container"
                ),
                
                # Data Flow Diagram
                Div(
                    H2("Data Flow - User Interactions"),
                    P("How data flows when users interact with the dashboard and AI search.", style="margin-bottom: 20px; color: #666;"),
                    Div(
                        """
                        flowchart LR
                            User([User])
                            Dashboard[Dashboard]
                            AISearch[AI Search]
                            FilterMgr[FilterManager]
                            QueryEngine[QueryEngine]
                            Neo4j[(Neo4j)]
                            Visualizer[Visualizer]
                            RAG[RAG System]
                            Claude[Claude API]
                            
                            User -->|Select Filters| Dashboard
                            User -->|Ask Question| AISearch
                            Dashboard --> FilterMgr
                            FilterMgr --> QueryEngine
                            QueryEngine --> Neo4j
                            Neo4j --> Visualizer
                            Visualizer --> Dashboard
                            Dashboard --> User
                            AISearch --> RAG
                            RAG --> Neo4j
                            RAG --> Claude
                            Claude --> AISearch
                            AISearch --> User
                        """,
                        cls="mermaid"
                    ),
                    cls="diagram-container"
                ),
                
                # Technology Stack
                Div(
                    H2("Technology Stack"),
                    Div(
                        Div(
                            H3("FastAPI"),
                            P("High-performance Python web framework serving as the main application server. Routes requests to FastHTML pages, Dash dashboard, and REST API endpoints on a single port."),
                            cls="tech-card"
                        ),
                        Div(
                            H3("FastHTML"),
                            P("Lightweight Python framework for building fast, SEO-friendly landing pages. Renders server-side HTML for optimal performance without heavy JavaScript."),
                            cls="tech-card"
                        ),
                        Div(
                            H3("Dash by Plotly"),
                            P("Python framework for building interactive analytical web applications. Powers the main dashboard with real-time filtering, multiple graph layouts, and network statistics."),
                            cls="tech-card"
                        ),
                        Div(
                            H3("Neo4j Graph Database"),
                            P("Graph database storing community relationships as nodes and edges. Enhanced with vector indexes for semantic search, enabling efficient querying of complex network patterns."),
                            cls="tech-card"
                        ),
                        Div(
                            H3("RAG System (neo4j_rag.py)"),
                            P("Retrieval-Augmented Generation system using Neo4j's vector indexes. Performs semantic search over relationships and communities, reducing API costs by 71% while improving answer quality."),
                            cls="tech-card"
                        ),
                        Div(
                            H3("Claude API (Anthropic)"),
                            P("Advanced AI language model powering the AI Search Agent. Receives focused context from RAG system to provide accurate, relevant answers about community connections and demographics."),
                            cls="tech-card"
                        ),
                        Div(
                            H3("NetworkX"),
                            P("Python library for graph analysis and manipulation. Processes Neo4j data to calculate network metrics, apply layout algorithms, and prepare visualizations."),
                            cls="tech-card"
                        ),
                        Div(
                            H3("Plotly"),
                            P("Interactive graphing library creating dynamic network visualizations with zoom, pan, and hover interactions. Renders the knowledge graph directly in the browser."),
                            cls="tech-card"
                        ),
                        Div(
                            H3("Sentence Transformers"),
                            P("Creates vector embeddings for semantic search using the all-MiniLM-L6-v2 model. Generates 384-dimensional embeddings for relationships and communities."),
                            cls="tech-card"
                        ),
                        cls="tech-grid"
                    ),
                    cls="section"
                ),
                
                # Key Features
                Div(
                    H2("Key Features"),
                    Ul(
                        Li("AI-powered search with RAG using Neo4j vector indexes"),
                        Li("71% cost reduction in AI API usage through semantic search"),
                        Li("18 different demographic and structural filters"),
                        Li("Multiple graph layout algorithms (Spring, Circular, Kamada-Kawai)"),
                        Li("Real-time network statistics (nodes, edges, density, average degree)"),
                        Li("Interactive visualizations with zoom, pan, and hover details"),
                        Li("RESTful API for programmatic access to graph data"),
                        Li("Responsive design working across desktop and mobile devices"),
                        Li("Single-server architecture - all frameworks on port 8000"),
                        Li("Persistent vector embeddings in Neo4j for fast retrieval"),
                        cls="features-list"
                    ),
                    cls="section"
                ),
                
                # File Structure
                Div(
                    H2("Code Architecture"),
                    P("The application uses object-oriented programming with clear separation of concerns:", style="margin-bottom: 15px;"),
                    P("📦 11 core Python files (~3,330 lines) organized into 8 main classes:", style="margin-bottom: 20px; font-weight: 600;"),
                    Ul(
                        Li("main.py - FastAPI application entry point (FastAPIApp)"),
                        Li("pages.py, about_page.py - FastHTML landing and about pages"),
                        Li("dash_app.py - Interactive Dash dashboard (DashApp - 1,377 lines)"),
                        Li("api_routes.py - REST API endpoints"),
                        Li("neo4j_queries.py - Neo4jQueryEngine class for database queries (533 lines)"),
                        Li("neo4j_rag.py - Neo4jRAG class for semantic search with RAG (429 lines)"),
                        Li("graph_utils.py - GraphVisualizer class for network visualizations"),
                        Li("data_loader.py - Data loading utilities"),
                        Li("filters.py - FilterManager class for filter extraction and validation"),
                        Li("config.py - Configuration and credentials"),
                        cls="features-list"
                    ),
                    P("🏗️ Design Patterns: Facade, Strategy, Singleton, Dependency Injection", 
                      style="margin-top: 20px; color: #667eea; font-weight: 600;"),
                    P("✨ SOLID Principles applied throughout for maintainability and testability",
                      style="color: #666; margin-top: 10px;"),
                    cls="section"
                ),
                
                cls="container"
            )
        )