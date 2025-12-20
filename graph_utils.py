"""
graph_utils.py - Object-Oriented Graph Visualization
Refactored to use GraphVisualizer class
"""

import networkx as nx
import plotly.graph_objects as go
from pyvis.network import Network
import pandas as pd
from typing import Optional, List, Dict, Tuple
from enum import Enum


class LayoutType(Enum):
    """Enumeration of available graph layout algorithms"""
    SPRING = 'spring'
    CIRCULAR = 'circular'
    KAMADA_KAWAI = 'kamada'


class NodeType(Enum):
    """Enumeration of node types in the knowledge graph"""
    COMMUNITY = 'Community'
    MAIN_COMMUNITY = 'Main_Community'
    ATTRIBUTE = 'Attribute'


class GraphVisualizer:
    """
    Handles creation and visualization of network graphs.
    
    Responsibilities:
    - Build NetworkX graphs from dataframes
    - Apply layout algorithms
    - Create Plotly visualizations
    - Create PyVis interactive networks
    """
    
    # Color scheme for node types
    NODE_COLORS = {
        NodeType.MAIN_COMMUNITY: '#f56565',  # Red
        NodeType.COMMUNITY: '#667eea',        # Purple
        NodeType.ATTRIBUTE: '#4ecdc4'          # Teal
    }
    
    def __init__(self, default_layout: LayoutType = LayoutType.SPRING):
        """
        Initialize GraphVisualizer.
        
        Args:
            default_layout: Default layout algorithm to use
        """
        self.default_layout = default_layout
        self.graph: Optional[nx.Graph] = None
        self.positions: Optional[Dict] = None
    
    def build_graph(self, 
                   triples_df: pd.DataFrame,
                   selected_predicates: Optional[List[str]] = None,
                   selected_nodes: Optional[List[str]] = None) -> nx.Graph:
        """
        Build a NetworkX graph from triples dataframe.
        
        Args:
            triples_df: DataFrame with subject, predicate, object columns
            selected_predicates: Filter by these predicates (None = all)
            selected_nodes: Filter by these nodes (None = all)
            
        Returns:
            NetworkX Graph object
        """
        G = nx.Graph()
        predicates_to_use = selected_predicates if selected_predicates else triples_df['predicate'].unique()
        
        for _, row in triples_df.iterrows():
            subject = str(row['subject']).strip()
            predicate = str(row['predicate']).strip()
            obj = str(row['object']).strip()
            
            # Skip invalid data
            if not subject or not obj or subject == 'nan' or obj == 'nan':
                continue
            
            # Apply node filter
            if selected_nodes and subject not in selected_nodes and obj not in selected_nodes:
                continue
            
            # Apply predicate filter
            if predicate not in predicates_to_use:
                continue
            
            # Add nodes with type information
            self._add_node_with_type(G, subject, row.get('subject_label', 'Community'))
            self._add_node_with_type(G, obj, row.get('object_label', 'Community'))
            
            # Add or update edge
            self._add_or_update_edge(G, subject, obj, predicate)
        
        self.graph = G
        return G
    
    def _add_node_with_type(self, G: nx.Graph, node: str, node_type: str) -> None:
        """Add a node to the graph with type information."""
        if not G.has_node(node):
            G.add_node(node, node_type=node_type)
    
    def _add_or_update_edge(self, G: nx.Graph, source: str, target: str, predicate: str) -> None:
        """Add a new edge or update existing edge with predicate."""
        if G.has_edge(source, target):
            G[source][target]['weight'] += 1
            G[source][target].setdefault('edge_types', []).append(predicate)
        else:
            G.add_edge(source, target, weight=1, edge_type=predicate, edge_types=[predicate])
    
    def calculate_layout(self, 
                        layout_type: Optional[LayoutType] = None,
                        **layout_kwargs) -> Dict:
        """
        Calculate node positions using specified layout algorithm.
        
        Args:
            layout_type: Layout algorithm to use (None = use default)
            **layout_kwargs: Additional arguments for layout algorithm
            
        Returns:
            Dictionary mapping node names to (x, y) positions
        """
        if self.graph is None:
            raise ValueError("Graph must be built before calculating layout")
        
        layout = layout_type or self.default_layout
        
        if layout == LayoutType.SPRING:
            self.positions = nx.spring_layout(
                self.graph, 
                k=layout_kwargs.get('k', 0.5),
                iterations=layout_kwargs.get('iterations', 50)
            )
        elif layout == LayoutType.CIRCULAR:
            self.positions = nx.circular_layout(self.graph)
        elif layout == LayoutType.KAMADA_KAWAI:
            self.positions = nx.kamada_kawai_layout(self.graph)
        else:
            raise ValueError(f"Unknown layout type: {layout}")
        
        return self.positions
    
    def create_plotly_figure(self, 
                            title: str = 'Interactive Knowledge Graph',
                            height: int = 700) -> go.Figure:
        """
        Create an interactive Plotly figure from the graph.
        
        Args:
            title: Graph title
            height: Figure height in pixels
            
        Returns:
            Plotly Figure object
        """
        if self.graph is None or len(self.graph.nodes()) == 0:
            return self._create_empty_figure(title, height)
        
        if self.positions is None:
            self.calculate_layout()
        
        # Create edge traces
        edge_traces = self._create_edge_traces()
        edge_label_traces = self._create_edge_label_traces()
        
        # Create node trace
        node_trace = self._create_node_trace()
        
        # Combine all traces
        fig = go.Figure(data=edge_traces + edge_label_traces + [node_trace])
        fig.update_layout(
            title=title,
            height=height,
            plot_bgcolor='#f8f9fa',
            margin=dict(b=0, l=0, r=0, t=40),
            showlegend=False,
            hovermode='closest',
            xaxis={'visible': False},
            yaxis={'visible': False}
        )
        
        return fig
    
    def _create_empty_figure(self, title: str, height: int) -> go.Figure:
        """Create an empty figure when there's no data."""
        fig = go.Figure()
        fig.update_layout(
            title=title or 'No data to display',
            xaxis={'visible': False},
            yaxis={'visible': False},
            height=height
        )
        return fig
    
    def _create_edge_traces(self) -> List[go.Scatter]:
        """Create Plotly traces for edges."""
        edge_traces = []
        
        for edge in self.graph.edges():
            x0, y0 = self.positions[edge[0]]
            x1, y1 = self.positions[edge[1]]
            
            edge_traces.append(go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line={'width': 1, 'color': '#888'},
                hovertemplate=f'{edge[0]} → {edge[1]}<extra></extra>',
                showlegend=False
            ))
        
        return edge_traces
    
    def _create_edge_label_traces(self) -> List[go.Scatter]:
        """Create Plotly traces for edge labels."""
        edge_label_traces = []
        
        for edge in self.graph.edges():
            x0, y0 = self.positions[edge[0]]
            x1, y1 = self.positions[edge[1]]
            mid_x, mid_y = (x0 + x1) / 2, (y0 + y1) / 2
            
            edge_types = self.graph[edge[0]][edge[1]].get('edge_types', [])
            label = ', '.join(edge_types[:2])  # Limit to 2 types for clarity
            
            edge_label_traces.append(go.Scatter(
                x=[mid_x],
                y=[mid_y],
                mode='text',
                text=[label],
                textfont={'size': 8, 'color': '#666'},
                showlegend=False
            ))
        
        return edge_label_traces
    
    def _create_node_trace(self) -> go.Scatter:
        """Create Plotly trace for nodes."""
        node_x, node_y = [], []
        node_text, node_size = [], []
        node_hover, node_color = [], []
        
        for node in self.graph.nodes():
            x, y = self.positions[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)
            
            # Size based on degree
            degree = self.graph.degree(node)
            node_size.append(15 + degree * 5)
            
            # Hover text
            node_type = self.graph.nodes[node].get('node_type', 'Community')
            node_hover.append(f'{node}<br>Type: {node_type}<br>Connections: {degree}')
            
            # Color based on type
            node_color.append(self._get_node_color(node_type))
        
        return go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            text=node_text,
            textposition='top center',
            hovertext=node_hover,
            hovertemplate='%{hovertext}<extra></extra>',
            marker={'size': node_size, 'color': node_color},
            showlegend=False
        )
    
    def _get_node_color(self, node_type: str) -> str:
        """Get color for node based on its type."""
        try:
            node_type_enum = NodeType(node_type)
            return self.NODE_COLORS[node_type_enum]
        except (ValueError, KeyError):
            return self.NODE_COLORS[NodeType.COMMUNITY]  # Default
    
    def create_pyvis_network(self,
                           height: str = '700px',
                           width: str = '100%',
                           bgcolor: str = '#f8f9fa') -> Network:
        """
        Create an interactive PyVis network visualization.
        
        Args:
            height: Network height
            width: Network width
            bgcolor: Background color
            
        Returns:
            PyVis Network object
        """
        net = Network(height=height, width=width, bgcolor=bgcolor, 
                     font_color='black', notebook=False)
        
        if self.graph is None or len(self.graph.nodes()) == 0:
            return net
        
        import colorsys
        nodes = list(self.graph.nodes())
        
        # Add nodes with colors
        for i, node in enumerate(nodes):
            hue = i / len(nodes)
            rgb = colorsys.hsv_to_rgb(hue, 0.7, 0.9)
            color = f'#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}'
            
            size = 15 + self.graph.degree(node) * 5
            net.add_node(node, label=node, size=size, color=color)
        
        # Add edges
        for u, v, data in self.graph.edges(data=True):
            label = ', '.join(data.get('edge_types', []))
            net.add_edge(u, v, label=label)
        
        return net
    
    def get_graph_statistics(self) -> Dict:
        """
        Calculate graph statistics.
        
        Returns:
            Dictionary with graph metrics
        """
        if self.graph is None:
            return {
                'nodes': 0,
                'edges': 0,
                'density': 0.0,
                'avg_degree': 0.0
            }
        
        num_nodes = self.graph.number_of_nodes()
        num_edges = self.graph.number_of_edges()
        density = nx.density(self.graph) if num_nodes > 0 else 0
        avg_degree = (2 * num_edges / num_nodes) if num_nodes > 0 else 0
        
        return {
            'nodes': num_nodes,
            'edges': num_edges,
            'density': round(density, 3),
            'avg_degree': round(avg_degree, 2)
        }


# Backward compatibility: functional interface
def create_network_graph(triples_df, layout_type='spring', selected_predicates=None, selected_nodes=None):
    """Legacy function - builds graph using GraphVisualizer class."""
    visualizer = GraphVisualizer()
    return visualizer.build_graph(triples_df, selected_predicates, selected_nodes)


def create_plotly_graph(G, layout_type='spring'):
    """Legacy function - creates Plotly figure using GraphVisualizer class."""
    visualizer = GraphVisualizer()
    visualizer.graph = G
    visualizer.calculate_layout(LayoutType(layout_type))
    return visualizer.create_plotly_figure()


def create_pyvis_network(G):
    """Legacy function - creates PyVis network using GraphVisualizer class."""
    visualizer = GraphVisualizer()
    visualizer.graph = G
    return visualizer.create_pyvis_network()