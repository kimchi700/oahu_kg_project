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
        """Get all available filter values from Neo4j by following relationships"""
    
        filter_options = {
            'communities': [
                'Acroyoga', 'Fire Spinning', 'Art / Vending', 'Surfing',
                'Slackline / Highline', 'Spiritual (meditations, retreats, etc.)',
                'Music Production (Djs, light production, etc.)', 'SurfBreak',
                'Dance (salsa, zouk, hip hop, etc.)', 'Rock Climbing',
                'Martial Arts', 'Running', 'Hiking', 'Diving', 'Yoga', 'Farming',
                'Business / Enterpreneurship', 'Poetry', 'Bar Scene'
            ],
            'locations': [
                'Florida', 'Pennsylvania', 'Connecticut', 'Ohio', 'New York',
                'Michigan', 'Maryland', 'New Jersey', 'Utah', 'Illinois',
                'California', 'Texas', 'Iowa', 'Delaware', 'Idaho',
                'Massachusetts', 'Nebraska', 'Hawaii', 'Missouri', 'Wisconsin',
                'Virginia', 'Colorado', 'Tennessee', 'Nevada'
            ],
            'residence': [
                'Honolulu', 'Central Oahu', 'North Shore', 'East Side', 'West Side'
            ],
            'religions': [
                'Christian', 'Agnostic, Atheist, or non-religious',
                'Buddhist', 'Spiritual', 'Other'
            ],
            'education_levels': [
                'Bachelor’s degree',
                'Associates or technical degree',
                'Graduate or professional degree (MA, MS, MBA, PhD, JD, MD, DDS etc.)',
                'Prefer not to say',
                'Some college, but no degree',
                'High school diploma or GED'
            ],
            'genders': ['Female', 'Male', 'Non-binary / third gender'],
            'sexualities': [
                'Heterosexual', 'Bisexual', 'Gay',
                'Pansexual', 'Fluid', 'Prefer not to disclose'
            ]
        }
            
        return filter_options
            
    ################# NEED TO FIX QUERIES HERE 
    def query_graph_with_filters(
            self,
            main_communities=None,
            communities=None,
            residences=None,
            locations=None,
            religions=None,
            education_levels=None,
            genders=None,
            sexualities=None,
            connection_types=None,
            community_scales=None,
            aloha_spirits=None,
            hawaiian_cultures=None,
            us_born=None,
            country=None,
            stay_on_island=None,
            relationship_status=None,
            age_ranges=None,
            occupations=None):

        """
        Query Neo4j with Cypher filters to get community relationships
        Returns DataFrame with subject, predicate, object, and labels
        
        New parameters:
        - main_communities: Filter by Main_Community nodes
        - connection_types: Filter by relationship type (ASSOCIATED_WITH, ALSO_INVOLVED_IN, HAS_MAIN_COMMUNITY)
        - community_scales: Filter by LEVEL_OF_INVOLVEMENT
        - aloha_spirits: Filter by FEELS_ALOHA_SPIRIT
        - hawaiian_cultures: Filter by HAWAIIAN_CULTURE_KNOWLEDGE
        - us_born: Filter by US_BORN_STATUS
        - countries: Filter by FROM_COUNTRY
        - stay_intentions: Filter by PLANS_TO_STAY
        - relationship_statuses: Filter by RELATIONSHIP_STATUS
        - ages: Filter by IN_AGE_RANGE_OF
        - occupations: Filter by HAS_OCCUPATION
        """
        with self.driver.session() as session:
            # Build WHERE clauses dynamically based on filters
            where_clauses = []
            params = {}
            
            # Determine relationship types to filter (connection_types)
            # Default: include ALL community connection types if not specified
            if connection_types:
                relationship_types = connection_types
            else:
                # Default: show ALL community-to-community relationship types
                relationship_types = ['HAS_MAIN_COMMUNITY', 'ASSOCIATED_WITH', 'ALSO_INVOLVED_IN']
            
            params['relationship_types'] = relationship_types
            
            # Main Community filter (for Main_Community nodes specifically)
            if main_communities:
                where_clauses.append("(c1:Main_Community AND c1.name IN $main_communities)")
                params['main_communities'] = main_communities
            
            # Community filter (for any Community or Main_Community)
            if communities:
                where_clauses.append("(c1.name IN $communities OR c2.name IN $communities)")
                params['communities'] = communities
            
            # Attribute filters - find communities that have these attributes
# Attribute filters - find communities that have these attributes
            attribute_filters = []
            
            if residences:
                attribute_filters.append("""
                    (
                        EXISTS {
                            MATCH (c1)-[:LIVES_IN]->(b)
                            WHERE b.name IN $residences
                        }
                        OR
                        EXISTS {
                            MATCH (b)-[:HAS_MAIN_COMMUNITY]->(c1)
                            WHERE b.name IN $residences
                        }
                    )
                """)
                params['residences'] = residences
            
            if locations:
                attribute_filters.append("""
                    (
                        EXISTS {
                            MATCH (c1)-[:ORIGINALLY_FROM]->(l)
                            WHERE l.name IN $locations
                        }
                        OR
                        EXISTS {
                            MATCH (l)-[:HAS_MAIN_COMMUNITY]->(c1)
                            WHERE l.name IN $locations
                        }
                    )
                """)
                params['locations'] = locations
            
            if religions:
                attribute_filters.append("""
                    (
                        EXISTS {
                            MATCH (c1)-[:HAS_RELIGIOUS_VIEW]->(attr)
                            WHERE attr.name IN $religions
                        }
                        OR
                        EXISTS {
                            MATCH (attr)-[:HAS_MAIN_COMMUNITY]->(c1)
                            WHERE attr.name IN $religions
                        }
                    )
                """)
                params['religions'] = religions
            
            if education_levels:
                attribute_filters.append("""
                    (
                        EXISTS {
                            MATCH (c1)-[:HAS_EDUCATION_LEVEL]->(attr)
                            WHERE attr.name IN $education_levels
                        }
                        OR
                        EXISTS {
                            MATCH (attr)-[:HAS_MAIN_COMMUNITY]->(c1)
                            WHERE attr.name IN $education_levels
                        }
                    )
                """)
                params['education_levels'] = education_levels
            
            if genders:
                attribute_filters.append("""
                    (
                        EXISTS {
                            MATCH (c1)-[:HAS_THE_GENDER]->(attr)
                            WHERE attr.name IN $genders
                        }
                        OR
                        EXISTS {
                            MATCH (attr)-[:HAS_MAIN_COMMUNITY]->(c1)
                            WHERE attr.name IN $genders
                        }
                    )
                """)
                params['genders'] = genders
            
            if sexualities:
                attribute_filters.append("""
                    (
                        EXISTS {
                            MATCH (c1)-[:HAS_SEXUALITY]->(attr)
                            WHERE attr.name IN $sexualities
                        }
                        OR
                        EXISTS {
                            MATCH (attr)-[:HAS_MAIN_COMMUNITY]->(c1)
                            WHERE attr.name IN $sexualities
                        }
                    )
                """)
                params['sexualities'] = sexualities
            
            # ---- NEW ATTRIBUTE FILTERS (corrected names) ----
            
            if community_scales:
                attribute_filters.append("""
                    (
                        EXISTS {
                            MATCH (c1)-[:LEVEL_OF_INVOLVEMENT]->(attr)
                            WHERE attr.name IN $community_scales
                        }
                        OR
                        EXISTS {
                            MATCH (attr)-[:HAS_MAIN_COMMUNITY]->(c1)
                            WHERE attr.name IN $community_scales
                        }
                    )
                """)
                params['community_scales'] = community_scales
            
            if aloha_spirits:
                attribute_filters.append("""
                    (
                        EXISTS {
                            MATCH (c1)-[:FEELS_ALOHA_SPIRIT]->(attr)
                            WHERE attr.name IN $aloha_spirits
                        }
                        OR
                        EXISTS {
                            MATCH (attr)-[:HAS_MAIN_COMMUNITY]->(c1)
                            WHERE attr.name IN $aloha_spirits
                        }
                    )
                """)
                params['aloha_spirits'] = aloha_spirits
            
            if hawaiian_cultures:
                attribute_filters.append("""
                    (
                        EXISTS {
                            MATCH (c1)-[:HAWAIIAN_CULTURE_KNOWLEDGE]->(attr)
                            WHERE attr.name IN $hawaiian_cultures
                        }
                        OR
                        EXISTS {
                            MATCH (attr)-[:HAS_MAIN_COMMUNITY]->(c1)
                            WHERE attr.name IN $hawaiian_cultures
                        }
                    )
                """)
                params['hawaiian_cultures'] = hawaiian_cultures
            
            if us_born:
                attribute_filters.append("""
                    (
                        EXISTS {
                            MATCH (c1)-[:US_BORN_STATUS]->(attr)
                            WHERE attr.name IN $us_born
                        }
                        OR
                        EXISTS {
                            MATCH (attr)-[:HAS_MAIN_COMMUNITY]->(c1)
                            WHERE attr.name IN $us_born
                        }
                    )
                """)
                params['us_born'] = us_born
            
            if country:
                attribute_filters.append("""
                    (
                        EXISTS {
                            MATCH (c1)-[:FROM_COUNTRY]->(attr)
                            WHERE attr.name IN $country
                        }
                        OR
                        EXISTS {
                            MATCH (attr)-[:HAS_MAIN_COMMUNITY]->(c1)
                            WHERE attr.name IN $country
                        }
                    )
                """)
                params['country'] = country
            
            if stay_on_island:
                attribute_filters.append("""
                    (
                        EXISTS {
                            MATCH (c1)-[:PLANS_TO_STAY]->(attr)
                            WHERE attr.name IN $stay_on_island
                        }
                        OR
                        EXISTS {
                            MATCH (attr)-[:HAS_MAIN_COMMUNITY]->(c1)
                            WHERE attr.name IN $stay_on_island
                        }
                    )
                """)
                params['stay_on_island'] = stay_on_island
            
            if relationship_status:
                attribute_filters.append("""
                    (
                        EXISTS {
                            MATCH (c1)-[:RELATIONSHIP_STATUS]->(attr)
                            WHERE attr.name IN $relationship_status
                        }
                        OR
                        EXISTS {
                            MATCH (attr)-[:HAS_MAIN_COMMUNITY]->(c1)
                            WHERE attr.name IN $relationship_status
                        }
                    )
                """)
                params['relationship_status'] = relationship_status
            
            if age_ranges:
                attribute_filters.append("""
                    (
                        EXISTS {
                            MATCH (c1)-[:IN_AGE_RANGE_OF]->(attr)
                            WHERE attr.name IN $age_ranges
                        }
                        OR
                        EXISTS {
                            MATCH (attr)-[:HAS_MAIN_COMMUNITY]->(c1)
                            WHERE attr.name IN $age_ranges
                        }
                    )
                """)
                params['age_ranges'] = age_ranges
            
            if occupations:
                attribute_filters.append("""
                    (
                        EXISTS {
                            MATCH (c1)-[:HAS_OCCUPATION]->(attr)
                            WHERE attr.name IN $occupations
                        }
                        OR
                        EXISTS {
                            MATCH (attr)-[:HAS_MAIN_COMMUNITY]->(c1)
                            WHERE attr.name IN $occupations
                        }
                    )
                """)
                params['occupations'] = occupations

            
            # Combine all attribute filters with OR (any matching attribute)
            if attribute_filters:
                where_clauses.append("(" + " OR ".join(attribute_filters) + ")")
            
            # Build additional WHERE conditions (use AND to append to existing WHERE)
            additional_where = ""
            if where_clauses:
                additional_where = "AND " + " AND ".join(where_clauses)

            ### Updated to include ALL relationship types by default and filter on node types
            query = f"""
            MATCH (c1)-[r]->(c2)
            WHERE (c1:Community OR c1:Main_Community) 
              AND (c2:Community OR c2:Main_Community)
              AND type(r) IN $relationship_types
              {additional_where}
            RETURN 
                c1.name as subject,
                labels(c1) as subject_labels,
                type(r) as predicate,
                c2.name as object,
                labels(c2) as object_labels
            """

            print(query)
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
    
    def get_graph_statistics(self, main_communities=None, communities=None, residences=None, locations=None,
                            religions=None, education_levels=None, genders=None, 
                            sexualities=None, connection_types=None, community_scales=None,
                            aloha_spirits=None, hawaiian_cultures=None, us_born=None,
                            countries=None, stay_intentions=None, relationship_statuses=None,
                            ages=None, occupations=None):
        """Get statistics about the filtered graph"""
        df = self.query_graph_with_filters(
            main_communities=main_communities,
            communities=communities,
            residences=residences,
            locations=locations,
            religions=religions,
            education_levels=education_levels,
            genders=genders,
            sexualities=sexualities,
            connection_types=connection_types,
            community_scales=community_scales,
            aloha_spirits=aloha_spirits,
            hawaiian_cultures=hawaiian_cultures,
            us_born=us_born,
            countries=countries,
            stay_intentions=stay_intentions,
            relationship_statuses=relationship_statuses,
            ages=ages,
            occupations=occupations
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