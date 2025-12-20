# Quick Start Guide

Get the Oahu Community Knowledge Graph up and running in 5 minutes.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.8 or higher** installed
- **Neo4j Database** installed and running
- **Anthropic API Key** (for AI features)
- **Git** (optional, for cloning)

## Step 1: Install Python Dependencies

```bash
# Install core dependencies
pip install fastapi uvicorn dash python-fasthtml pandas networkx neo4j

# Install visualization and AI libraries
pip install plotly sentence-transformers anthropic

# Install document processing (optional)
pip install --break-system-packages python-pptx openpyxl python-docx
```

## Step 2: Set Up Neo4j

### Install Neo4j

**macOS (Homebrew):**
```bash
brew install neo4j
brew services start neo4j
```

**Windows/Linux:**
Download from https://neo4j.com/download/

### Configure Neo4j

1. Open Neo4j Browser: http://localhost:7474
2. Set your password (remember this!)
3. Create a new database or use the default

## Step 3: Configure Application

Edit `config.py` with your credentials:

```python
# Neo4j Configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "your_password_here"  # Replace with your Neo4j password

# Anthropic API Configuration
ANTHROPIC_API_KEY = "sk-ant-api03-..."  # Replace with your Anthropic API key
```

**Get Anthropic API Key:**
1. Visit https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys
4. Create a new key
5. Copy and paste into config.py

## Step 4: Load Data (First Time Only)

If you have survey data to load:

```bash
# Load data into Neo4j
python scripts/kg_ingest.py
```

**Note:** This step is optional if Neo4j already has data loaded.

## Step 5: Start the Application

```bash
python main.py
```

You should see:

```
Loading data from Neo4j...
Loaded 847 triples
Extracted filter values

Initializing Neo4j RAG system...
  ✓ Connected to Neo4j successfully
  ✓ Using existing embeddings from Neo4j

Creating Dash application...
Dash app mounted at /dash/

Creating FastHTML pages...
FastHTML pages mounted at /

======================================================================
Oahu Community Knowledge Graph - FULL HYBRID
   FastAPI + FastHTML + Dash
======================================================================

Access Points:
   Landing Page (FastHTML): http://localhost:8000/
   About (FastHTML):        http://localhost:8000/about
   Dash App:                http://localhost:8000/dash/
   API Root:                http://localhost:8000/api
   API Filters:             http://localhost:8000/api/filters
   API Docs (Swagger):      http://localhost:8000/docs

All three frameworks running on ONE server (port 8000)!

INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 6: Access the Application

Open your browser and visit:

### Landing Page
http://localhost:8000/

Features:
- Hero section with background image
- Project overview
- Quick navigation

### Dashboard
http://localhost:8000/dash/

Features:
- Interactive network visualization
- 18 different filter options
- Multiple graph layouts
- AI Search Agent
- Real-time statistics

### About Page
http://localhost:8000/about

Features:
- System architecture diagrams
- Technology stack details
- Feature descriptions

### API Documentation
http://localhost:8000/docs

Features:
- Interactive Swagger UI
- Test API endpoints
- View request/response schemas

## Quick Test

### Test the Dashboard

1. Go to http://localhost:8000/dash/
2. Select a community (e.g., "Surfing")
3. Click "Update Graph"
4. Explore the network visualization

### Test the AI Search

1. In the dashboard, click "AI Search Agent" tab
2. Ask: "What communities do rock climbers join?"
3. Wait for the AI-powered response
4. See semantic search in action

### Test the API

```bash
# Get available filters
curl http://localhost:8000/api/filters

# Should return JSON with all filter values
```

## Common Issues & Solutions

### Issue: Neo4j Connection Error

**Error Message:**
```
neo4j.exceptions.AuthError: authentication failure
```

**Solution:**
1. Verify Neo4j is running: http://localhost:7474
2. Check password in config.py matches Neo4j password
3. Test connection:
```bash
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'your_password')); driver.verify_connectivity(); print('Connected!')"
```

### Issue: Port 8000 Already in Use

**Error Message:**
```
OSError: [Errno 48] Address already in use
```

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port in main.py
uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Issue: Module Not Found

**Error Message:**
```
ModuleNotFoundError: No module named 'xxx'
```

**Solution:**
```bash
# Install missing module
pip install xxx

# Or reinstall all dependencies
pip install -r requirements.txt
```

### Issue: No Data in Dashboard

**Solution:**
1. Verify Neo4j has data:
```bash
# Open Neo4j Browser: http://localhost:7474
# Run query: MATCH (n) RETURN count(n)
```

2. If no data, run ingestion:
```bash
python scripts/kg_ingest.py
```

### Issue: AI Search Not Working

**Possible Causes:**
1. Missing Anthropic API key in config.py
2. API key invalid or expired
3. No vector indexes in Neo4j

**Solution:**
```bash
# Verify API key is set
grep ANTHROPIC_API_KEY config.py

# Reindex data (creates vector embeddings)
# In Python shell:
from neo4j_rag import get_neo4j_rag
import pandas as pd
rag = get_neo4j_rag()
survey_df = pd.read_csv('data/data_preprcd_12_18.csv')
rag.reindex_all(survey_df)
```

## Next Steps

### Customize Your Dashboard

1. Edit `dash_app.py` to modify layout
2. Add custom filters
3. Change color schemes
4. Add new visualizations

### Add Custom Pages

1. Edit `pages.py` to add routes
2. Use FastHTML components
3. Add to navigation menu

### Extend the API

1. Edit `api_routes.py`
2. Add new endpoints
3. Update Swagger documentation

## Performance Tips

### Speed Up Data Loading

```python
# In data_loader.py, use batching for large datasets
# Increase Neo4j connection pool size
```

### Optimize Vector Search

```python
# In neo4j_rag.py, adjust n_results parameter
# Lower values = faster queries
rag.retrieve_relevant_context(query, n_results=5)  # Instead of 10
```

### Cache Filter Values

```python
# Filter values are cached automatically
# Clear cache by restarting the application
```

## Resources

### Documentation
- **README.md** - Full project documentation
- **PROJECT_SUMMARY.md** - High-level project summary
- **UML_CLASS_DIAGRAM.md** - Architecture diagrams

### Code Examples
- See `dash_app.py` for dashboard examples
- See `api_routes.py` for API examples
- See `neo4j_rag.py` for RAG implementation

### Getting Help

1. Check error messages carefully
2. Review troubleshooting section above
3. Consult project documentation
4. Check Neo4j logs: `neo4j.log`
5. Enable debug mode in main.py

## Security Notes

### Production Deployment

**Important:** Before deploying to production:

1. **Change default passwords**
   - Neo4j admin password
   - Any default credentials

2. **Secure API keys**
   - Use environment variables
   - Never commit keys to Git
   - Rotate keys regularly

3. **Enable authentication**
   - Add user authentication to dashboard
   - Protect API endpoints
   - Use HTTPS

4. **Configure firewall**
   - Restrict Neo4j port (7687)
   - Only expose port 8000 if needed
   - Use reverse proxy (nginx/Apache)

### Environment Variables (Recommended)

Instead of hardcoding in config.py:

```bash
# .env file
NEO4J_PASSWORD=your_password
ANTHROPIC_API_KEY=your_key

# Load in config.py
from dotenv import load_dotenv
import os

load_dotenv()
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
```

## Summary

You should now have:
- A running application on http://localhost:8000
- Interactive dashboard with network visualizations
- AI-powered search capability
- RESTful API endpoints
- Working Neo4j connection

**Congratulations! You're ready to explore Oahu community connections.**

For detailed information, see README.md and PROJECT_SUMMARY.md.
