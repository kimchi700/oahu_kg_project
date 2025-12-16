"""
filters.py - Filter value extraction utilities
"""

import pandas as pd


def extract_filter_values(df: pd.DataFrame) -> dict:
    """
    Extract unique values for each filter category from the dataframe.
    Only extracts Communities (not Attributes) for the community filter.
    Extracts Attribute values for all other filters.
    
    Args:
        df: DataFrame with columns including 'subject', 'object', 'predicate',
            'subject_label', 'object_label'
    
    Returns:
        Dictionary with filter options for each category
    """
    
    # Communities - only get nodes labeled as Community or Main_Community
    community_predicates = ['ALSO_INVOLVED_IN', 'ASSOCIATED_WITH']
    communities = set()
    
    if 'subject_label' in df.columns:
        # Get subjects that are Communities from community-related predicates
        for pred in community_predicates:
            community_subjects = df[
                (df['predicate'] == pred) & 
                (df['subject_label'].isin(['Community', 'Main_Community']))
            ]['subject'].dropna().unique()
            communities.update(community_subjects)
            
            # Also get objects that are Communities
            community_objects = df[
                (df['predicate'] == pred) & 
                (df['object_label'].isin(['Community', 'Main_Community']))
            ]['object'].dropna().unique()
            communities.update(community_objects)
    else:
        # Fallback if no label columns
        for pred in community_predicates:
            communities.update(df[df['predicate'] == pred]['subject'].dropna().unique())
        
        # Add top activity subjects
        activity_subjects = df['subject'].value_counts().head(50).index.tolist()
        communities.update(activity_subjects)
    
    communities = sorted([c for c in communities if isinstance(c, str) and c != 'nan'])
    
    # Locations (Originally From) - get Attribute nodes
    locations = set()
    locations.update(df[df['predicate'] == 'ORIGINALLY_FROM']['object'].dropna().unique())
    locations = sorted([loc for loc in locations if isinstance(loc, str) and loc != 'nan'])
    
    # Residence (Lives In) - get Attribute nodes
    residence = set()
    residence.update(df[df['predicate'] == 'LIVES_IN']['object'].dropna().unique())
    residence = sorted([loc for loc in residence if isinstance(loc, str) and loc != 'nan'])
    
    # Religions - get Attribute nodes
    religions = df[df['predicate'] == 'HAS_RELIGIOUS_VIEW']['object'].dropna().unique()
    religions = sorted([r for r in religions if isinstance(r, str) and r != 'nan'])
    
    # Education Levels - get Attribute nodes
    education_levels = df[df['predicate'] == 'HAS_EDUCATION_LEVEL']['object'].dropna().unique()
    education_levels = sorted([e for e in education_levels if isinstance(e, str) and e != 'nan'])
    
    # Genders - get Attribute nodes
    genders = df[df['predicate'] == 'HAS_THE_GENDER']['object'].dropna().unique()
    genders = sorted([g for g in genders if isinstance(g, str) and g != 'nan'])
    
    # Sexualities - get from LGBTQ associations
    sexualities = set()
    lgbtq_nodes = df[
        (df['predicate'] == 'ASSOCIATED_WITH') & 
        (df['object'].str.contains('LGBTQ', case=False, na=False))
    ]['object'].unique()
    sexualities.update(lgbtq_nodes)
    sexualities = sorted([s for s in sexualities if isinstance(s, str) and s != 'nan'])
    
    return {
        'communities': communities,
        'locations': locations,
        'residence': residence,
        'religions': religions,
        'education_levels': education_levels,
        'genders': genders,
        'sexualities': sexualities
    }


def get_node_type_counts(df: pd.DataFrame) -> dict:
    """
    Count nodes by their label type.
    
    Args:
        df: DataFrame with node label columns
    
    Returns:
        Dictionary with counts for each node type
    """
    if 'subject_label' not in df.columns or 'object_label' not in df.columns:
        return {}
    
    all_nodes = {}
    
    # Count subject nodes
    for _, row in df.iterrows():
        node_name = row['subject']
        node_label = row['subject_label']
        if node_name not in all_nodes:
            all_nodes[node_name] = node_label
    
    # Count object nodes
    for _, row in df.iterrows():
        node_name = row['object']
        node_label = row['object_label']
        if node_name not in all_nodes:
            all_nodes[node_name] = node_label
    
    # Aggregate counts by label
    label_counts = {}
    for node_label in all_nodes.values():
        label_counts[node_label] = label_counts.get(node_label, 0) + 1
    
    return label_counts
