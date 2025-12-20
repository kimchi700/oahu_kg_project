"""
neo4j_rag.py - RAG Using Neo4j Vector Index (FIXED CREDENTIALS HANDLING)
Uses Neo4j's built-in vector search - data stays in the graph database
"""

from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Tuple, Dict


class Neo4jRAG:
    """
    RAG system using Neo4j's built-in vector index
    No separate vector database needed - everything in Neo4j!
    """
    
    def __init__(self, uri, user, password, model_name='all-MiniLM-L6-v2'):
        """
        Initialize Neo4j RAG system
        
        Args:
            uri: Neo4j connection URI (e.g., 'bolt://localhost:7687')
            user: Neo4j username
            password: Neo4j password
            model_name: Embedding model to use
        """
        print("Initializing Neo4j RAG system...")
        print(f"  Connecting to Neo4j at: {uri}")
        print(f"  Username: {user}")
        
        # Connect to Neo4j
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            print("  ✓ Connected to Neo4j successfully")
        except Exception as e:
            print(f"  ✗ Failed to connect to Neo4j: {e}")
            print("\n" + "="*60)
            print("AUTHENTICATION ERROR - Please check your credentials!")
            print("="*60)
            print("\nTroubleshooting:")
            print("1. Check your config.py has correct Neo4j credentials")
            print("2. Verify Neo4j is running")
            print("3. Test connection in Neo4j Browser first")
            print("="*60 + "\n")
            raise
        
        # Load embedding model
        print(f"  Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.embedding_dimension = self.model.get_sentence_embedding_dimension()
        print(f"  ✓ Model loaded (dimension: {self.embedding_dimension})")
        
        # Check Neo4j version (skip if connection failed above)
        self._check_neo4j_version()
    
    def _check_neo4j_version(self):
        """Check if Neo4j supports vector indexes"""
        try:
            with self.driver.session() as session:
                result = session.run("CALL dbms.components() YIELD versions RETURN versions[0] as version")
                version = result.single()['version']
                print(f"  Neo4j version: {version}")
                
                # Vector indexes available in 5.11+
                major, minor = map(int, version.split('.')[:2])
                if major < 5 or (major == 5 and minor < 11):
                    print("  ⚠️  WARNING: Neo4j version < 5.11 - vector indexes may not be available")
                    print("  ⚠️  Will fall back to computing similarities in Python")
        except Exception as e:
            print(f"  ⚠️  Could not check Neo4j version: {e}")
    
    def create_vector_indexes(self):
        """
        Create vector indexes in Neo4j for relationships and communities
        This only needs to be done once!
        """
        print("\nCreating vector indexes in Neo4j...")
        
        with self.driver.session() as session:
            # Drop existing indexes if they exist
            try:
                session.run("DROP INDEX relationship_embeddings IF EXISTS")
                session.run("DROP INDEX community_embeddings IF EXISTS")
            except:
                pass
            
            # Create vector index for relationships
            # This index will be on a new 'embedding' property we'll add
            try:
                session.run(f"""
                    CREATE VECTOR INDEX relationship_embeddings IF NOT EXISTS
                    FOR ()-[r:ALSO_INVOLVED_IN|ASSOCIATED_WITH|HAS_MAIN_COMMUNITY]-()
                    ON r.embedding
                    OPTIONS {{
                        indexConfig: {{
                            `vector.dimensions`: {self.embedding_dimension},
                            `vector.similarity_function`: 'cosine'
                        }}
                    }}
                """)
                print("  ✓ Created relationship vector index")
            except Exception as e:
                print(f"  ⚠️  Could not create relationship index: {e}")
            
            # Create vector index for community nodes
            try:
                session.run(f"""
                    CREATE VECTOR INDEX community_embeddings IF NOT EXISTS
                    FOR (n:Community)
                    ON n.embedding
                    OPTIONS {{
                        indexConfig: {{
                            `vector.dimensions`: {self.embedding_dimension},
                            `vector.similarity_function`: 'cosine'
                        }}
                    }}
                """)
                print("  ✓ Created community vector index")
            except Exception as e:
                print(f"  ⚠️  Could not create community index: {e}")
    
    def index_relationships(self):
        """Add embeddings to all relationships in the graph"""
        print("\nIndexing relationships with embeddings...")
        
        with self.driver.session() as session:
            # Get all relationships
            result = session.run("""
                MATCH (c1)-[r]->(c2)
                WHERE (c1:Community OR c1:Main_Community) 
                  AND (c2:Community OR c2:Main_Community)
                RETURN id(r) as rel_id, 
                       c1.name as subject, 
                       type(r) as predicate, 
                       c2.name as object
            """)
            
            relationships = list(result)
            print(f"  Found {len(relationships)} relationships to index")
            
            # Create embeddings in batches
            batch_size = 100
            for i in range(0, len(relationships), batch_size):
                batch = relationships[i:i+batch_size]
                
                # Create text for each relationship
                texts = [f"{r['subject']} {r['predicate']} {r['object']}" 
                        for r in batch]
                
                # Generate embeddings
                embeddings = self.model.encode(texts, show_progress_bar=False)
                
                # Update Neo4j with embeddings
                for rel, embedding in zip(batch, embeddings):
                    session.run("""
                        MATCH ()-[r]->()
                        WHERE id(r) = $rel_id
                        SET r.embedding = $embedding
                    """, rel_id=rel['rel_id'], embedding=embedding.tolist())
                
                if (i + batch_size) % 500 == 0:
                    print(f"    Indexed {i + batch_size}/{len(relationships)}...")
            
            print(f"  ✓ Indexed {len(relationships)} relationships")
    
    def index_communities(self, survey_df):
        """Add embeddings to community nodes based on demographics"""
        print("\nIndexing communities with demographic embeddings...")
        
        if survey_df is None or len(survey_df) == 0:
            print("  No survey data available")
            return
        
        # Create demographic summaries for each community
        communities = {}
        for community in survey_df['Main Community'].dropna().unique():
            community_data = survey_df[survey_df['Main Community'] == community]
            
            # Create text summary
            text = f"Community: {community}. Members: {len(community_data)}. "
            
            if 'Gender' in community_data.columns:
                gender = community_data['Gender'].value_counts().to_dict()
                text += f"Gender: {gender}. "
            
            if 'Age' in community_data.columns:
                age = community_data['Age'].value_counts().to_dict()
                text += f"Age: {age}. "
            
            if 'State' in community_data.columns:
                states = community_data['State'].value_counts().head(5).to_dict()
                text += f"From: {states}. "
            
            if 'Residence' in community_data.columns:
                residence = community_data['Residence'].value_counts().to_dict()
                text += f"Lives in: {residence}. "
            
            communities[community] = text
        
        print(f"  Found {len(communities)} communities to index")
        
        # Generate embeddings
        community_names = list(communities.keys())
        texts = list(communities.values())
        embeddings = self.model.encode(texts, show_progress_bar=False)
        
        # Update Neo4j
        with self.driver.session() as session:
            for name, embedding in zip(community_names, embeddings):
                session.run("""
                    MATCH (c)
                    WHERE (c:Community OR c:Main_Community) 
                      AND c.name = $name
                    SET c.embedding = $embedding,
                        c.demographics = $text
                """, name=name, 
                    embedding=embedding.tolist(),
                    text=communities[name])
        
        print(f"  ✓ Indexed {len(communities)} communities")
    
    def retrieve_relevant_context(self, query: str, n_results: int = 10) -> Tuple[str, str]:
        """
        Retrieve relevant context using Neo4j vector search
        
        Args:
            query: User's question
            n_results: Number of results to retrieve
            
        Returns:
            Tuple of (kg_context, survey_context)
        """
        # Generate query embedding
        query_embedding = self.model.encode([query], show_progress_bar=False)[0]
        
        kg_context = ""
        survey_context = ""
        
        with self.driver.session() as session:
            # Search relationships using vector index
            try:
                # Use Neo4j's vector search if available
                result = session.run("""
                    MATCH (c1)-[r]->(c2)
                    WHERE r.embedding IS NOT NULL
                    WITH r, c1, c2,
                         vector.similarity.cosine(r.embedding, $query_embedding) AS score
                    WHERE score > 0.1
                    RETURN c1.name as subject, 
                           type(r) as predicate, 
                           c2.name as object,
                           score
                    ORDER BY score DESC
                    LIMIT $limit
                """, query_embedding=query_embedding.tolist(), limit=n_results)
                
                relationships = list(result)
                
                if relationships:
                    kg_context = "KNOWLEDGE GRAPH - Community Relationships:\n"
                    for rel in relationships:
                        kg_context += f"- {rel['subject']} {rel['predicate']} {rel['object']}\n"
                    kg_context += f"\n(Retrieved {len(relationships)} most relevant relationships)"
                
            except Exception as e:
                print(f"  Note: Vector search not available, using fallback: {e}")
                # Fallback: get all relationships and compute similarity in Python
                result = session.run("""
                    MATCH (c1)-[r]->(c2)
                    WHERE r.embedding IS NOT NULL
                    RETURN c1.name as subject, 
                           type(r) as predicate, 
                           c2.name as object,
                           r.embedding as embedding
                    LIMIT 500
                """)
                
                relationships = list(result)
                if relationships:
                    # Compute similarities
                    embeddings = np.array([r['embedding'] for r in relationships])
                    similarities = np.dot(embeddings, query_embedding)
                    
                    # Get top N
                    top_indices = np.argsort(similarities)[-n_results:][::-1]
                    
                    kg_context = "KNOWLEDGE GRAPH - Community Relationships:\n"
                    for idx in top_indices:
                        rel = relationships[idx]
                        kg_context += f"- {rel['subject']} {rel['predicate']} {rel['object']}\n"
                    kg_context += f"\n(Retrieved {len(top_indices)} most relevant relationships)"
            
            # Search communities using vector index
            try:
                result = session.run("""
                    MATCH (c)
                    WHERE (c:Community OR c:Main_Community) 
                      AND c.embedding IS NOT NULL
                    WITH c,
                         vector.similarity.cosine(c.embedding, $query_embedding) AS score
                    WHERE score > 0.1
                    RETURN c.name as community,
                           c.demographics as demographics,
                           score
                    ORDER BY score DESC
                    LIMIT $limit
                """, query_embedding=query_embedding.tolist(), limit=n_results)
                
                communities = list(result)
                
                if communities:
                    survey_context = "\n\nSURVEY DATA - Demographics and Statistics:\n"
                    for comm in communities:
                        survey_context += f"\n{comm['demographics']}"
                    survey_context += f"\n\n(Retrieved {len(communities)} most relevant communities)"
                
            except Exception as e:
                print(f"  Note: Community vector search not available: {e}")
                # Fallback
                result = session.run("""
                    MATCH (c)
                    WHERE (c:Community OR c:Main_Community) 
                      AND c.embedding IS NOT NULL
                    RETURN c.name as community,
                           c.demographics as demographics,
                           c.embedding as embedding
                    LIMIT 100
                """)
                
                communities = list(result)
                if communities:
                    embeddings = np.array([c['embedding'] for c in communities])
                    similarities = np.dot(embeddings, query_embedding)
                    top_indices = np.argsort(similarities)[-n_results:][::-1]
                    
                    survey_context = "\n\nSURVEY DATA - Demographics and Statistics:\n"
                    for idx in top_indices:
                        survey_context += f"\n{communities[idx]['demographics']}"
                    survey_context += f"\n\n(Retrieved {len(top_indices)} most relevant communities)"
        
        return kg_context, survey_context
    
    def reindex_all(self, survey_df=None):
        """Reindex everything - run this when data changes"""
        print("\n" + "="*60)
        print("Reindexing Neo4j RAG system...")
        print("="*60)
        
        # Create indexes
        self.create_vector_indexes()
        
        # Index relationships
        self.index_relationships()
        
        # Index communities (if survey data provided)
        if survey_df is not None:
            self.index_communities(survey_df)
        
        print("\n✓ Reindexing complete!")
        print("="*60 + "\n")
    
    def get_stats(self) -> Dict:
        """Get statistics about indexed data"""
        with self.driver.session() as session:
            # Count relationships with embeddings
            rel_result = session.run("""
                MATCH ()-[r]->()
                WHERE r.embedding IS NOT NULL
                RETURN count(r) as count
            """)
            rel_count = rel_result.single()['count']
            
            # Count communities with embeddings
            comm_result = session.run("""
                MATCH (c)
                WHERE (c:Community OR c:Main_Community) 
                  AND c.embedding IS NOT NULL
                RETURN count(c) as count
            """)
            comm_count = comm_result.single()['count']
            
            return {
                'kg_count': rel_count,
                'survey_count': comm_count
            }
    
    def close(self):
        """Close Neo4j connection"""
        self.driver.close()


# Global instance
_neo4j_rag = None

def get_neo4j_rag(uri=None, user=None, password=None):
    """Get or create the global Neo4j RAG instance"""
    global _neo4j_rag
    if _neo4j_rag is None:
        # Import config for credentials
        try:
            from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
            uri = uri or NEO4J_URI
            user = user or NEO4J_USER
            password = password or NEO4J_PASSWORD
            print(f"  Using credentials from config.py")
        except (ImportError, AttributeError) as e:
            print(f"  ⚠️  Warning: Could not import from config.py: {e}")
            # Use provided parameters or defaults
            uri = uri or "bolt://localhost:7687"
            user = user or "neo4j"
            password = password or "password"
            print(f"  Using default/provided credentials")
            print(f"  URI: {uri}")
            print(f"  User: {user}")
            print("\n" + "="*60)
            print("IMPORTANT: Please check your config.py file!")
            print("="*60)
            print("It should contain:")
            print("  NEO4J_URI = 'bolt://localhost:7687'")
            print("  NEO4J_USER = 'neo4j'")
            print("  NEO4J_PASSWORD = 'your_password_here'")
            print("="*60 + "\n")
        
        _neo4j_rag = Neo4jRAG(uri, user, password)
    
    return _neo4j_rag