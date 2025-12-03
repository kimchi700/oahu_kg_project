# -------------------------------
# callbacks.py
# -------------------------------
from dash import Input, Output, State, dcc, html
import networkx as nx
from graph_utils import create_network_graph, create_plotly_graph, create_pyvis_network
from query_handler import query_relationships

def register_callbacks(app, df, predicates, nodes):
    @app.callback([Output('query-response', 'children'), Output('query-response', 'style')], [Input('query-button', 'n_clicks')], [State('query-input', 'value')])
    def process_query(n_clicks, query_text):
        if n_clicks == 0 or not query_text:
            return '', {'display': 'none'}
        response = query_relationships(query_text, df, nodes)
        return response, {'display': 'block'}

    @app.callback([Output('knowledge-graph', 'figure'), Output('knowledge-graph', 'style'), Output('pyvis-graph', 'srcDoc'), Output('pyvis-graph', 'style'), Output('graph-stats', 'children')], [Input('layout-dropdown', 'value'), Input('viz-type', 'value'), Input('predicate-dropdown', 'value'), Input('node-dropdown', 'value')])
    def update_graph(layout_type, viz_type, selected_predicates, selected_nodes):
        if not selected_predicates: selected_predicates = predicates
        G = create_network_graph(df, layout_type, selected_predicates, selected_nodes)
        num_nodes, num_edges = G.number_of_nodes(), G.number_of_edges()
        density = nx.density(G) if num_nodes > 0 else 0
        stats = html.Div([html.Div(f'Nodes: {num_nodes}'), html.Div(f'Edges: {num_edges}'), html.Div(f'Density: {density:.3f}')])
        if viz_type == 'plotly':
            fig = create_plotly_graph(G, layout_type)
            return fig, {'display': 'block'}, '', {'display': 'none'}, stats
        else:
            net = create_pyvis_network(G)
            html_string = net.generate_html()
            return go.Figure(), {'display': 'none'}, html_string, {'display': 'block'}, stats


# -------------------------------
# app.py
# -------------------------------
from dash import Dash
import pandas as pd
from config import KG_FILE
from data_loader import load_triples
from layout import get_layout
from callbacks import register_callbacks

app = Dash(__name__)
triples = load_triples(KG_FILE)
df = pd.DataFrame(triples, columns=['subject', 'predicate', 'object'])
predicates = sorted(df['predicate'].dropna().unique().astype(str))
all_nodes = sorted(set(df['subject'].dropna().astype(str)) | set(df['object'].dropna().astype(str)))
app.layout = get_layout(predicates, all_nodes)
register_callbacks(app, df, predicates, all_nodes)

if __name__ == '__main__':
    app.run(debug=True, port=8050)
