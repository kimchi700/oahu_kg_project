import networkx as nx
import plotly.graph_objects as go
from pyvis.network import Network

def create_network_graph(triples_df, layout_type='spring', selected_predicates=None, selected_nodes=None):
    G = nx.Graph()
    predicates_to_use = selected_predicates if selected_predicates else triples_df['predicate'].unique()
    for _, row in triples_df.iterrows():
        s, p, o = str(row['subject']).strip(), str(row['predicate']).strip(), str(row['object']).strip()
        if not s or not o or s == 'nan' or o == 'nan':
            continue
        if selected_nodes and s not in selected_nodes and o not in selected_nodes:
            continue
        if p not in predicates_to_use:
            continue
        if G.has_edge(s, o):
            G[s][o]['weight'] += 1
            G[s][o].setdefault('edge_types', []).append(p)
        else:
            G.add_edge(s, o, weight=1, edge_type=p, edge_types=[p])
    return G


def create_plotly_graph(G, layout_type='spring'):
    if len(G.nodes()) == 0:
        fig = go.Figure()
        fig.update_layout(title='No data to display', xaxis={'visible': False}, yaxis={'visible': False}, height=700)
        return fig
    pos = nx.spring_layout(G, k=0.5, iterations=50) if layout_type == 'spring' else (
          nx.circular_layout(G) if layout_type == 'circular' else nx.kamada_kawai_layout(G))
    edge_traces, edge_label_traces = [], []
    for e in G.edges():
        x0, y0 = pos[e[0]]; x1, y1 = pos[e[1]]
        edge_types = G[e[0]][e[1]].get('edge_types', [])
        edge_traces.append(go.Scatter(x=[x0, x1, None], y=[y0, y1, None],
                                      mode='lines', line={'width': 1, 'color': '#888'},
                                      hovertemplate=f'{e[0]} → {e[1]}<extra></extra>', showlegend=False))
        mid_x, mid_y = (x0 + x1)/2, (y0 + y1)/2
        edge_label_traces.append(go.Scatter(x=[mid_x], y=[mid_y], mode='text', text=[', '.join(edge_types[:2])],
                                            textfont={'size': 8, 'color': '#666'}, showlegend=False))
    node_x, node_y, node_text, node_size = [], [], [], []
    for n in G.nodes():
        x, y = pos[n]; node_x.append(x); node_y.append(y)
        node_text.append(n); node_size.append(15 + G.degree(n) * 5)
    node_trace = go.Scatter(x=node_x, y=node_y, mode='markers+text', text=node_text,
                            textposition='top center', marker={'size': node_size, 'colorscale': 'Viridis'},
                            showlegend=False)
    fig = go.Figure(data=edge_traces + edge_label_traces + [node_trace])
    fig.update_layout(title='Interactive Knowledge Graph', height=700, plot_bgcolor='#f8f9fa',
                      margin=dict(b=0, l=0, r=0, t=40))
    return fig


def create_pyvis_network(G):
    net = Network(height='700px', width='100%', bgcolor='#f8f9fa', font_color='black', notebook=False)
    if len(G.nodes()) == 0: return net
    import colorsys
    nodes = list(G.nodes())
    for i, n in enumerate(nodes):
        hue = i / len(nodes)
        rgb = colorsys.hsv_to_rgb(hue, 0.7, 0.9)
        net.add_node(n, label=n, size=15 + G.degree(n) * 5,
                     color=f'#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}')
    for u, v, data in G.edges(data=True):
        label = ', '.join(data.get('edge_types', []))
        net.add_edge(u, v, label=label)
    return net
