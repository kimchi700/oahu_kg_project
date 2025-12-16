"""
pages.py - FastHTML page routes
"""

from fasthtml.common import *
from about_page import add_about_route


def create_pages():
    """Create FastHTML app with all page routes"""
    fasthtml_app, rt = fast_app()
    
    # Add about page route
    add_about_route(rt)
    
    @rt("/")
    def get():
        """FastHTML landing page"""
        return Titled("Oahu Community Knowledge Graph",
            Style("""
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
                    margin: 0; padding: 0;
                    color: #1a1a1a;
                    overflow-x: hidden;
                }
                
                /* Hero Section with Background Image */
                .hero {
                    position: relative;
                    height: 100vh;
                    display: flex;
                    align-items: flex-start;
                    padding-top: 15vh;
                    justify-content: center;
                    text-align: center;
                    color: #1a1a1a;
                    overflow: hidden;
                }
                .hero::before {
                    content: '';
                    position: absolute;
                    top: 0; left: 0; right: 0; bottom: 0;
                    background: url('/static/oahu_background.jpg') center/cover no-repeat;
                    z-index: -1;
                }
                .hero-content {
                    width: 100%;
                    max-width: none;
                    padding: 60px 80px;
                    background: rgba(255, 255, 255, 0.5);
                    animation: fadeInUp 1s ease-out;
                }
                .hero h1 { 
                    font-size: 64px; 
                    font-weight: 800;
                    margin-bottom: 20px; 
                    color: #2c3e50;
                    letter-spacing: -1px;
                }
                .hero p { 
                    font-size: 24px; 
                    margin-bottom: 40px; 
                    font-weight: 300;
                    color: #333;
                    max-width: 800px;
                    margin-left: auto;
                    margin-right: auto;
                }
                
                /* CTA Buttons */
                .cta-buttons {
                    display: flex;
                    gap: 20px;
                    justify-content: center;
                    flex-wrap: wrap;
                }
                .btn-primary {
                    display: inline-block;
                    padding: 16px 40px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 50px;
                    font-weight: 600;
                    font-size: 18px;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
                }
                .btn-primary:hover { 
                    background: #764ba2;
                    transform: translateY(-3px);
                    box-shadow: 0 6px 25px rgba(102, 126, 234, 0.4);
                }
                .btn-secondary {
                    display: inline-block;
                    padding: 16px 40px;
                    background: transparent;
                    color: #667eea;
                    text-decoration: none;
                    border-radius: 50px;
                    border: 2px solid #667eea;
                    font-weight: 600;
                    font-size: 18px;
                    transition: all 0.3s ease;
                }
                .btn-secondary:hover { 
                    background: #667eea;
                    color: white;
                    transform: translateY(-3px);
                }
                
                /* Features Section */
                .features {
                    padding: 100px 20px;
                    background: #f8f9fa;
                }
                .features h2 {
                    text-align: center;
                    font-size: 42px;
                    margin-bottom: 60px;
                    color: #2c3e50;
                    font-weight: 700;
                }
                .feature-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
                    gap: 40px;
                    max-width: 1200px;
                    margin: 0 auto;
                }
                .feature-card {
                    padding: 40px;
                    background: white;
                    border-radius: 20px;
                    text-align: center;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.07);
                    border: 1px solid rgba(0,0,0,0.05);
                }
                .feature-card:hover {
                    transform: translateY(-8px);
                    box-shadow: 0 12px 24px rgba(102, 126, 234, 0.15);
                }
                .feature-card h3 { 
                    color: #2c3e50;
                    font-size: 24px;
                    margin-bottom: 15px;
                    font-weight: 600;
                }
                .feature-card p {
                    color: #666;
                    line-height: 1.6;
                    margin-bottom: 20px;
                }
                .feature-link {
                    color: #667eea;
                    text-decoration: none;
                    font-weight: 600;
                    font-size: 16px;
                    display: inline-flex;
                    align-items: center;
                    gap: 5px;
                }
                .feature-link:hover {
                    color: #764ba2;
                }
                
                /* Scroll Down Indicator */
                .scroll-indicator {
                    position: absolute;
                    bottom: 30px;
                    left: 50%;
                    transform: translateX(-50%);
                    animation: bounce 2s infinite;
                }
                .scroll-indicator::after {
                    content: '↓';
                    font-size: 32px;
                    color: #667eea;
                    text-shadow: 0 2px 4px rgba(255, 255, 255, 0.8);
                }
                
                /* Animations */
                @keyframes fadeInUp {
                    from {
                        opacity: 0;
                        transform: translateY(30px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
                @keyframes bounce {
                    0%, 20%, 50%, 80%, 100% {
                        transform: translateX(-50%) translateY(0);
                    }
                    40% {
                        transform: translateX(-50%) translateY(-10px);
                    }
                    60% {
                        transform: translateX(-50%) translateY(-5px);
                    }
                }
                
                /* Responsive */
                @media (max-width: 768px) {
                    .hero { padding-top: 10vh; }
                    .hero-content { padding: 40px 30px; }
                    .hero h1 { font-size: 40px; }
                    .hero p { font-size: 18px; }
                    .cta-buttons { flex-direction: column; }
                    .features h2 { font-size: 32px; }
                }
            """),
            
            # Hero Section
            Div(
                Div(
                    H1("Oahu Community Knowledge Graph"),
                    P("Explore connections across Oahu's diverse communities through interactive visualizations and powerful data insights"),
                    Div(
                        A("Launch Dashboard →", href="/dash/", cls="btn-primary"),
                        A("API Documentation", href="/docs", cls="btn-secondary"),
                        cls="cta-buttons"
                    ),
                    cls="hero-content"
                ),
                Div(cls="scroll-indicator"),
                cls="hero"
            ),
            
            # Features Section
            Div(
                H2("Three Powerful Interfaces"),
                Div(
                    Div(
                        H3("Interactive Dashboard"),
                        P("Visualize community connections with real-time filtering, multiple layout algorithms, and detailed network statistics powered by Dash and Plotly."),
                        A("Launch Dashboard →", href="/dash/", cls="feature-link"),
                        cls="feature-card"
                    ),
                    Div(
                        H3("REST API"),
                        P("Programmatic access to knowledge graph data with flexible filtering, custom layouts, and comprehensive network metrics for integration into your applications."),
                        A("View API Docs →", href="/docs", cls="feature-link"),
                        cls="feature-card"
                    ),
                    Div(
                        H3("Fast Landing Pages"),
                        P("Lightning-fast, responsive pages built with FastHTML delivering information instantly without the overhead of heavy JavaScript frameworks."),
                        A("About This Project →", href="/about", cls="feature-link"),
                        cls="feature-card"
                    ),
                    cls="feature-grid"
                ),
                cls="features"
            )
        )
    
    return fasthtml_app