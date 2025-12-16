# neo4j_queries.py - Direct Neo4j queries for filtering

from neo4j import GraphDatabase
import pandas as pd


class Neo4jQueryEngine:
    """Execute Cypher queries directly against Neo4j for filtering"""
    
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def get_filter_options(self):
        """Get all available filter values from Neo4j"""
        with self.driver.session() as session:
            # Get all unique attribute values by type
            query = """
            MATCH (n)
            WHERE n:Attribute OR n:Community OR n:Main_Community
            WITH labels(n) as node_labels, n.name as name
            UNWIND node_labels as label
            RETURN DISTINCT label, collect(DISTINCT name) as values
            """
            result = session.run(query)
            
            filter_options = {
                'communities': [],
                'locations': [],
                'residence': [],
                'religions': [],
                'education_levels': [],
                'genders': [],
                'sexualities': []
            }
            
            for record in result:
                label = record['label']
                values = [v for v in record['values'] if v is not None]
                
                if label in ['Community', 'Main_Community']:
                    filter_options['communities'].extend(values)
                elif label == 'Location':
                    filter_options['locations'].extend(values)
                elif label == 'Residence':
                    filter_options['residence'].extend(values)
                elif label == 'Religion':
                    filter_options['religions'].extend(values)
                elif label == 'Education':
                    filter_options['education_levels'].extend(values)
                elif label == 'Gender':
                    filter_options['genders'].extend(values)
                elif label == 'Sexuality':
                    filter_options['sexualities'].extend(values)
            
            # Remove duplicates and sort
            for key in filter_options:
                filter_options[key] = sorted(list(set(filter_options[key])))
            
            return filter_options
    
    def query_graph_with_filters(self, communities=None, residences=None, locations=None,
                                  religions=None, education_levels=None, genders=None, 
                                  sexualities=None):
        """
        Query Neo4j with Cypher filters to get community relationships
        Returns DataFrame with subject, predicate, object, and labels
        """
        with self.driver.session() as session:
            # Build WHERE clauses dynamically based on filters
            where_clauses = []
            params = {}
            
            # Community filter
            if communities:
                where_clauses.append("(c1.name IN $communities OR c2.name IN $communities)")
                params['communities'] = communities
            
            # Attribute filters - find communities that have these attributes
            attribute_filters = []
            
            if residences:
                attribute_filters.append("""
                    EXISTS {
                        MATCH (c1)-[:has_residence|lives_in]->(r:Residence)
                        WHERE r.name IN $residences
                    }
                """)
                params['residences'] = residences
            
            if locations:
                attribute_filters.append("""
                    EXISTS {
                        MATCH (c1)-[:originally_from]->(l:Location)
                        WHERE l.name IN $locations
                    }
                """)
                params['locations'] = locations
            
            if religions:
                attribute_filters.append("""
                    EXISTS {
                        MATCH (c1)-[:has_religious_view]->(rel:Religion)
                        WHERE rel.name IN $religions
                    }
                """)
                params['religions'] = religions
            
            if education_levels:
                attribute_filters.append("""
                    EXISTS {
                        MATCH (c1)-[:has_education_level]->(e:Education)
                        WHERE e.name IN $education_levels
                    }
                """)
                params['education_levels'] = education_levels
            
            if genders:
                attribute_filters.append("""
                    EXISTS {
                        MATCH (c1)-[:has_the_gender]->(g:Gender)
                        WHERE g.name IN $genders
                    }
                """)
                params['genders'] = genders
            
            if sexualities:
                attribute_filters.append("""
                    EXISTS {
                        MATCH (c1)-[:has_sexuality]->(s:Sexuality)
                        WHERE s.name IN $sexualities
                    }
                """)
                params['sexualities'] = sexualities
            
            # Combine all attribute filters with OR (any matching attribute)
            if attribute_filters:
                where_clauses.append("(" + " OR ".join(attribute_filters) + ")")
            
            # Build the main query
            where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
            
            query = f"""
            MATCH (c1)-[r]->(c2)
            WHERE (c1:Community OR c1:Main_Community) 
              AND (c2:Community OR c2:Main_Community)
              AND type(r) IN ['also_involved_in', 'associated_with']
            {where_clause}
            RETURN 
                c1.name as subject,
                labels(c1) as subject_labels,
                type(r) as predicate,
                c2.name as object,
                labels(c2) as object_labels
            """
            
            result = session.run(query, params)
            
            # Convert to DataFrame
            records = []
            for record in result:
                # Get primary label (prefer Main_Community, then Community)
                subject_label = 'Main_Community' if 'Main_Community' in record['subject_labels'] else 'Community'
                object_label = 'Main_Community' if 'Main_Community' in record['object_labels'] else 'Community'
                
                records.append({
                    'subject': record['subject'],
                    'subject_label': subject_label,
                    'predicate': record['predicate'],
                    'object': record['object'],
                    'object_label': object_label
                })
            
            df = pd.DataFrame(records)
            return df
    
    def get_community_attributes(self, community_name):
        """Get all attributes for a specific community"""
        with self.driver.session() as session:
            query = """
            MATCH (c {name: $community_name})-[r]->(attr)
            WHERE c:Community OR c:Main_Community
            RETURN 
                type(r) as relationship,
                labels(attr) as attr_labels,
                attr.name as attr_value
            """
            result = session.run(query, community_name=community_name)
            
            attributes = {
                'residence': [],
                'location': [],
                'religion': [],
                'education': [],
                'gender': [],
                'sexuality': []
            }
            
            for record in result:
                rel_type = record['relationship']
                attr_labels = record['attr_labels']
                attr_value = record['attr_value']
                
                if 'Residence' in attr_labels:
                    attributes['residence'].append(attr_value)
                elif 'Location' in attr_labels:
                    attributes['location'].append(attr_value)
                elif 'Religion' in attr_labels:
                    attributes['religion'].append(attr_value)
                elif 'Education' in attr_labels:
                    attributes['education'].append(attr_value)
                elif 'Gender' in attr_labels:
                    attributes['gender'].append(attr_value)
                elif 'Sexuality' in attr_labels:
                    attributes['sexuality'].append(attr_value)
            
            return attributes
    
    def get_graph_statistics(self, communities=None, residences=None, locations=None,
                            religions=None, education_levels=None, genders=None, 
                            sexualities=None):
        """Get statistics about the filtered graph"""
        df = self.query_graph_with_filters(
            communities=communities,
            residences=residences,
            locations=locations,
            religions=religions,
            education_levels=education_levels,
            genders=genders,
            sexualities=sexualities
        )
        
        stats = {
            'num_nodes': len(set(df['subject'].tolist() + df['object'].tolist())) if len(df) > 0 else 0,
            'num_edges': len(df),
            'num_communities': len(df[df['subject_label'] == 'Community']['subject'].unique()) if len(df) > 0 else 0,
            'num_main_communities': len(df[df['subject_label'] == 'Main_Community']['subject'].unique()) if len(df) > 0 else 0,
        }
        
        return stats


# Initialize query engine with config
def get_query_engine():
    """Get Neo4j query engine instance"""
    try:
        from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
        return Neo4jQueryEngine(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    except ImportError:
        # Fallback to environment variables or default
        import os
        uri = os.getenv('NEO4J_URI', 'neo4j+s://33f70fbd.databases.neo4j.io')
        user = os.getenv('NEO4J_USER', 'neo4j')
        password = os.getenv('NEO4J_PASSWORD', 'IEHBh2DpL5FMxfT6-p5QDz7GK2GIxh3cTIcxNJMErNY')
        return Neo4jQueryEngine(uri, user, password)


if __name__ == "__main__":
    # Test the query engine
    print("Testing Neo4j Query Engine...")
    
    engine = get_query_engine()
    
    print("\n1. Getting filter options...")
    filters = engine.get_filter_options()
    for key, values in filters.items():
        print(f"   {key}: {len(values)} options")
    
    print("\n2. Querying all communities...")
    df = engine.query_graph_with_filters()
    print(f"   Found {len(df)} relationships")
    
    print("\n3. Querying with filters (Honolulu residence)...")
    df_filtered = engine.query_graph_with_filters(residences=['Honolulu'])
    print(f"   Found {len(df_filtered)} relationships")
    
    print("\n4. Getting statistics...")
    stats = engine.get_graph_statistics(residences=['Honolulu'])
    print(f"   Nodes: {stats['num_nodes']}, Edges: {stats['num_edges']}")
    
    engine.close()
    print("\nTests completed!")