# callbacks.py - Filter logic for full hybrid application

import pandas as pd


def filter_by_node_types(df, communities=None, locations=None, residences=None,
                         religions=None, education_levels=None, genders=None, 
                         sexualities=None):
    """
    Filter dataframe to show only Community and Main_Community nodes based on their attributes.
    
    This function:
    1. Finds communities that match the selected attribute filters
    2. Returns only triples where BOTH subject and object are Community or Main_Community nodes
    3. Filters out all Attribute nodes from the visualization
    
    Args:
        df: DataFrame with columns ['subject', 'subject_label', 'predicate', 'object', 'object_label']
        communities: List of selected community values
        locations: List of selected location values (origin)
        residences: List of selected residence values
        religions: List of selected religion values
        education_levels: List of selected education levels
        genders: List of selected gender values
        sexualities: List of selected sexuality values
    
    Returns:
        Filtered DataFrame containing only Community-to-Community relationships
    """
    filtered_df = df.copy()
    matching_communities = set()
    has_filters = False
    
    # Filter by community (direct selection)
    if communities and len(communities) > 0:
        has_filters = True
        matching_communities.update(communities)
    
    # Filter by location (originally from) - find communities with this attribute
    if locations and len(locations) > 0:
        has_filters = True
        location_communities = set(df[
            (df['predicate'] == 'ORIGINALLY_FROM') & 
            (df['object'].isin(locations))
        ]['subject'].unique())
        matching_communities.update(location_communities)
    
    # Filter by residence (lives in) - find communities with this attribute
    if residences and len(residences) > 0:
        has_filters = True
        residence_communities = set(df[
            (df['predicate'] == 'LIVES_IN') & 
            (df['object'].isin(residences))
        ]['subject'].unique())
        matching_communities.update(residence_communities)
    
    # Filter by religion - find communities with this attribute
    if religions and len(religions) > 0:
        has_filters = True
        religion_communities = set(df[
            (df['predicate'] == 'HAS_RELIGIOUS_VIEW') & 
            (df['object'].isin(religions))
        ]['subject'].unique())
        matching_communities.update(religion_communities)
    
    # Filter by education level - find communities with this attribute
    if education_levels and len(education_levels) > 0:
        has_filters = True
        education_communities = set(df[
            (df['predicate'] == 'HAS_EDUCATION_LEVEL') & 
            (df['object'].isin(education_levels))
        ]['subject'].unique())
        matching_communities.update(education_communities)
    
    # Filter by gender - find communities with this attribute
    if genders and len(genders) > 0:
        has_filters = True
        gender_communities = set(df[
            (df['predicate'] == 'HAS_THE_GENDER') & 
            (df['object'].isin(genders))
        ]['subject'].unique())
        matching_communities.update(gender_communities)
    
    # Filter by sexuality (associated_with LGBTQ) - find communities with this attribute
    if sexualities and len(sexualities) > 0:
        has_filters = True
        sexuality_communities = set(df[
            (df['predicate'] == 'ASSOCIATED_WITH') & 
            (df['object'].isin(sexualities))
        ]['subject'].unique())
        matching_communities.update(sexuality_communities)
    
    # Now filter to only show Community and Main_Community nodes
    # Only include relationships between Community/Main_Community nodes
    community_labels = {'Community', 'Main_Community'}
    
    if has_filters:
        # Filter to matching communities AND only Community-to-Community relationships
        filtered_df = df[
            (df['subject'].isin(matching_communities) | df['object'].isin(matching_communities)) &
            (df['subject_label'].isin(community_labels)) &
            (df['object_label'].isin(community_labels))
        ]
    else:
        # No filters: show all Community-to-Community relationships
        filtered_df = df[
            (df['subject_label'].isin(community_labels)) &
            (df['object_label'].isin(community_labels))
        ]
    
    return filtered_df


def get_communities_for_visualization(df):
    """
    Extract only Community and Main_Community nodes for visualization.
    
    Args:
        df: DataFrame with node label information
    
    Returns:
        Set of node names that should be visualized
    """
    community_labels = {'Community', 'Main_Community'}
    
    # Get all nodes that are Community or Main_Community
    community_subjects = set(df[df['subject_label'].isin(community_labels)]['subject'].unique())
    community_objects = set(df[df['object_label'].isin(community_labels)]['object'].unique())
    
    return community_subjects | community_objects


# Optional: Helper function to get filter statistics
def get_filter_stats(df, filtered_df):
    """
    Calculate statistics about how filters affected the data.
    
    Args:
        df: Original DataFrame
        filtered_df: Filtered DataFrame
    
    Returns:
        Dictionary with statistics
    """
    # Only count Community and Main_Community nodes
    community_labels = {'Community', 'Main_Community'}
    
    original_communities = set()
    if 'subject_label' in df.columns:
        original_communities.update(df[df['subject_label'].isin(community_labels)]['subject'].unique())
        original_communities.update(df[df['object_label'].isin(community_labels)]['object'].unique())
    else:
        original_communities = set(df['subject'].unique()) | set(df['object'].unique())
    
    filtered_communities = set()
    if 'subject_label' in filtered_df.columns:
        filtered_communities.update(filtered_df[filtered_df['subject_label'].isin(community_labels)]['subject'].unique())
        filtered_communities.update(filtered_df[filtered_df['object_label'].isin(community_labels)]['object'].unique())
    else:
        filtered_communities = set(filtered_df['subject'].unique()) | set(filtered_df['object'].unique())
    
    return {
        'original_triples': len(df),
        'filtered_triples': len(filtered_df),
        'triples_removed': len(df) - len(filtered_df),
        'original_communities': len(original_communities),
        'filtered_communities': len(filtered_communities),
        'communities_removed': len(original_communities) - len(filtered_communities),
        'reduction_percentage': round((1 - len(filtered_df) / len(df)) * 100, 2) if len(df) > 0 else 0
    }


# Example usage (for testing)
if __name__ == "__main__":
    # Test with sample data including node labels
    sample_data = {
        'subject': ['Alice', 'Bob', 'Alice', 'Charlie', 'Alice', 'Alice', 'Bob'],
        'subject_label': ['Community', 'Community', 'Community', 'Community', 'Community', 'Community', 'Community'],
        'predicate': ['LIVES_IN', 'LIVES_IN', 'HAS_THE_GENDER', 'ALSO_INVOLVED_IN', 'ALSO_INVOLVED_IN', 'ASSOCIATED_WITH', 'ASSOCIATED_WITH'],
        'object': ['Honolulu', 'Kailua', 'Female', 'Surfing', 'Acroyoga', 'Surfing', 'Acroyoga'],
        'object_label': ['Attribute', 'Attribute', 'Attribute', 'Community', 'Community', 'Community', 'Community']
    }
    
    df = pd.DataFrame(sample_data)
    
    # Test filter - should only show Community-to-Community relationships
    filtered = filter_by_node_types(
        df,
        residences=['Honolulu'],
        genders=['Female']
    )
    
    print("Original DataFrame:")
    print(df)
    print("\nFiltered DataFrame (Community-to-Community only):")
    print(filtered)
    print("\nStatistics:")
    print(get_filter_stats(df, filtered))
