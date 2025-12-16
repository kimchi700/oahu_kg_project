# rag_system.py - Retrieval-Augmented Generation for Oahu Community Knowledge Graph

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
import re


class CommunityKnowledgeRAG:
    """
    RAG system for querying community knowledge graph and survey data.
    Uses semantic search and structured retrieval to find relevant context.
    """
    
    def __init__(self, kg_df: pd.DataFrame, survey_df: pd.DataFrame = None):
        """
        Initialize RAG system with knowledge graph and survey data.
        
        Args:
            kg_df: Knowledge graph DataFrame with columns [subject, predicate, object]
            survey_df: Survey data DataFrame (optional)
        """
        self.kg_df = kg_df
        self.survey_df = survey_df
        self.community_index = self._build_community_index()
        
    def _build_community_index(self) -> Dict:
        """Build an index of communities and their relationships for fast lookup"""
        index = {}
        
        # Index all nodes (subjects and objects)
        all_nodes = set(self.kg_df['subject'].unique()) | set(self.kg_df['object'].unique())
        
        for node in all_nodes:
            # Get all relationships where this node is the subject
            outgoing = self.kg_df[self.kg_df['subject'] == node]
            # Get all relationships where this node is the object
            incoming = self.kg_df[self.kg_df['object'] == node]
            
            index[node] = {
                'outgoing': outgoing.to_dict('records'),
                'incoming': incoming.to_dict('records'),
                'degree': len(outgoing) + len(incoming)
            }
        
        return index
    
    def extract_communities_from_query(self, query: str) -> List[str]:
        """
        Extract community names mentioned in the query.
        Uses fuzzy matching to find community names.
        """
        query_lower = query.lower()
        mentioned_communities = []
        
        # Get all community names
        all_communities = list(self.community_index.keys())
        
        for community in all_communities:
            # Check if community name appears in query (case-insensitive)
            if community.lower() in query_lower:
                mentioned_communities.append(community)
                continue
            
            # Check for partial matches (e.g., "rock climb" matches "Rock Climbing")
            community_words = set(community.lower().split())
            query_words = set(query_lower.split())
            
            # If 2+ words match, consider it a match
            if len(community_words & query_words) >= 2:
                mentioned_communities.append(community)
            # If it's a single-word community and it matches
            elif len(community_words) == 1 and community_words & query_words:
                mentioned_communities.append(community)
        
        return mentioned_communities
    
    def retrieve_community_relationships(self, community: str, max_hops: int = 2) -> Dict:
        """
        Retrieve all relationships for a community up to N hops away.
        
        Args:
            community: Community name
            max_hops: Maximum number of relationship hops (default 2)
            
        Returns:
            Dictionary with relationship information
        """
        if community not in self.community_index:
            return {'error': f'Community "{community}" not found'}
        
        result = {
            'community': community,
            'direct_relationships': {},
            'second_hop_relationships': {}
        }
        
        # Get direct relationships
        node_data = self.community_index[community]
        
        # Categorize outgoing relationships
        for rel in node_data['outgoing']:
            pred = rel['predicate']
            obj = rel['object']
            
            if pred not in result['direct_relationships']:
                result['direct_relationships'][pred] = []
            result['direct_relationships'][pred].append(obj)
        
        # If max_hops > 1, get second-hop relationships
        if max_hops > 1:
            # Get communities this one is connected to
            connected_communities = []
            for pred in ['ALSO_INVOLVED_IN', 'ASSOCIATED_WITH']:
                if pred in result['direct_relationships']:
                    connected_communities.extend(result['direct_relationships'][pred])
            
            # For each connected community, get their relationships
            for connected in connected_communities[:10]:  # Limit to top 10 to avoid too much data
                if connected in self.community_index:
                    connected_data = self.community_index[connected]
                    result['second_hop_relationships'][connected] = {}
                    
                    for rel in connected_data['outgoing']:
                        pred = rel['predicate']
                        obj = rel['object']
                        
                        if pred not in result['second_hop_relationships'][connected]:
                            result['second_hop_relationships'][connected][pred] = []
                        result['second_hop_relationships'][connected][pred].append(obj)
        
        return result
    
    def retrieve_survey_demographics(self, community: str = None, 
                                     communities: List[str] = None) -> Dict:
        """
        Retrieve demographic data for one or more communities from survey data.
        
        Args:
            community: Single community name
            communities: List of community names (for intersection analysis)
            
        Returns:
            Dictionary with demographic statistics
        """
        if self.survey_df is None:
            return {'error': 'Survey data not available'}
        
        # Determine which communities to analyze
        target_communities = []
        if community:
            target_communities = [community]
        elif communities:
            target_communities = communities
        
        if not target_communities:
            return {'error': 'No communities specified'}
        
        # Filter survey data
        if len(target_communities) == 1:
            # Single community analysis
            filtered = self.survey_df[self.survey_df['Main Community'] == target_communities[0]]
            analysis_type = 'single_community'
        else:
            # Multi-community analysis (people involved in multiple communities)
            # Check if people are involved in ALL specified communities
            filtered = self.survey_df.copy()
            for comm in target_communities:
                # Check Main Community or Community Involvement columns
                mask = (filtered['Main Community'] == comm) | \
                       (filtered['Community Involvement'].str.contains(comm, case=False, na=False)) | \
                       (filtered['Associated Communities'].str.contains(comm, case=False, na=False))
                filtered = filtered[mask]
            analysis_type = 'multi_community'
        
        if len(filtered) == 0:
            return {
                'communities': target_communities,
                'count': 0,
                'message': 'No survey responses found for this community/combination'
            }
        
        # Calculate demographics
        demographics = {
            'communities': target_communities,
            'analysis_type': analysis_type,
            'total_responses': len(filtered),
            'gender': filtered['Gender'].value_counts().to_dict(),
            'residence': filtered['Residence'].value_counts().to_dict(),
            'education': filtered['Education'].value_counts().to_dict(),
            'religious_view': filtered['Religious View'].value_counts().to_dict(),
        }
        
        # Add numeric statistics
        if 'Years on Island:' in filtered.columns:
            years_data = filtered['Years on Island:'].dropna()
            if len(years_data) > 0:
                demographics['years_on_island'] = {
                    'mean': float(years_data.mean()),
                    'median': float(years_data.median()),
                    'min': float(years_data.min()),
                    'max': float(years_data.max())
                }
        
        if 'Age' in filtered.columns:
            demographics['age_distribution'] = filtered['Age'].value_counts().to_dict()
        
        return demographics
    
    def retrieve_relevant_context(self, query: str) -> str:
        """
        Main RAG retrieval function: Extract most relevant context for a query.
        
        This is the key function that determines what information to send to the LLM.
        
        Args:
            query: User's question
            
        Returns:
            Formatted context string with relevant information
        """
        query_lower = query.lower()
        context_parts = []
        
        # 1. Extract mentioned communities
        mentioned_communities = self.extract_communities_from_query(query)
        
        if mentioned_communities:
            context_parts.append(f"COMMUNITIES MENTIONED: {', '.join(mentioned_communities)}\n")
        
        # 2. Determine query type and retrieve accordingly
        
        # Query Type: Relationships between communities
        if any(word in query_lower for word in ['relationship', 'connect', 'link', 'involved', 'associated', 'related']):
            context_parts.append("RELATIONSHIP ANALYSIS:\n")
            for community in mentioned_communities[:3]:  # Limit to 3 communities
                rel_data = self.retrieve_community_relationships(community, max_hops=2)
                
                if 'error' not in rel_data:
                    context_parts.append(f"\n{community}:")
                    
                    # Direct relationships
                    if 'ALSO_INVOLVED_IN' in rel_data['direct_relationships']:
                        also_involved = rel_data['direct_relationships']['ALSO_INVOLVED_IN']
                        context_parts.append(f"  Also involved in: {', '.join(also_involved[:5])}")
                    
                    if 'ASSOCIATED_WITH' in rel_data['direct_relationships']:
                        associated = rel_data['direct_relationships']['ASSOCIATED_WITH']
                        context_parts.append(f"  Associated with: {', '.join(associated[:5])}")
        
        # Query Type: Demographics
        if any(word in query_lower for word in ['demographic', 'gender', 'age', 'education', 'who', 'residence', 'live']):
            context_parts.append("\nDEMOGRAPHIC DATA:\n")
            
            if len(mentioned_communities) == 1:
                # Single community demographics
                demo_data = self.retrieve_survey_demographics(community=mentioned_communities[0])
                context_parts.append(self._format_demographics(demo_data))
            elif len(mentioned_communities) > 1:
                # Multi-community demographics (intersection)
                demo_data = self.retrieve_survey_demographics(communities=mentioned_communities)
                context_parts.append(self._format_demographics(demo_data))
        
        # Query Type: Hawaiian culture/history
        if any(word in query_lower for word in ['history', 'culture', 'hawaiian', 'traditional', 'aloha', 'origin']):
            context_parts.append("\nCULTURAL CONTEXT NEEDED: This query requires Hawaiian cultural/historical knowledge.")
            context_parts.append("Use your knowledge of Hawaiian culture and traditions.")
        
        # If no specific context was retrieved, provide general overview
        if len(context_parts) <= 1:  # Only has the "COMMUNITIES MENTIONED" part
            context_parts.append("\nGENERAL COMMUNITY OVERVIEW:\n")
            
            # Get most connected communities
            top_communities = sorted(
                self.community_index.items(),
                key=lambda x: x[1]['degree'],
                reverse=True
            )[:5]
            
            for comm, data in top_communities:
                context_parts.append(f"- {comm}: {data['degree']} connections")
        
        return '\n'.join(context_parts)
    
    def _format_demographics(self, demo_data: Dict) -> str:
        """Format demographic data for LLM context"""
        if 'error' in demo_data or demo_data.get('count', 0) == 0:
            return f"No demographic data available for {demo_data.get('communities', 'specified communities')}"
        
        formatted = []
        formatted.append(f"Total responses: {demo_data['total_responses']}")
        
        if 'gender' in demo_data:
            formatted.append(f"Gender: {demo_data['gender']}")
        
        if 'residence' in demo_data:
            formatted.append(f"Residence: {demo_data['residence']}")
        
        if 'education' in demo_data:
            formatted.append(f"Education: {demo_data['education']}")
        
        if 'years_on_island' in demo_data:
            years = demo_data['years_on_island']
            formatted.append(f"Years on Island: avg={years['mean']:.1f}, median={years['median']:.1f}")
        
        return '\n'.join(formatted)


# Utility function to format RAG context for LLM prompt
def format_rag_context_for_llm(rag_context: str, query: str) -> str:
    """
    Format RAG-retrieved context into a structured prompt for the LLM.
    
    Args:
        rag_context: Retrieved context from RAG system
        query: Original user query
        
    Returns:
        Formatted prompt with context
    """
    prompt = f"""USER QUESTION: {query}

RETRIEVED RELEVANT DATA:
{rag_context}

Please answer the user's question using the data provided above. Be specific and cite the data when available.
If the data doesn't fully answer the question, use your general knowledge but make it clear when you're doing so."""

    return prompt