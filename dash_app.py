"""
dash_app.py - Dash dashboard application
Visualizes only Community and Main_Community nodes, uses Attributes for filtering
Uses DIRECT Neo4j Cypher queries for dynamic filtering
Includes AI Search Agent tab
"""

from dash import Dash, dcc, html as dash_html, Input, Output, State
import networkx as nx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from collections import defaultdict
from neo4j_queries import get_query_engine
from graph_utils import create_network_graph, create_plotly_graph
from neo4j_rag import get_neo4j_rag

COMPACT_DROPDOWN_STYLE = {
    "fontSize": "12px",
    "minHeight": "34px",
}



survey_df = pd.read_csv('data/data_preprcd_12_18.csv')

def apply_filters_to_survey(survey_df, communities=None, residences=None, locations=None, 
                            education_levels=None, religions=None, genders=None, sexualities=None,
                            community_scales=None, aloha_spirits=None, hawaiian_cultures=None,
                            us_born=None, country=None, stay_on_island=None,
                            relationship_status=None, age_ranges=None, occupations=None):
    """Apply the same filters used for the graph to the survey data"""
    if survey_df is None or len(survey_df) == 0:
        return pd.DataFrame()
    
    filtered = survey_df.copy()
    
    # Apply filters based on what's selected
    if communities:
        # Filter by Main Community or any Communities involved
        community_mask = filtered['Main Community'].isin(communities)
        # Also check "Communities" column if it exists (comma-separated values)
        if 'Communities' in filtered.columns:
            community_mask |= filtered['Communities'].apply(
                lambda x: any(c in communities for c in str(x).split(',')) if pd.notna(x) else False
            )
        filtered = filtered[community_mask]
    
    if residences:
        filtered = filtered[filtered['Residence'].isin(residences)]
    
    if locations:
        # Location filter might be based on specific areas  
        if 'State' in filtered.columns:
            filtered = filtered[filtered['State'].isin(locations)]
    
    if education_levels:
        if 'Education' in filtered.columns:
            filtered = filtered[filtered['Education'].isin(education_levels)]
    
    if religions:
        if 'Religious View' in filtered.columns:
            filtered = filtered[filtered['Religious View'].isin(religions)]
    
    if genders:
        if 'Gender' in filtered.columns:
            filtered = filtered[filtered['Gender'].isin(genders)]
    
    if sexualities:
        if 'Sexuality' in filtered.columns:
            filtered = filtered[filtered['Sexuality'].isin(sexualities)]
    
    # New filters
    if community_scales:
        if 'Community Scale' in filtered.columns:
            filtered = filtered[filtered['Community Scale'].isin(community_scales)]
    
    if aloha_spirits:
        if 'Feel Aloha Spirit' in filtered.columns:
            filtered = filtered[filtered['Feel Aloha Spirit'].isin(aloha_spirits)]
    
    if hawaiian_cultures:
        if 'Hawaiian Culture' in filtered.columns:
            filtered = filtered[filtered['Hawaiian Culture'].isin(hawaiian_cultures)]
    
    if us_born:
        if 'U.S. Born' in filtered.columns:
            filtered = filtered[filtered['U.S. Born'].isin(us_born)]
    
    if country:
        if 'Country' in filtered.columns:
            filtered = filtered[filtered['Country'].isin(country)]
    
    if stay_on_island:
        if 'Stay on Island:' in filtered.columns:
            filtered = filtered[filtered['Stay on Island:'].isin(stay_on_island)]
    
    if relationship_status:
        if 'Relationship Status ' in filtered.columns:
            filtered = filtered[filtered['Relationship Status '].isin(relationship_status)]
    
    if age_ranges:
        if 'Age' in filtered.columns:
            filtered = filtered[filtered['Age'].isin(age_ranges)]
    
    if occupations:
        if 'Occupation' in filtered.columns:
            filtered = filtered[filtered['Occupation'].isin(occupations)]
    
    return filtered


def calculate_demographic_stats(filtered_survey_df):
    """Calculate demographic statistics from filtered survey data"""
    stats_elements = []
    
    if filtered_survey_df is None or len(filtered_survey_df) == 0:
        return {
            'total_responses': 0,
            'stats_elements': [dash_html.Div('No demographic data available', 
                                            style={'paddingLeft': '10px', 'color': '#999'})]
        }
    
    total = len(filtered_survey_df)
    
    # Helper function to create stat entry
    def create_stat_entry(label, series, top_n=5):
        if series is None or label not in filtered_survey_df.columns:
            return []
        
        data = filtered_survey_df[label].dropna()
        if len(data) == 0:
            return []
        
        elements = [dash_html.Div(f'{label}:', style={'marginBottom': '3px', 'paddingLeft': '10px', 'fontWeight': 'bold', 'fontSize': '11px'})]
        
        # For numeric data, show mean/median
        if pd.api.types.is_numeric_dtype(data):
            mean_val = data.mean()
            median_val = data.median()
            elements.append(
                dash_html.Div(f'Mean: {mean_val:.1f}, Median: {median_val:.1f}', 
                             style={'paddingLeft': '20px', 'fontSize': '10px', 'marginBottom': '3px'})
            )
        else:
            # For categorical, show top values
            value_counts = data.value_counts().head(top_n)
            for val, count in value_counts.items():
                pct = (count / total) * 100
                elements.append(
                    dash_html.Div(f'{val}: {count} ({pct:.1f}%)', 
                                 style={'paddingLeft': '20px', 'fontSize': '10px', 'marginBottom': '2px'})
                )
        
        return elements
    
    # Add demographic breakdowns
    # Origin/Ethnicity
    if 'State' in filtered_survey_df.columns:
        stats_elements.extend(create_stat_entry('State', filtered_survey_df['State']))
        
    elif 'Residence' in filtered_survey_df.columns:
        stats_elements.extend(create_stat_entry('Residence', filtered_survey_df['Residence']))
    
    # Gender
    if 'Gender' in filtered_survey_df.columns:
        stats_elements.extend(create_stat_entry('Gender', filtered_survey_df['Gender']))
    
    # Education
    if 'Education' in filtered_survey_df.columns:
        stats_elements.extend(create_stat_entry('Education Level', filtered_survey_df['Education']))
    
    # Years on Island
    if 'Years on Island:' in filtered_survey_df.columns:
        stats_elements.extend(create_stat_entry('Years on Island:', filtered_survey_df['Years on Island:']))
    elif 'Years on Island' in filtered_survey_df.columns:
        stats_elements.extend(create_stat_entry('Years on Island', filtered_survey_df['Years on Island']))
    
    # Aloha Spirit (if it's a numeric scale)
    if 'Feel Aloha Spirit' in filtered_survey_df.columns:
        stats_elements.extend(create_stat_entry('Feel Aloha Spirit', filtered_survey_df['Feel Aloha Spirit']))
    
    # Hawaiian Culture Knowledge (if it's a numeric scale)
    if 'Hawaiian Culture' in filtered_survey_df.columns:
        stats_elements.extend(create_stat_entry('Hawaiian Culture', filtered_survey_df['Hawaiian Culture']))

        # Hawaiian Culture Knowledge (if it's a numeric scale)
    if 'Community Scale' in filtered_survey_df.columns:
        stats_elements.extend(create_stat_entry('Community Scale', filtered_survey_df['Community Scale']))

    # Age Range
    if 'Age Range' in filtered_survey_df.columns:
        stats_elements.extend(create_stat_entry('Age Range', filtered_survey_df['Age Range']))
    elif 'Age' in filtered_survey_df.columns:
        stats_elements.extend(create_stat_entry('Age', filtered_survey_df['Age']))
    
    return {
        'total_responses': total,
        'stats_elements': stats_elements if stats_elements else [
            dash_html.Div('No demographic data available', 
                         style={'paddingLeft': '10px', 'color': '#999'})
        ]
    }


def create_dash_app():
    """Create and configure the Dash application"""
    
    # Initialize Neo4j query engine for direct queries
    print("Connecting to Neo4j...")
    query_engine = get_query_engine()
    
    # Get filter options directly from Neo4j
    print("Loading filter options from Neo4j...")
    #### this needs to be updated 

    filter_vals = {

        # ---- Communities ----
        'main_communities': [
            "Dance",
            "Fire Spinning",
            "Music",
            "Rock Climbing",
            "Slackline / Highline",
            "Spiritual",
            "SurfBreak",
            "Surfing",
            "Yoga"
        ],
    
        'communities': [
            "Acroyoga",
            "Art / Vending",
            "Bar Scene",
            "Boating",
            "Business / Entrepreneurship",
            "Calisthenics",
            "Dance",
            "Farming",
            "Fire Spinning",
            "Free Diving / Scuba Diving",
            "Hiking",
            "Hunting",
            "LGBTQ",
            "Martial Arts",
            "Music",
            "Music Production",
            "Paddling / Outrigger",
            "Pickle Ball",
            "Poetry",
            "Rock Climbing",
            "Running",
            "Slackline / Highline",
            "Spiritual",
            "SurfBreak",
            "Surfing",
            "Tech",
            "Theatre",
            "Volley Ball",
            "Yoga"
        ],
    
        'associated_communities': [
            "Acroyoga",
            "Art / Vending",
            "Bar Scene",
            "Dance",
            "Fire Spinning",
            "Music",
            "Rock Climbing",
            "Slackline / Highline",
            "Spiritual",
            "SurfBreak",
            "Surfing",
            "Yoga"
        ],
    
        # ---- Geography ----
        'locations': [
            'Florida', 'Pennsylvania', 'Connecticut', 'Ohio', 'New York',
            'Michigan', 'Maryland', 'New Jersey', 'Utah', 'Illinois',
            'California', 'Texas', 'Iowa', 'Delaware', 'Idaho',
            'Massachusetts', 'Nebraska', 'Hawaii', 'Missouri', 'Wisconsin',
            'Virginia', 'Colorado', 'Tennessee', 'Nevada'
        ],
    
        'country': [
            'United States', 'Canada', 'Australia',
            'United Kingdom', 'Germany', 'France', 'Japan'
        ],
    
        'residence': [
            'Honolulu', 'Central Oahu', 'North Shore', 'East Side', 'West Side'
        ],

        # ---- Community Involvement ----
        'community_scales': [
                "1.0",
                "3.0",
                "4.0",
                "5.0",
                "6.0",
                "7.0",
                "8.0",
                "9.0",
                "10.0"
            ],
        # ---- Time on Island ----
        'years_on_island': ['0–1', '1–3', '3–5', '5–10', '10+'],
        # 'months_on_island': ['0–3', '3–6', '6–12'],
        'stay_on_island': ['Temporarily', 'Seasonally', 'Permanently', 'Not sure yet'],
    
        # ---- Cultural Connection ----
        'aloha_spirits': [
            'Not at all', 'Somewhat', 'Strongly', 'Very strongly'
        ],
    
        'hawaiian_cultures': [
            'Not connected', 'Somewhat connected',
            'Strongly connected', 'Very strongly connected'
        ],
    
        # ---- Identity ----quer
        'us_born': ['Yes', 'No'],
    
        'religions': [
            'Christian',
            'Agnostic, Atheist, or non-religious',
            'Buddhist',
            'Spiritual',
            'Other'
        ],
    
        'education_levels': [
            'High school diploma or GED',
            'Some college, but no degree',
            'Associates or technical degree',
            'Bachelor’s degree',
            'Graduate or professional degree (MA, MS, MBA, PhD, JD, MD, DDS etc.)',
            'Prefer not to say'
        ],
    
        'genders': ['Female', 'Male', 'Non-binary / third gender'],
    
        'sexualities': [
            'Heterosexual',
            'Bisexual',
            'Gay',
            'Pansexual',
            'Fluid',
            'Prefer not to disclose'
        ],
    
        'relationship_status': [
            'Single',
            'In a relationship',
            'Married',
            'Divorced'
        ],
    
        'age_ranges': [
            '18–24', '25–34', '35–44', '45–54', '55+'
        ],
    
        # ---- Occupation ----
        'occupations': [
            'Artist',
            'Business / Entrepreneurship',
            'Construction / Trades',
            'Education',
            'Engineering',
            'Finance',
            'Full-time student',
            'Hospitality',
            'Legal',
            'Marketing',
            'Medical Field / Healthcare',
            'Military',
            'Real Estate',
            'Research',
            'Tech',
            'Tourism',
            'Unemployed',
            'Other'
        ]
    }


    
    print(f"  Filter Options:")
    print(f"    - Communities: {len(filter_vals['communities'])}")
    print(f"    - Locations: {len(filter_vals['locations'])}")
    print(f"    - Residence: {len(filter_vals['residence'])}")
    print(f"    - Religions: {len(filter_vals['religions'])}")
    print(f"    - Education Levels: {len(filter_vals['education_levels'])}")
    print(f"    - Genders: {len(filter_vals['genders'])}")
    print(f"    - Sexualities: {len(filter_vals['sexualities'])}")
    
    # Add connection type options (static - based on graph structure, not survey data)
    filter_vals['connection_types'] = [
        {'label': 'Associated Communities', 'value': 'ASSOCIATED_WITH'},
        {'label': 'Communities', 'value': 'ALSO_INVOLVED_IN'},
        {'label': 'Main Community', 'value': 'HAS_MAIN_COMMUNITY'}
    ]
    
    # ========== Initialize Neo4j RAG System ==========
    print("\nInitializing Neo4j RAG system for semantic search...")
    rag_system = get_neo4j_rag()  # Uses credentials from config.py
    
    # Check if embeddings already exist in Neo4j
    stats = rag_system.get_stats()
    print(f"  Current embeddings in Neo4j: {stats['kg_count']} relationships, {stats['survey_count']} communities")
    
    # Index if needed (only runs once!)
    if stats['kg_count'] == 0 or stats['survey_count'] == 0:
        print("  No embeddings found. Indexing data into Neo4j...")
        print("  (This takes ~5-10 seconds and only happens once)")
        rag_system.reindex_all(survey_df)
        stats = rag_system.get_stats()
        print(f"  ✓ Indexed {stats['kg_count']} relationships and {stats['survey_count']} communities")
    else:
        print("  ✓ Using existing embeddings from Neo4j")
    print("="*60)
    # ========== End RAG Initialization ==========

    
    # Create Dash app
    dash_app = Dash(
        __name__,
        routes_pathname_prefix="/",
        requests_pathname_prefix="/dash/",
        suppress_callback_exceptions=True
    )
    
    # Define layout with tabs
    dash_app.layout = dash_html.Div([
        # Header navigation
        dash_html.Div([
            dash_html.A("← Home", href="/", style={
                'color': '#667eea', 
                'textDecoration': 'none', 
                'fontSize': '16px', 
                'marginRight': '20px'
            }),
            dash_html.A("API Docs", href="/docs", style={
                'color': '#667eea', 
                'textDecoration': 'none', 
                'fontSize': '16px'
            }),
        ], style={'padding': '10px 20px', 'background': '#f8f9fa'}),
        
        # Title
        dash_html.H1('Oahu Community Knowledge Graph', 
                     style={'textAlign': 'center', 'color': '#2c3e50', 'margin': '20px'}),
        
        # Tabs
        dcc.Tabs(id='main-tabs', value='graph-tab', children=[
            dcc.Tab(label='Knowledge Graph', value='graph-tab', style={'padding': '10px'}),
            dcc.Tab(label='AI Search Agent', value='stats-tab', style={'padding': '10px'}),
        ]),
        
        # Tab content container
        dash_html.Div(id='tab-content')
    ])
    
    # Callback to render tab content
    @dash_app.callback(
        Output('tab-content', 'children'),
        Input('main-tabs', 'value')
    )
    def render_tab_content(tab):
        if tab == 'graph-tab':
            return create_graph_tab(filter_vals)
        elif tab == 'stats-tab':
            return create_stats_tab(survey_df)
    
    # Callback for graph tab - NOW USES CYPHER QUERIES
    @dash_app.callback(
        [Output('graph', 'figure'),
         Output('stats', 'children')],
        [Input('layout', 'value'),
         Input('main_communities', 'value'),
         Input('communities', 'value'),
         Input('residences', 'value'),
         Input('locations', 'value'),
         Input('education_levels', 'value'),
         Input('religions', 'value'),
         Input('genders', 'value'), 
         Input('sexualities', 'value'),
         Input('connection_types', 'value'),
         Input('community_scales', 'value'),
         Input('aloha_spirits', 'value'),
         Input('hawaiian_cultures', 'value'),
         Input('us_born', 'value'),
         Input('country', 'value'),
         Input('stay_on_island', 'value'),
         Input('relationship_status', 'value'),
         Input('age_ranges', 'value'),
         Input('occupations', 'value')]
    )
    def update_graph(layout, main_communities, communities, residences, locations, education_levels, religions, genders, sexualities,
                    connection_types, community_scales, aloha_spirits, hawaiian_cultures, us_born, country, 
                    stay_on_island, relationship_status, age_ranges, occupations):
        """Update graph based on filter selections - QUERIES Neo4j DIRECTLY with Cypher"""
        
        print("\n=== Updating Graph with Neo4j Query ===")
        print(f"Filters selected:")
        print(f"  Main Communities: {main_communities}")
        print(f"  Communities: {communities}")
        print(f"  Residences: {residences}")
        print(f"  Locations: {locations}")
        print(f"  Education: {education_levels}")
        print(f"  Religions: {religions}")
        print(f"  Genders: {genders}")
        print(f"  Sexualities: {sexualities}")
        print(f"  Connection Types: {connection_types}")
        print(f"  Community Scales: {community_scales}")
        print(f"  Aloha Spirits: {aloha_spirits}")
        print(f"  Hawaiian Cultures: {hawaiian_cultures}")
        print(f"  U.S. Born: {us_born}")
        print(f"  country: {country}")
        print(f"  age_ranges: {age_ranges}")
        print(f"  Occupations: {occupations}")


        
        # Execute Cypher query in Neo4j with WHERE clauses
        filtered_df = query_engine.query_graph_with_filters(
            main_communities=main_communities if main_communities else None,
            communities=communities if communities else None,
            residences=residences if residences else None,
            locations=locations if locations else None,
            religions=religions if religions else None,
            education_levels=education_levels if education_levels else None,
            genders=genders if genders else None,
            sexualities=sexualities if sexualities else None,
            connection_types=connection_types if connection_types else None,
            community_scales=community_scales if community_scales else None,
            aloha_spirits=aloha_spirits if aloha_spirits else None,
            hawaiian_cultures=hawaiian_cultures if hawaiian_cultures else None,
            us_born=us_born if us_born else None,
            country=country if country else None,
            stay_on_island=stay_on_island if stay_on_island else None,
            relationship_status=relationship_status if relationship_status else None,
            age_ranges=age_ranges if age_ranges else None,
            occupations=occupations if occupations else None
        )
        
        print(f"Neo4j query returned: {len(filtered_df)} relationships")
        
        # Combine main_communities and communities for survey filtering
        all_communities = []
        if main_communities:
            all_communities.extend(main_communities)
        if communities:
            all_communities.extend(communities)
        survey_df = pd.read_csv('data/data_preprcd_12_18.csv')
        # Apply same filters to survey data for demographic stats
        filtered_survey_df = apply_filters_to_survey(
            survey_df,
            communities=all_communities if all_communities else None,
            residences=residences,
            locations=locations,
            education_levels=education_levels,
            religions=religions,
            genders=genders,
            sexualities=sexualities,
            community_scales=community_scales,
            aloha_spirits=aloha_spirits,
            hawaiian_cultures=hawaiian_cultures,
            us_born=us_born,
            country=country,
            stay_on_island=stay_on_island,
            relationship_status=relationship_status,
            age_ranges=age_ranges,
            occupations=occupations
        )
        
        # Handle empty results
        if len(filtered_df) == 0:
            print("WARNING: No relationships found in Neo4j")
            # Create empty graph
            G = nx.Graph()
            
            # Create empty stats
            stats = dash_html.Div([
                dash_html.Div('No data found with current filters', 
                             style={'marginBottom': '10px', 'color': '#e74c3c', 'fontWeight': 'bold'}),
                dash_html.Div('Try:', style={'marginBottom': '5px'}),
                dash_html.Div('• Clearing all filters', style={'marginBottom': '3px', 'paddingLeft': '10px'}),
                dash_html.Div('• Checking Neo4j has community relationships', style={'marginBottom': '3px', 'paddingLeft': '10px'}),
                dash_html.Div('• Verifying relationship types: also_involved_in, associated_with', style={'paddingLeft': '10px'}),
            ])
            
            # Create empty figure
            fig = go.Figure()
            fig.update_layout(
                title="No Data to Display",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                annotations=[{
                    'text': 'No relationships found. Check filters or database.',
                    'xref': 'paper',
                    'yref': 'paper',
                    'x': 0.5,
                    'y': 0.5,
                    'showarrow': False,
                    'font': {'size': 20, 'color': '#7f8c8d'}
                }]
            )
            
            return fig, stats
        
        # Convert predicate to uppercase for consistency
        filtered_df['predicate'] = filtered_df['predicate'].str.upper()
        
        # Get predicates for graph
        predicates = sorted(filtered_df['predicate'].dropna().unique().astype(str)) if len(filtered_df) > 0 else []
        
        # Create network graph
        G = create_network_graph(filtered_df, layout, predicates, [])
        
        # Calculate graph statistics
        num_nodes = G.number_of_nodes()
        num_edges = G.number_of_edges()
        density = nx.density(G) if num_nodes > 0 else 0
        avg_degree = (2 * num_edges / num_nodes) if num_nodes > 0 else 0
        
        # Calculate demographic statistics from filtered survey data
        demo_stats = calculate_demographic_stats(filtered_survey_df)
        
        # Create stats display with demographics
        stats = dash_html.Div([
            # Graph metrics
            dash_html.Div(f'Total Nodes: {num_nodes}', style={'marginBottom': '5px', 'fontWeight': 'bold'}),
            dash_html.Div(f'Edges: {num_edges}', style={'marginBottom': '5px'}),
            dash_html.Div(f'Density: {density:.3f}', style={'marginBottom': '5px'}),
            dash_html.Div(f'Avg Degree: {avg_degree:.2f}', style={'marginBottom': '15px'}),
            
            # Demographics header
            dash_html.Div('Demographics:', style={'marginBottom': '5px', 'fontWeight': 'bold', 'marginTop': '10px'}),
            dash_html.Div(f'Survey Responses: {demo_stats["total_responses"]}', 
                         style={'marginBottom': '10px', 'paddingLeft': '10px', 'fontSize': '12px', 'color': '#666'}),
            
            # Demographic breakdowns
            *demo_stats['stats_elements']
        ])
        
        # Create figure
        fig = create_plotly_graph(G, layout)
        
        # Ensure showlegend is enabled globally
        fig.update_layout(showlegend=True)
        
        # Add legend to the graph
        # Add invisible traces for legend entries
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=12, color='#667eea'),
            showlegend=True,
            name='Community',
            legendgroup='community',
            hoverinfo='skip'
        ))
        
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=12, color='#f56565'),
            showlegend=True,
            name='Main Community',
            legendgroup='main_community',
            hoverinfo='skip'
        ))
        
        # Update legend position and styling
        fig.update_layout(
            legend=dict(
                yanchor="top",
                y=0.98,
                xanchor="right",
                x=0.99,
                bgcolor="rgba(255, 255, 255, 0.95)",
                bordercolor="#333",
                borderwidth=2,
                font=dict(size=14, color='#2c3e50'),
                title=dict(
                    text="Node Types",
                    font=dict(size=15, color='#2c3e50', family='Arial Black')
                )
            )
        )
        
        return fig, stats
    
    # Callback for AI search agent
    @dash_app.callback(
        Output('ai-response', 'children'),
        Input('ai-search-button', 'n_clicks'),
        State('ai-search-input', 'value'),
        prevent_initial_call=True
    )
    def handle_ai_search(n_clicks, query):
        """Handle AI search queries using Neo4j RAG (semantic search)"""
        
        # Only process if button was actually clicked
        if n_clicks is None or n_clicks == 0:
            return dash_html.Div(
                "Enter a question above and click the Search button.",
                style={'color': '#7f8c8d', 'fontStyle': 'italic', 'padding': '10px'}
            )
        
        if not query or not query.strip():
            return dash_html.Div(
                "Enter a question above and click Search to get started.",
                style={'color': '#7f8c8d', 'fontStyle': 'italic', 'padding': '10px'}
            )
        
        try:
            # ========== Use Neo4j RAG for semantic search ==========
            print(f"\n{'='*60}")
            print(f"Neo4j RAG Query: '{query}'")
            print(f"{'='*60}")
            
            # Use Neo4j RAG to retrieve only relevant context via semantic search
            print("  Retrieving relevant context using Neo4j vector search...")
            kg_context, survey_context = rag_system.retrieve_relevant_context(
                query=query,
                n_results=10  # Get top 10 most relevant items from each collection
            )
            
            print(f"  ✓ Retrieved KG context: {len(kg_context)} chars")
            print(f"  ✓ Retrieved survey context: {len(survey_context)} chars")
            # =======================================================
            
            # Call Claude API with focused, relevant context
            print("  Querying Claude API...")
            response_text = query_claude_api(query, kg_context, survey_context)
            print("  ✓ Response received")
            print(f"{'='*60}\n")
            
            return dash_html.Div([
                dash_html.Strong("Answer:", style={'color': '#667eea', 'display': 'block', 'marginBottom': '8px'}),
                dcc.Markdown(response_text)
            ])
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"  ✗ Error: {str(e)}")
            print(f"{'='*60}\n")
            return dash_html.Div([
                dash_html.Strong("Error:", style={'color': '#e74c3c'}),
                dash_html.P(f"Could not process query: {str(e)}", style={'marginTop': '5px'}),
                dash_html.Details([
                    dash_html.Summary("Show error details", style={'cursor': 'pointer', 'marginTop': '10px', 'color': '#7f8c8d'}),
                    dash_html.Pre(error_details, style={
                        'fontSize': '10px', 
                        'background': '#f8f9fa', 
                        'padding': '10px', 
                        'overflow': 'auto',
                        'marginTop': '10px',
                        'border': '1px solid #ddd',
                        'borderRadius': '4px'
                    })
                ])
            ])
    
    return dash_app


def prepare_kg_context_from_neo4j(query_engine):
    """Prepare knowledge graph data summary using direct Neo4j queries"""
    # Query all community relationships from Neo4j
    df = query_engine.query_graph_with_filters()
    
    # Get community relationships
    community_rels = df[df['predicate'].str.upper().isin(['ALSO_INVOLVED_IN', 'ASSOCIATED_WITH'])]
    
    # Count relationships by community
    community_connections = defaultdict(lambda: {'also_involved': [], 'associated': []})
    
    for _, row in community_rels.iterrows():
        subj = row['subject']
        obj = row['object']
        pred = row['predicate'].upper()
        
        if pred == 'ALSO_INVOLVED_IN':
            community_connections[subj]['also_involved'].append(obj)
        elif pred == 'ASSOCIATED_WITH':
            community_connections[subj]['associated'].append(obj)
    
    # Format summary - REDUCED to top 10 to save tokens
    summary = "KNOWLEDGE GRAPH SUMMARY (from Neo4j):\n\n"
    summary += f"Total communities tracked: {len(community_connections)}\n\n"
    
    summary += "Top Community Connections:\n"
    for i, (comm, rels) in enumerate(list(community_connections.items())[:10]):  # Only top 10
        if rels['also_involved'] or rels['associated']:
            summary += f"- {comm}:\n"
            if rels['also_involved']:
                summary += f"  Also involved: {', '.join(rels['also_involved'][:3])}\n"  # Max 3
            if rels['associated']:
                summary += f"  Associated: {', '.join(rels['associated'][:3])}\n"  # Max 3
    
    return summary


# Legacy function for backward compatibility
def prepare_kg_context(df):
    """Prepare knowledge graph data summary for AI context"""
    # Get community relationships
    community_rels = df[df['predicate'].isin(['ALSO_INVOLVED_IN', 'ASSOCIATED_WITH'])]
    
    # Count relationships by community
    from collections import defaultdict
    community_connections = defaultdict(lambda: {'also_involved': [], 'associated': []})
    
    for _, row in community_rels.iterrows():
        subj = row['subject']
        obj = row['object']
        pred = row['predicate']
        
        if pred == 'ALSO_INVOLVED_IN':
            community_connections[subj]['also_involved'].append(obj)
        elif pred == 'ASSOCIATED_WITH':
            community_connections[subj]['associated'].append(obj)
    
    # Format summary
    summary = "KNOWLEDGE GRAPH SUMMARY:\n\n"
    summary += f"Total relationships: {len(df)}\n"
    summary += f"Total communities: {len(community_connections)}\n\n"
    
    summary += "Community Connections (sample):\n"
    for i, (comm, rels) in enumerate(list(community_connections.items())[:20]):
        if rels['also_involved'] or rels['associated']:
            summary += f"- {comm}:\n"
            if rels['also_involved']:
                summary += f"  Also involved in: {', '.join(rels['also_involved'][:5])}\n"
            if rels['associated']:
                summary += f"  Associated with: {', '.join(rels['associated'][:5])}\n"
    
    return summary


def prepare_survey_context(survey_df):
    """Prepare survey data summary for AI context - includes demographics and location data"""
    summary = "\n\nSURVEY DATA SUMMARY:\n\n"
    summary += f"Total responses: {len(survey_df)}\n\n"
    
    # Main communities
    top_communities = survey_df['Main Community'].value_counts().head(10)
    summary += "Top Main Communities:\n"
    for comm, count in top_communities.items():
        summary += f"- {comm}: {count} members\n"
    
    # Origin locations (where people are from)
    if 'Country' in survey_df.columns:
        summary += f"\nOrigin Locations:\n"
        # US states
        us_respondents = survey_df[survey_df['U.S. Born'] == 'Yes']
        if len(us_respondents) > 0 and 'State' in survey_df.columns:
            state_counts = us_respondents['State'].value_counts().head(10)
            summary += "  US States:\n"
            for state, count in state_counts.items():
                if pd.notna(state):
                    summary += f"    - {state}: {count}\n"
        
        # country (non-US)
        foreign_respondents = survey_df[survey_df['U.S. Born'] == 'No']
        if len(foreign_respondents) > 0:
            country_counts = foreign_respondents['Country'].value_counts().head(10)
            summary += "  Other country:\n"
            for country, count in country_counts.items():
                if pd.notna(country):
                    summary += f"    - {country}: {count}\n"
    
    # Community Involvement patterns
    if 'Community Involvement' in survey_df.columns:
        summary += f"\nCommunity Involvement Patterns:\n"
        # Get sample of community involvements
        involvements = survey_df['Community Involvement'].dropna().head(10)
        for i, involvement in enumerate(involvements[:5], 1):
            communities = str(involvement).split(',')[:3]  # First 3 communities
            summary += f"  Person {i}: {', '.join(communities)}\n"
    
    # Demographics overview
    summary += f"\nCurrent Residence:\n"
    for res, count in survey_df['Residence'].value_counts().items():
        summary += f"- {res}: {count}\n"
    
    summary += f"\nEducation levels:\n"
    for edu, count in survey_df['Education'].value_counts().head(5).items():
        summary += f"- {edu}: {count}\n"
    
    summary += f"\nGender distribution:\n"
    for gender, count in survey_df['Gender'].value_counts().items():
        summary += f"- {gender}: {count}\n"
    
    # Years on island stats
    if 'Years on Island:' in survey_df.columns:
        years_data = survey_df['Years on Island:'].dropna()
        if len(years_data) > 0:
            summary += f"\nYears on Island: mean={years_data.mean():.1f}, median={years_data.median():.1f}\n"
    
    return summary


def query_claude_api(user_query, kg_context, survey_context):
    """Query Claude API with knowledge graph and survey context"""
    import anthropic
    
    # Get API key from config or environment
    try:
        from config import ANTHROPIC_API_KEY
        api_key = ANTHROPIC_API_KEY
    except (ImportError, AttributeError):
        # Fallback to environment variable
        api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key or api_key.startswith('sk-ant-XXXXXX'):
        return "Error: Please configure ANTHROPIC_API_KEY in config.py or as an environment variable."
    
    client = anthropic.Anthropic(api_key=api_key)
    
    system_prompt = """You are an expert on Hawaiian community culture and data analysis. 
You have access to knowledge graph data showing relationships between communities in Oahu, 
and survey data with demographics, community involvement, and origin locations (where people are from).

When answering questions:
1. For community relationships: Use the knowledge graph data to show which communities are connected
2. For demographics: Use the survey data to provide statistical summaries
3. For location-based questions: Use the survey data showing where people are from (US states, country)
   Example: "What communities do people from Colorado join?" - Look at State/Country data and Community Involvement
4. For Hawaiian culture/history: Draw on your knowledge of Hawaiian traditions, especially:
   - Surfing (he'e nalu) - ancient Hawaiian practice, spiritual connection to ocean
   - Slack lining and balance practices - modern extensions of traditional Hawaiian athletic training
   - Rock climbing - newer to Hawaii, but connects to ancient cliff diving (lele kawa) traditions
   - Acro yoga, fire spinning, and other movement arts - blend modern practice with Hawaiian emphasis on community and 'ohana
   - The concept of 'Aloha Spirit' and how it manifests in community activities
   - Hawaiian values: kuleana (responsibility), malama (care), lokahi (unity)

The survey data includes:
- Where people are originally from (State for US-born, Country for international)
- Current residence on Oahu
- Community involvement (which communities they participate in)
- Demographics (education, gender, etc.)
- Years on island

Provide specific data when available, and be clear when you're drawing on general cultural knowledge vs. the specific data provided."""

    user_message = f"""USER QUESTION: {user_query}

AVAILABLE DATA:

{kg_context}

{survey_context}

Please answer the user's question using the data provided and your knowledge of Hawaiian culture."""

    try:
        # Create the API call with explicit parameters
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )
        
        # Extract the text from the response
        if response and response.content and len(response.content) > 0:
            return response.content[0].text
        else:
            return "Error: No response content received from Claude API."
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"Error querying Claude API: {str(e)}\n\nDetails:\n{error_details}"


def create_graph_tab(filter_vals):
    """Create the Knowledge Graph tab layout"""
    return dash_html.Div([
        dash_html.P(
            'Visualizing Community Connections • Filter by Attributes',
            style={'textAlign': 'center', 'color': '#7f8c8d', 'margin': '10px'}
        ),
        
        # Main content area (sidebar + graph)
        dash_html.Div([
            # Sidebar with filters
            dash_html.Div([
                dash_html.H3('Graph Controls'),
                
                dash_html.Label('Layout:'),
                dcc.Dropdown(
                    id='layout',
                    options=[
                        {'label': 'Spring', 'value': 'spring'},
                        {'label': 'Circular', 'value': 'circular'},
                        {'label': 'Kamada-Kawai', 'value': 'kamada'}
                    ],
                    value='spring',
                    style={'marginBottom': '10px'}
                ),
                
                dash_html.Hr(),
                dash_html.H3('Filters', style={'marginBottom': '10px'}),
                dash_html.P(
                    'Filter communities by their attributes',
                    style={'fontSize': '12px', 'color': '#7f8c8d', 'fontStyle': 'italic', 'marginBottom': '15px'}
                ),
                
                # Compact 2-column filter layout
                dash_html.Div([
                    # Row 1: Main Community & Community
                    dash_html.Div([
                        dash_html.Div([
                            dash_html.Label('Main Community:', style={'fontSize': '13px', 'marginBottom': '3px'}),
                            dcc.Dropdown(
                                id='main_communities',
                                options=[{'label': c, 'value': c} for c in filter_vals['communities']],
                                value=[], 
                                multi=True,
                                placeholder='Select...',
                                style={'fontSize': '12px'}
                            ),
                        ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '4%', 'verticalAlign': 'top'}),
                        
                        dash_html.Div([
                            dash_html.Label('Community:', style={'fontSize': '13px', 'marginBottom': '3px'}),
                            dcc.Dropdown(
                                id='communities',
                                options=[{'label': c, 'value': c} for c in filter_vals['communities']],
                                value=[], 
                                multi=True,
                                placeholder='Select...',
                                style={'fontSize': '12px'}
                            ),
                        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                    ], style={'marginBottom': '10px'}),
                   
                    
                    # Row 3: Origin State & Residence


                    dash_html.Div([
                        dash_html.Div([
                            dash_html.Label('Origin State:', style={'fontSize': '13px', 'marginBottom': '3px'}),
                            dcc.Dropdown(
                                id='locations',
                                options=[{'label': r, 'value': r} for r in filter_vals['locations']],
                                value=[], 
                                multi=True,
                                placeholder='Select...',
                                style={'fontSize': '12px'}
                            ),
                        ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '4%', 'verticalAlign': 'top'}),
                        
                        dash_html.Div([
                            dash_html.Label('Residence', style={'fontSize': '13px', 'marginBottom': '3px'}),
                            dcc.Dropdown(
                                id='residences',
                                options=[{'label': g, 'value': g} for g in filter_vals['residence']],
                                value=[], 
                                multi=True,
                                placeholder='Select...',
                                style={'fontSize': '12px'}
                            ),
                        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                    ], style={'marginBottom': '10px'}),   

                # Row 4: Education and Occupation 
                    dash_html.Div([
                        dash_html.Div([
                            dash_html.Label('Education:', style={'fontSize': '13px', 'marginBottom': '3px'}),
                            dcc.Dropdown(
                                id='education_levels',
                                options=[{'label': r, 'value': r} for r in filter_vals['education_levels']],
                                value=[], 
                                multi=True,
                                placeholder='Select...',
                                style={'fontSize': '12px'}
                            ),
                        ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '4%', 'verticalAlign': 'top'}),
                        
                        dash_html.Div([
                            dash_html.Label('Occupation:', style={'fontSize': '13px', 'marginBottom': '3px'}),
                            dcc.Dropdown(
                                id='occupations',
                                options=[{'label': g, 'value': g} for g in filter_vals['occupations']],
                                value=[], 
                                multi=True,
                                placeholder='Select...',
                                style={'fontSize': '12px'}
                            ),
                        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                    ], style={'marginBottom': '10px'}),
                    
                    # Row 4: Religion & Gender
                    dash_html.Div([
                        dash_html.Div([
                            dash_html.Label('Religion:', style={'fontSize': '13px', 'marginBottom': '3px'}),
                            dcc.Dropdown(
                                id='religions',
                                options=[{'label': r, 'value': r} for r in filter_vals['religions']],
                                value=[], 
                                multi=True,
                                placeholder='Select...',
                                style={'fontSize': '12px'}
                            ),
                        ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '4%', 'verticalAlign': 'top'}),
                        
                        dash_html.Div([
                            dash_html.Label('Gender:', style={'fontSize': '13px', 'marginBottom': '3px'}),
                            dcc.Dropdown(
                                id='genders',
                                options=[{'label': g, 'value': g} for g in filter_vals['genders']],
                                value=[], 
                                multi=True,
                                placeholder='Select...',
                                style={'fontSize': '12px'}
                            ),
                        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                    ], style={'marginBottom': '10px'}),
                    
                  dash_html.Div([
                    dash_html.Div([
                        dash_html.Label('Sexuality:', style={'fontSize': '13px', 'marginBottom': '3px'}),
                        dcc.Dropdown(
                            id='sexualities',
                            options=[{'label': g, 'value': g} for g in filter_vals['sexualities']],
                            value=[],
                            multi=True,
                            placeholder='Select...',
                            style=COMPACT_DROPDOWN_STYLE,
                            maxHeight=120
                        ),
                    ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '4%', 'verticalAlign': 'top'}),
                
                    dash_html.Div([
                        dash_html.Label('Connection Type:', style={'fontSize': '13px', 'marginBottom': '3px'}),
                        dcc.Dropdown(
                            id='connection_types',
                            options=filter_vals['connection_types'],
                            value=[],
                            multi=True,
                            placeholder='Select...',
                            style=COMPACT_DROPDOWN_STYLE,
                            maxHeight=120
                        ),
                    ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                ], style={'marginBottom': '10px'}),

                    # Row 7: Community Scale & Aloha Spirit
                    dash_html.Div([
                        dash_html.Div([
                            dash_html.Label('Community Scale:', style={'fontSize': '13px', 'marginBottom': '3px'}),
                            dcc.Dropdown(
                                id='community_scales',
                                options=[{'label': str(s), 'value': s} for s in filter_vals['community_scales']],
                                value=[], 
                                multi=True,
                                placeholder='Select...',
                                style={'fontSize': '12px'}
                            ),
                        ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '4%', 'verticalAlign': 'top'}),
                        
                        dash_html.Div([
                            dash_html.Label('Aloha Spirit:', style={'fontSize': '13px', 'marginBottom': '3px'}),
                            dcc.Dropdown(
                                id='aloha_spirits',
                                options=[{'label': a[:50] + '...' if len(a) > 50 else a, 'value': a} for a in filter_vals['aloha_spirits']],
                                value=[], 
                                multi=True,
                                placeholder='Select...',
                                style={'fontSize': '12px'}
                            ),
                        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                    ], style={'marginBottom': '10px'}),
                    
                    # Row 8: Hawaiian Culture & U.S. Born
                    dash_html.Div([
                        dash_html.Div([
                            dash_html.Label('Hawaiian Culture:', style={'fontSize': '13px', 'marginBottom': '3px'}),
                            dcc.Dropdown(
                                id='hawaiian_cultures',
                                options=[{'label': h, 'value': h} for h in filter_vals['hawaiian_cultures']],
                                value=[], 
                                multi=True,
                                placeholder='Select...',
                                style={'fontSize': '12px'}
                            ),
                        ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '4%', 'verticalAlign': 'top'}),
                        
                        dash_html.Div([
                            dash_html.Label('U.S. Born:', style={'fontSize': '13px', 'marginBottom': '3px'}),
                            dcc.Dropdown(
                                id='us_born',
                                options=[{'label': u, 'value': u} for u in filter_vals['us_born']],
                                value=[], 
                                multi=True,
                                placeholder='Select...',
                                style={'fontSize': '12px'}
                            ),
                        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                    ], style={'marginBottom': '10px'}),
                    
                    # Row 9: Country & Stay on Island
                    dash_html.Div([
                        dash_html.Div([
                            dash_html.Label('Country:', style={'fontSize': '13px', 'marginBottom': '3px'}),
                            dcc.Dropdown(
                                id='country',
                                options=[{'label': c, 'value': c} for c in filter_vals['country']],
                                value=[], 
                                multi=True,
                                placeholder='Select...',
                                style={'fontSize': '12px'}
                            ),
                        ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '4%', 'verticalAlign': 'top'}),
                        
                        dash_html.Div([
                            dash_html.Label('Stay on Island:', style={'fontSize': '13px', 'marginBottom': '3px'}),
                            dcc.Dropdown(
                                id='stay_on_island',
                                options=[{'label': s[:30] + '...' if len(s) > 30 else s, 'value': s} for s in filter_vals['stay_on_island']],
                                value=[], 
                                multi=True,
                                placeholder='Select...',
                                style={'fontSize': '12px'}
                            ),
                        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                    ], style={'marginBottom': '10px'}),
                    
                    # Row 10: Relationship Status & Age
                    dash_html.Div([
                        dash_html.Div([
                            dash_html.Label('Relationship Status:', style={'fontSize': '13px', 'marginBottom': '3px'}),
                            dcc.Dropdown(
                                id='relationship_status',
                                options=[{'label': r, 'value': r} for r in filter_vals['relationship_status']],
                                value=[], 
                                multi=True,
                                placeholder='Select...',
                                style={'fontSize': '12px'}
                            ),
                        ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '4%', 'verticalAlign': 'top'}),
                        
                        dash_html.Div([
                            dash_html.Label('Age:', style={'fontSize': '13px', 'marginBottom': '3px'}),
                            dcc.Dropdown(
                                id='age_ranges',
                                options=[{'label': a, 'value': a} for a in filter_vals['age_ranges']],
                                value=[], 
                                multi=True,
                                placeholder='Select...',
                                style={'fontSize': '12px'}
                            ),
                        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                    ], style={'marginBottom': '10px'}),
                ]),
                
                dash_html.Hr(),
                dash_html.H3('Graph Stats'),
                dash_html.Div(id='stats'),
                
            ], style={
                'width': '28%', 
                'padding': '15px', 
                'background': '#f8f9fa', 
                'height': '85vh', 
                'overflowY': 'auto', 
                'flexShrink': '0'
            }),
            
            # Graph visualization area
            dash_html.Div([
                dcc.Graph(id='graph', style={'height': '85vh'})
            ], style={'width': '72%', 'flexGrow': '1'}),
            
        ], style={'display': 'flex', 'flexDirection': 'row', 'width': '100%'})
    ])


def create_stats_tab(survey_df):
    """Create the AI Search Agent tab layout"""
    if survey_df is None:
        return dash_html.Div([
            dash_html.H3('Survey data not available', 
                        style={'textAlign': 'center', 'color': '#e74c3c', 'marginTop': '50px'})
        ])
    
    # Create layout with only AI Search Agent
    return dash_html.Div([
        dash_html.H2('AI Search Agent', 
                    style={'textAlign': 'center', 'color': '#2c3e50', 'margin': '40px 20px 20px 20px'}),
        dash_html.P(
            'Ask questions about communities, relationships, and Hawaiian culture',
            style={'textAlign': 'center', 'fontSize': '16px', 'color': '#7f8c8d', 'fontStyle': 'italic', 'marginBottom': '40px'}
        ),
        
        dash_html.Div([
            # AI Search input
            dcc.Textarea(
                id='ai-search-input',
                placeholder='Example: What communities are Rock Climbers also involved in?\nExample: What is the history of surfing in Hawaiian culture?\nExample: Show demographics for the Acroyoga community...',
                style={
                    'width': '100%',
                    'height': '150px',
                    'fontSize': '15px',
                    'padding': '15px',
                    'borderRadius': '8px',
                    'border': '2px solid #ddd',
                    'resize': 'vertical',
                    'fontFamily': 'Arial, sans-serif',
                    'marginBottom': '20px'
                }
            ),
            
            dash_html.Button(
                'Search',
                id='ai-search-button',
                n_clicks=0,
                style={
                    'width': '220px',
                    'padding': '14px',
                    'background': '#667eea',
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '8px',
                    'cursor': 'pointer',
                    'fontSize': '16px',
                    'fontWeight': '600',
                    'display': 'block',
                    'marginLeft': 'auto',
                    'marginRight': 'auto',
                    'marginBottom': '30px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                    'transition': 'all 0.3s ease'
                }
            ),
            
            # AI Response area
            dcc.Loading(
                id='ai-loading',
                type='circle',
                children=dash_html.Div(
                    id='ai-response',
                    style={
                        'padding': '20px',
                        'background': '#f8f9fa',
                        'borderRadius': '8px',
                        'border': '1px solid #ddd',
                        'fontSize': '15px',
                        'minHeight': '150px',
                        'maxHeight': '600px',
                        'overflowY': 'auto',
                        'lineHeight': '1.7'
                    },
                    children=dash_html.Div(
                        "Enter a question above and click Search to get started.",
                        style={'color': '#7f8c8d', 'fontStyle': 'italic', 'textAlign': 'center', 'padding': '40px'}
                    )
                )
            ),
        ], style={'maxWidth': '1000px', 'margin': '0 auto', 'padding': '40px 20px'})
    ])