"""
dash_app.py - Dash dashboard application
Visualizes only Community and Main_Community nodes, uses Attributes for filtering
Includes Survey Statistics tab and AI Search Agent
"""

from dash import Dash, dcc, html as dash_html, Input, Output
import networkx as nx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from collections import defaultdict
from data_loader import load_triples_from_neo4j
from filters import extract_filter_values, get_node_type_counts
from graph_utils import create_network_graph, create_plotly_graph
from callbacks import filter_by_node_types


def create_dash_app():
    """Create and configure the Dash application"""
    
    # Initialize data for Dash
    print("Loading data for Dash...")
    df = load_triples_from_neo4j()
    df['predicate'] = df['predicate'].str.upper()
    
    # Show node type distribution
    if 'subject_label' in df.columns:
        node_counts = get_node_type_counts(df)
        print("  Node Type Distribution:")
        for label, count in node_counts.items():
            print(f"    - {label}: {count}")
    
    # Extract filter values
    filter_vals = extract_filter_values(df)
    print(f"  Filter Options:")
    print(f"    - Communities: {len(filter_vals['communities'])}")
    print(f"    - Locations: {len(filter_vals['locations'])}")
    print(f"    - Residence: {len(filter_vals['residence'])}")
    print(f"    - Religions: {len(filter_vals['religions'])}")
    print(f"    - Education Levels: {len(filter_vals['education_levels'])}")
    print(f"    - Genders: {len(filter_vals['genders'])}")
    print(f"    - Sexualities: {len(filter_vals['sexualities'])}")
    
    predicates = sorted(df['predicate'].dropna().unique().astype(str))
    
    # Load survey data
    print("Loading survey data...")
    try:
        survey_df = pd.read_csv('data/data_preprcd_12_12.csv')
        print(f"  Loaded {len(survey_df)} survey responses")
    except FileNotFoundError:
        print("  WARNING: Survey data file not found")
        survey_df = None
    
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
            dcc.Tab(label='Survey Statistics', value='stats-tab', style={'padding': '10px'}),
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
    
    # Callback for graph tab
    @dash_app.callback(
        [Output('graph', 'figure'),
         Output('stats', 'children')],
        [Input('layout', 'value'),
         Input('communities', 'value'),
         Input('residences', 'value'),
         Input('locations', 'value'),
         Input('education_levels', 'value'),
         Input('religions', 'value'),
         Input('genders', 'value'), 
         Input('sexualities', 'value')]
    )
    def update_graph(layout, communities, residences, locations, education_levels, religions, genders, sexualities):
        """Update graph based on filter selections - shows only Community nodes"""
        
        # Filter data
        filtered = filter_by_node_types(
            df,
            communities=communities,
            residences=residences,
            locations=locations,
            religions=religions,
            education_levels=education_levels,
            genders=genders,
            sexualities=sexualities
        )
        
        # Create network graph
        G = create_network_graph(filtered, layout, predicates, [])
        
        # Calculate statistics
        num_nodes = G.number_of_nodes()
        num_edges = G.number_of_edges()
        density = nx.density(G) if num_nodes > 0 else 0
        avg_degree = (2 * num_edges / num_nodes) if num_nodes > 0 else 0
        
        # Count node types
        num_communities = sum(1 for n in G.nodes() if G.nodes[n].get('node_type') == 'Community')
        num_main_communities = sum(1 for n in G.nodes() if G.nodes[n].get('node_type') == 'Main_Community')
        
        # Create stats display
        stats = dash_html.Div([
            dash_html.Div(f'Total Nodes: {num_nodes}', style={'marginBottom': '5px'}),
            dash_html.Div(f'Communities: {num_communities}', style={'marginBottom': '5px', 'paddingLeft': '10px'}),
            dash_html.Div(f'Main Communities: {num_main_communities}', style={'marginBottom': '10px', 'paddingLeft': '10px'}),
            dash_html.Div(f'Edges: {num_edges}', style={'marginBottom': '5px'}),
            dash_html.Div(f'Density: {density:.3f}', style={'marginBottom': '5px'}),
            dash_html.Div(f'Avg Degree: {avg_degree:.2f}', style={'marginBottom': '5px'}),
        ])
        
        # Create figure
        fig = create_plotly_graph(G, layout)
        
        return fig, stats
    
    # Callback for AI search agent
    @dash_app.callback(
        Output('ai-response', 'children'),
        Input('ai-search-button', 'n_clicks'),
        Input('ai-search-input', 'value'),
        prevent_initial_call=True
    )
    def handle_ai_search(n_clicks, query):
        """Handle AI search queries about communities and Hawaiian culture"""
        if not query or not query.strip():
            return dash_html.Div("Enter a question to get started.", 
                               style={'color': '#7f8c8d', 'fontStyle': 'italic'})
        
        try:
            # Prepare context from knowledge graph
            kg_summary = prepare_kg_context(df)
            
            # Prepare context from survey data
            if survey_df is not None:
                survey_summary = prepare_survey_context(survey_df)
            else:
                survey_summary = "Survey data not available."
            
            # Call Claude API
            response_text = query_claude_api(query, kg_summary, survey_summary)
            
            return dash_html.Div([
                dash_html.Strong("Answer:", style={'color': '#667eea', 'display': 'block', 'marginBottom': '8px'}),
                dcc.Markdown(response_text)
            ])
            
        except Exception as e:
            return dash_html.Div([
                dash_html.Strong("Error:", style={'color': '#e74c3c'}),
                dash_html.P(f"Could not process query: {str(e)}", style={'marginTop': '5px'})
            ])
    
    return dash_app


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
    """Prepare survey data summary for AI context"""
    summary = "\n\nSURVEY DATA SUMMARY:\n\n"
    summary += f"Total responses: {len(survey_df)}\n\n"
    
    # Main communities
    top_communities = survey_df['Main Community'].value_counts().head(10)
    summary += "Top Main Communities:\n"
    for comm, count in top_communities.items():
        summary += f"- {comm}: {count} members\n"
    
    # Demographics overview
    summary += f"\nResidence distribution:\n"
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
and survey data with demographics and community involvement.

When answering questions:
1. For community relationships: Use the knowledge graph data to show which communities are connected
2. For demographics: Use the survey data to provide statistical summaries
3. For Hawaiian culture/history: Draw on your knowledge of Hawaiian traditions, especially:
   - Surfing (he'e nalu) - ancient Hawaiian practice, spiritual connection to ocean
   - Slack lining and balance practices - modern extensions of traditional Hawaiian athletic training
   - Rock climbing - newer to Hawaii, but connects to ancient cliff diving (lele kawa) traditions
   - Acro yoga, fire spinning, and other movement arts - blend modern practice with Hawaiian emphasis on community and 'ohana
   - The concept of 'Aloha Spirit' and how it manifests in community activities
   - Hawaiian values: kuleana (responsibility), malama (care), lokahi (unity)

Provide specific data when available, and be clear when you're drawing on general cultural knowledge vs. the specific data provided."""

    user_message = f"""USER QUESTION: {user_query}

AVAILABLE DATA:

{kg_context}

{survey_context}

Please answer the user's question using the data provided and your knowledge of Hawaiian culture."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": user_message}
            ],
            system=system_prompt
        )
        
        return message.content[0].text
        
    except Exception as e:
        return f"Error querying Claude API: {str(e)}\n\nPlease check your API key and connection."


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
                    # Row 1: Community & Residence
                    dash_html.Div([
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
                        ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '4%', 'verticalAlign': 'top'}),
                        
                        dash_html.Div([
                            dash_html.Label('Residence:', style={'fontSize': '13px', 'marginBottom': '3px'}),
                            dcc.Dropdown(
                                id='residences',
                                options=[{'label': r, 'value': r} for r in filter_vals['residence']],
                                value=[], 
                                multi=True,
                                placeholder='Select...',
                                style={'fontSize': '12px'}
                            ),
                        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                    ], style={'marginBottom': '10px'}),
                    
                    # Row 2: Location & Education
                    dash_html.Div([
                        dash_html.Div([
                            dash_html.Label('Origin:', style={'fontSize': '13px', 'marginBottom': '3px'}),
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
                            dash_html.Label('Education:', style={'fontSize': '13px', 'marginBottom': '3px'}),
                            dcc.Dropdown(
                                id='education_levels',
                                options=[{'label': r, 'value': r} for r in filter_vals['education_levels']],
                                value=[], 
                                multi=True,
                                placeholder='Select...',
                                style={'fontSize': '12px'}
                            ),
                        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                    ], style={'marginBottom': '10px'}),
                    
                    # Row 3: Religion & Gender
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
                    
                    # Row 4: Sexuality (single column)
                    dash_html.Div([
                        dash_html.Label('Sexuality:', style={'fontSize': '13px', 'marginBottom': '3px'}),
                        dcc.Dropdown(
                            id='sexualities',
                            options=[{'label': g, 'value': g} for g in filter_vals['sexualities']],
                            value=[], 
                            multi=True,
                            placeholder='Select...',
                            style={'fontSize': '12px'}
                        ),
                    ], style={'marginBottom': '10px'}),
                ]),
                
                dash_html.Hr(),
                dash_html.H3('AI Search Agent', style={'marginBottom': '10px'}),
                dash_html.P(
                    'Ask questions about communities, relationships, and Hawaiian culture',
                    style={'fontSize': '12px', 'color': '#7f8c8d', 'fontStyle': 'italic', 'marginBottom': '10px'}
                ),
                
                # AI Search input
                dcc.Textarea(
                    id='ai-search-input',
                    placeholder='Example: What communities are Rock Climbers also involved in?\nExample: What is the history of surfing in Hawaiian culture?\nExample: Show demographics for the Acroyoga community...',
                    style={
                        'width': '100%',
                        'height': '100px',
                        'fontSize': '13px',
                        'padding': '8px',
                        'borderRadius': '5px',
                        'border': '1px solid #ddd',
                        'resize': 'vertical'
                    }
                ),
                
                dash_html.Button(
                    'Search',
                    id='ai-search-button',
                    n_clicks=0,
                    style={
                        'width': '100%',
                        'marginTop': '8px',
                        'padding': '8px',
                        'background': '#667eea',
                        'color': 'white',
                        'border': 'none',
                        'borderRadius': '5px',
                        'cursor': 'pointer',
                        'fontSize': '14px',
                        'fontWeight': '600'
                    }
                ),
                
                # AI Response area
                dcc.Loading(
                    id='ai-loading',
                    type='circle',
                    children=dash_html.Div(
                        id='ai-response',
                        style={
                            'marginTop': '15px',
                            'padding': '12px',
                            'background': '#fff',
                            'borderRadius': '5px',
                            'border': '1px solid #ddd',
                            'fontSize': '13px',
                            'maxHeight': '300px',
                            'overflowY': 'auto',
                            'lineHeight': '1.5'
                        }
                    )
                ),
                
                dash_html.Hr(),
                dash_html.H3('Graph Stats'),
                dash_html.Div(id='stats'),
                
                dash_html.Hr(),
                dash_html.Div([
                    dash_html.P('Legend:', style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dash_html.Div([
                        dash_html.Span('●', style={'color': '#667eea', 'fontSize': '20px', 'marginRight': '5px'}),
                        dash_html.Span('Community')
                    ], style={'marginBottom': '5px'}),
                    dash_html.Div([
                        dash_html.Span('●', style={'color': '#f56565', 'fontSize': '20px', 'marginRight': '5px'}),
                        dash_html.Span('Main Community')
                    ])
                ], style={'fontSize': '12px', 'padding': '10px', 'background': '#fff', 'borderRadius': '5px'})
                
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
    """Create the Survey Statistics tab layout"""
    if survey_df is None:
        return dash_html.Div([
            dash_html.H3('Survey data not available', 
                        style={'textAlign': 'center', 'color': '#e74c3c', 'marginTop': '50px'})
        ])
    
    # Create visualizations
    
    # 1. Histogram of Years on Island
    years_data = survey_df['Years on Island:'].dropna()
    fig_years = px.histogram(
        years_data, 
        x='Years on Island:',
        nbins=20,
        title='Distribution of Years on Island',
        labels={'Years on Island:': 'Years on Island'},
        color_discrete_sequence=['#667eea']
    )
    fig_years.update_layout(
        xaxis_title='Years on Island',
        yaxis_title='Count',
        showlegend=False,
        plot_bgcolor='#f8f9fa'
    )
    
    # 2. Bar chart (not boxplot) of Main Community counts
    main_community_counts = survey_df['Main Community'].value_counts().head(15)
    fig_community = px.bar(
        x=main_community_counts.index,
        y=main_community_counts.values,
        title='Top 15 Main Communities by Count',
        labels={'x': 'Main Community', 'y': 'Count'},
        color_discrete_sequence=['#667eea']
    )
    fig_community.update_layout(
        xaxis_title='Main Community',
        yaxis_title='Count',
        showlegend=False,
        xaxis_tickangle=-45,
        plot_bgcolor='#f8f9fa'
    )
    
    # 3. Bar chart of Occupation
    occupation_counts = survey_df['Occcupation'].value_counts().head(15)
    fig_occupation = px.bar(
        x=occupation_counts.index,
        y=occupation_counts.values,
        title='Top 15 Occupations by Count',
        labels={'x': 'Occupation', 'y': 'Count'},
        color_discrete_sequence=['#764ba2']
    )
    fig_occupation.update_layout(
        xaxis_title='Occupation',
        yaxis_title='Count',
        showlegend=False,
        xaxis_tickangle=-45,
        plot_bgcolor='#f8f9fa'
    )
    
    # 4. Bar chart of Residence
    residence_counts = survey_df['Residence'].value_counts()
    fig_residence = px.bar(
        x=residence_counts.index,
        y=residence_counts.values,
        title='Residence Distribution',
        labels={'x': 'Residence', 'y': 'Count'},
        color_discrete_sequence=['#667eea']
    )
    fig_residence.update_layout(
        xaxis_title='Residence',
        yaxis_title='Count',
        showlegend=False,
        xaxis_tickangle=-45,
        plot_bgcolor='#f8f9fa'
    )
    
    # 5. Scatter mapbox of locations
    map_data = survey_df[['Location Latitude', 'Location Longitude', 'Main Community']].dropna()
    
    # Debug: Print map data info
    print(f"  Map data points: {len(map_data)}")
    if len(map_data) > 0:
        print(f"  Lat range: {map_data['Location Latitude'].min():.4f} to {map_data['Location Latitude'].max():.4f}")
        print(f"  Lon range: {map_data['Location Longitude'].min():.4f} to {map_data['Location Longitude'].max():.4f}")
    
    # Calculate center point for Oahu
    if len(map_data) > 0:
        center_lat = map_data['Location Latitude'].mean()
        center_lon = map_data['Location Longitude'].mean()
    else:
        center_lat = 21.4389
        center_lon = -157.9850
    
    fig_map = px.scatter_mapbox(
        map_data,
        lat='Location Latitude',
        lon='Location Longitude',
        hover_name='Main Community',
        hover_data={'Location Latitude': ':.4f', 'Location Longitude': ':.4f'},
        title='Survey Response Locations on Oahu',
        zoom=9.5,
        height=600,
        color_discrete_sequence=['#667eea']
    )
    
    # Update map layout with explicit settings
    fig_map.update_traces(marker=dict(size=12, opacity=0.7))
    fig_map.update_layout(
        mapbox=dict(
            style='open-street-map',
            center=dict(lat=center_lat, lon=center_lon),
            zoom=9.5
        ),
        margin={"r":0,"t":40,"l":0,"b":0},
        plot_bgcolor='#f8f9fa',
        hovermode='closest'
    )
    
    # Create layout
    return dash_html.Div([
        dash_html.H2('Survey Statistics', 
                    style={'textAlign': 'center', 'color': '#2c3e50', 'margin': '20px'}),
        dash_html.P(
            f'Based on {len(survey_df)} survey responses',
            style={'textAlign': 'center', 'color': '#7f8c8d', 'marginBottom': '30px'}
        ),
        
        # Charts in a 2x2 grid
        dash_html.Div([
            # Row 1
            dash_html.Div([
                dash_html.Div([
                    dcc.Graph(figure=fig_years)
                ], style={'width': '50%', 'display': 'inline-block', 'padding': '10px', 'verticalAlign': 'top'}),
                
                dash_html.Div([
                    dcc.Graph(figure=fig_community)
                ], style={'width': '50%', 'display': 'inline-block', 'padding': '10px', 'verticalAlign': 'top'}),
            ], style={'width': '100%'}),
            
            # Row 2
            dash_html.Div([
                dash_html.Div([
                    dcc.Graph(figure=fig_occupation)
                ], style={'width': '50%', 'display': 'inline-block', 'padding': '10px', 'verticalAlign': 'top'}),
                
                dash_html.Div([
                    dcc.Graph(figure=fig_residence)
                ], style={'width': '50%', 'display': 'inline-block', 'padding': '10px', 'verticalAlign': 'top'}),
            ], style={'width': '100%'}),
            
            # Row 3 - Full width map
            dash_html.Div([
                dash_html.H3('Geographic Distribution', 
                           style={'textAlign': 'center', 'color': '#2c3e50', 'marginTop': '20px'}),
                dcc.Graph(figure=fig_map)
            ], style={'width': '100%', 'padding': '10px'}),
            
        ], style={'padding': '20px', 'maxWidth': '1400px', 'margin': '0 auto'})
    ])