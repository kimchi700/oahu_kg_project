"""
about_page.py - About page content for FastHTML
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
                /* Make Mermaid subgraph labels more readable with white boxes */
                .mermaid .cluster rect {
                    fill: #f8f9fa !important;
                    stroke: #667eea !important;
                    stroke-width: 2px !important;
                }
                .mermaid .cluster text {
                    fill: #2c3e50 !important;
                    font-weight: 700 !important;
                    font-size: 15px !important;
                }
                .mermaid .cluster .label-container {
                    background-color: white !important;
                }
                .mermaid .cluster-label text {
                    background-color: white !important;
                    padding: 8px 16px !important;
                    border-radius: 6px !important;
                    font-weight: 700 !important;
                    font-size: 15px !important;
                }
                .mermaid text.clusterLabel {
                    background-color: white !important;
                    padding: 8px 16px !important;
                    border-radius: 6px !important;
                    font-weight: 700 !important;
                    font-size: 15px !important;
                    fill: #2c3e50 !important;
                }
                /* Make edge labels more readable */
                .mermaid .edgeLabel {
                    background-color: white !important;
                    padding: 4px 8px !important;
                    border-radius: 4px !important;
                    font-size: 12px !important;
                }
                .mermaid .edgeLabel rect {
                    fill: white !important;
                    stroke: #ddd !important;
                    stroke-width: 1px !important;
                }
                .mermaid .edgeLabel span {
                    background-color: white !important;
                    padding: 4px 8px !important;
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
            """),
            
            Div(
                A("← Back to Home", href="/", cls="back-link"),
                
                H1("🌺 About This Project"),
                
                P("The Oahu Community Knowledge Graph is a full-stack web application that visualizes community connections across Oahu using modern web technologies and graph database architecture.", 
                  cls="intro"),
                
                # Architecture Diagram
                Div(
                    H2("Architecture Stack"),
                    Div(
                        """
                        graph TB
                            subgraph Client["🌐 Client Layer"]
                                Browser["Web Browser"]
                            end
                            
                            subgraph Server["⚙️ Application Server - Port 8000"]
                                FastAPI["FastAPI<br/>Main App"]
                                FastHTML["FastHTML<br/>Pages"]
                                Dash["Dash<br/>Dashboard"]
                            end
                            
                            subgraph Data["💾 Data Layer"]
                                Neo4j["Neo4j<br/>Graph DB"]
                                NetworkX["NetworkX<br/>Processing"]
                            end
                            
                            subgraph Viz["📊 Visualization"]
                                Plotly["Plotly<br/>Charts"]
                            end
                            
                            Browser -->|"HTTP"| FastAPI
                            FastAPI -->|"/ routes"| FastHTML
                            FastAPI -->|"/dash routes"| Dash
                            FastAPI -->|"/api/* routes"| FastAPI
                            
                            FastHTML -.->|"Static HTML"| Browser
                            Dash -->|"Uses"| Plotly
                            Plotly -.->|"Interactive"| Browser
                            
                            FastAPI -->|"Queries"| Neo4j
                            Dash -->|"Queries"| Neo4j
                            Neo4j -->|"Data"| NetworkX
                            NetworkX -->|"Analysis"| Plotly
                            
                            classDef apiStyle fill:#667eea,stroke:#333,stroke-width:3px,color:#fff
                            classDef htmlStyle fill:#764ba2,stroke:#333,stroke-width:3px,color:#fff
                            classDef dashStyle fill:#00d4ff,stroke:#333,stroke-width:3px,color:#000
                            classDef dbStyle fill:#008CC1,stroke:#333,stroke-width:3px,color:#fff
                            classDef vizStyle fill:#3F4F75,stroke:#333,stroke-width:3px,color:#fff
                            classDef clientStyle fill:#34495e,stroke:#333,stroke-width:3px,color:#fff
                            
                            class FastAPI apiStyle
                            class FastHTML htmlStyle
                            class Dash dashStyle
                            class Neo4j,NetworkX dbStyle
                            class Plotly vizStyle
                            class Browser clientStyle
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
                            P("High-performance Python web framework providing RESTful API endpoints, CORS support, and application routing. Handles all HTTP requests and coordinates between different frameworks."),
                            cls="tech-card"
                        ),
                        Div(
                            H3("FastHTML"),
                            P("Lightweight Python framework for building fast, SEO-friendly landing pages without heavy JavaScript. Renders server-side HTML for optimal performance and simplicity."),
                            cls="tech-card"
                        ),
                        Div(
                            H3("Dash by Plotly"),
                            P("Python framework for building interactive analytical web applications. Powers the main dashboard with real-time filtering, graph layouts, and network statistics."),
                            cls="tech-card"
                        ),
                        Div(
                            H3("Neo4j"),
                            P("Graph database storing community relationships as nodes and edges. Enables efficient querying of complex network connections and community patterns."),
                            cls="tech-card"
                        ),
                        Div(
                            H3("NetworkX"),
                            P("Python library for graph analysis and manipulation. Processes Neo4j data to calculate network metrics, apply layout algorithms, and prepare visualizations."),
                            cls="tech-card"
                        ),
                        Div(
                            H3("Plotly"),
                            P("Interactive graphing library creating dynamic network visualizations with zoom, pan, and hover interactions. Renders the knowledge graph in the browser."),
                            cls="tech-card"
                        ),
                        cls="tech-grid"
                    ),
                    cls="section"
                ),
                
                # Features
                Div(
                    H2("Key Features"),
                    Ul(
                        Li("Multi-dimensional filtering across community, location, religion, education, gender, and sexuality"),
                        Li("Multiple graph layout algorithms (Spring, Circular, Kamada-Kawai)"),
                        Li("Real-time network statistics (nodes, edges, density, average degree)"),
                        Li("RESTful API for programmatic access to graph data"),
                        Li("Interactive visualizations with zoom, pan, and hover details"),
                        Li("Responsive design working across desktop and mobile devices"),
                        Li("Single-server architecture running all frameworks on port 8000"),
                        cls="features-list"
                    ),
                    cls="section"
                ),
                
                cls="container"
            )
        )
