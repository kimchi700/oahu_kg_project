import networkx as nx
import plotly.graph_objects as go
from pyvis.network import Network

def create_network_graph(triples_df, layout_type='spring', selected_predicates=None, selected_nodes=None):
    """
    Create a NetworkX graph from triples, only including Community and Main_Community nodes.
    
    Args:
        triples_df: DataFrame with columns including 'subject', 'object', 'predicate', 
                    'subject_label', 'object_label'
        layout_type: Layout algorithm to use
        selected_predicates: List of predicates to include (if None, include all)
        selected_nodes: List of specific nodes to include (if None, include all Community nodes)
    
    Returns:
        NetworkX Graph with only Community and Main_Community nodes
    """
    G = nx.Graph()
    
    # Define which node labels to visualize
    visualizable_labels = {'Community', 'Main_Community'}
    
    # Filter predicates
    predicates_to_use = selected_predicates if selected_predicates else triples_df['predicate'].unique()
    
    for _, row in triples_df.iterrows():
        s = str(row['subject']).strip()
        p = str(row['predicate']).strip()
        o = str(row['object']).strip()
        
        # Skip empty or NaN values
        if not s or not o or s == 'nan' or o == 'nan':
            continue
        
        # Check if we have label information
        if 'subject_label' in row and 'object_label' in row:
            s_label = str(row['subject_label']).strip()
            o_label = str(row['object_label']).strip()
            
            # Only include nodes that are Community or Main_Community
            if s_label not in visualizable_labels or o_label not in visualizable_labels:
                continue
        
        # Apply node filter if specified
        if selected_nodes and s not in selected_nodes and o not in selected_nodes:
            continue
        
        # Apply predicate filter
        if p not in predicates_to_use:
            continue
        
        # Add edge with metadata
        if G.has_edge(s, o):
            G[s][o]['weight'] += 1
            G[s][o].setdefault('edge_types', []).append(p)
        else:
            G.add_edge(s, o, weight=1, edge_type=p, edge_types=[p])
        
        # Add node labels as attributes
        if 'subject_label' in row:
            G.nodes[s]['node_type'] = row['subject_label']
        if 'object_label' in row:
            G.nodes[o]['node_type'] = row['object_label']
    
    return G


def create_plotly_graph(G, layout_type='spring'):
    """
    Create an interactive Plotly visualization of the graph.
    Colors nodes differently based on whether they're Community or Main_Community.
    
    Args:
        G: NetworkX graph
        layout_type: 'spring', 'circular', or 'kamada'
    
    Returns:
        Plotly Figure object
    """
    if len(G.nodes()) == 0:
        fig = go.Figure()
        fig.update_layout(
            title='No data to display - try adjusting filters',
            xaxis={'visible': False},
            yaxis={'visible': False},
            height=700
        )
        return fig
    
    # Choose layout algorithm
    if layout_type == 'spring':
        pos = nx.spring_layout(G, k=0.5, iterations=50)
    elif layout_type == 'circular':
        pos = nx.circular_layout(G)
    else:  # kamada
        pos = nx.kamada_kawai_layout(G)
    
    # Create edge traces
    edge_traces = []
    edge_label_traces = []
    
    for e in G.edges():
        x0, y0 = pos[e[0]]
        x1, y1 = pos[e[1]]
        edge_types = G[e[0]][e[1]].get('edge_types', [])
        
        # Edge line
        edge_traces.append(go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            mode='lines',
            line={'width': 1, 'color': '#888'},
            hovertemplate=f'{e[0]} → {e[1]}<extra></extra>',
            showlegend=False
        ))
        
        # Edge label at midpoint
        mid_x, mid_y = (x0 + x1) / 2, (y0 + y1) / 2
        edge_label_traces.append(go.Scatter(
            x=[mid_x],
            y=[mid_y],
            mode='text',
            text=[', '.join(edge_types[:2])],  # Show first 2 edge types
            textfont={'size': 8, 'color': '#666'},
            showlegend=False
        ))
    
    # Create node traces - separate by type
    community_nodes = {'x': [], 'y': [], 'text': [], 'size': []}
    main_community_nodes = {'x': [], 'y': [], 'text': [], 'size': []}
    
    for n in G.nodes():
        x, y = pos[n]
        node_type = G.nodes[n].get('node_type', 'Community')
        size = 15 + G.degree(n) * 5
        
        if node_type == 'Main_Community':
            main_community_nodes['x'].append(x)
            main_community_nodes['y'].append(y)
            main_community_nodes['text'].append(n)
            main_community_nodes['size'].append(size)
        else:  # Community
            community_nodes['x'].append(x)
            community_nodes['y'].append(y)
            community_nodes['text'].append(n)
            community_nodes['size'].append(size)
    
    # Create node trace for Communities
    community_trace = go.Scatter(
        x=community_nodes['x'],
        y=community_nodes['y'],
        mode='markers+text',
        text=community_nodes['text'],
        textposition='top center',
        marker={
            'size': community_nodes['size'],
            'color': '#667eea',  # Purple for regular communities
            'line': {'width': 2, 'color': '#fff'}
        },
        name='Community',
        showlegend=True
    )
    
    # Create node trace for Main_Communities
    main_community_trace = go.Scatter(
        x=main_community_nodes['x'],
        y=main_community_nodes['y'],
        mode='markers+text',
        text=main_community_nodes['text'],
        textposition='top center',
        marker={
            'size': main_community_nodes['size'],
            'color': '#f56565',  # Red for main communities
            'line': {'width': 2, 'color': '#fff'}
        },
        name='Main Community',
        showlegend=True
    )
    
    # Combine all traces
    all_traces = edge_traces + edge_label_traces
    if len(community_nodes['x']) > 0:
        all_traces.append(community_trace)
    if len(main_community_nodes['x']) > 0:
        all_traces.append(main_community_trace)
    
    # Create figure
    fig = go.Figure(data=all_traces)
    fig.update_layout(
        title='Oahu Community Knowledge Graph - Community Connections',
        height=700,
        plot_bgcolor='#f8f9fa',
        margin=dict(b=0, l=0, r=0, t=40),
        xaxis={'visible': False},
        yaxis={'visible': False},
        hovermode='closest',
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='#ccc',
            borderwidth=1
        )
    )
    
    return fig


def create_pyvis_network(G):
    """
    Create a PyVis network visualization with different colors for Community types.
    
    Args:
        G: NetworkX graph
    
    Returns:
        PyVis Network object
    """
    net = Network(height='700px', width='100%', bgcolor='#f8f9fa', font_color='black', notebook=False)
    
    if len(G.nodes()) == 0:
        return net
    
    # Add nodes with colors based on type
    for n in G.nodes():
        node_type = G.nodes[n].get('node_type', 'Community')
        size = 15 + G.degree(n) * 5
        
        if node_type == 'Main_Community':
            color = '#f56565'  # Red for main communities
            title = f"{n} (Main Community)"
        else:  # Community
            color = '#667eea'  # Purple for regular communities
            title = f"{n} (Community)"
        
        net.add_node(n, label=n, size=size, color=color, title=title)
    
    # Add edges
    for u, v, data in G.edges(data=True):
        label = ', '.join(data.get('edge_types', []))
        net.add_edge(u, v, label=label, title=label)
    
    return net