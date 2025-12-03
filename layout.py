
from dash import html, dcc

def get_layout(predicates, nodes):
    return html.Div([
        html.H1('Oahu Community Knowledge Graph', style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 30}),
        html.Div([
            html.Div([
                html.Label('Select Layout:'),
                dcc.Dropdown(id='layout-dropdown', options=[{'label': l, 'value': v} for l, v in [('Spring', 'spring'), ('Circular', 'circular'), ('Kamada-Kawai', 'kamada')]], value='spring'),
                html.Label('Select Predicates:'),
                dcc.Dropdown(id='predicate-dropdown', options=[{'label': p, 'value': p} for p in predicates], value=predicates, multi=True),
                html.Label('Filter by Nodes:'),
                dcc.Dropdown(id='node-dropdown', options=[{'label': n, 'value': n} for n in nodes], value=[], multi=True),
                html.Label('Visualization Type:'),
                dcc.RadioItems(id='viz-type', options=[{'label': 'Plotly', 'value': 'plotly'}, {'label': 'PyVis', 'value': 'pyvis'}], value='plotly'),
                html.Label('Query Relationships:'),
                dcc.Textarea(id='query-input', placeholder='Ask about relationships...', style={'width': '100%', 'height': '80px'}),
                html.Button('Search', id='query-button', n_clicks=0, style={'width': '100%'}),
                html.Div(id='query-response', style={'display': 'none'}),
                html.Div(id='graph-stats')
            ], style={'width': '25%', 'display': 'inline-block', 'verticalAlign': 'top'}),
            html.Div([
                dcc.Graph(id='knowledge-graph', style={'display': 'block'}),
                html.Iframe(id='pyvis-graph', style={'display': 'none', 'width': '100%', 'height': '700px'})
            ], style={'width': '70%', 'display': 'inline-block'})
        ])
    ])


