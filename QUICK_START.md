# 🚀 Quick Start Guide - Knowledge Graph Filters

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Configure your Neo4j credentials in config.py
# Then run the app
python app.py
```

## Using the Filters

### 🏘️ Community Filter
**What it does**: Shows nodes associated with specific community activities

**Example queries**:
- "Show me everyone involved in Acroyoga"
- "Compare Surfing and Rock Climbing communities"
- "Find overlap between Fire Spinning and Spiritual communities"

**How to use**:
1. Click the Community dropdown
2. Select one or more communities (e.g., "Acroyoga", "Surfing")
3. Graph updates to show only selected communities and their connections

---

### 📍 Location Filter
**What it does**: Shows nodes based on where people live or are originally from

**Example queries**:
- "Who lives in Honolulu?"
- "Show people from California"
- "Compare North Shore vs Central Oahu residents"

**How to use**:
1. Click the Location dropdown
2. Select locations (e.g., "Honolulu (Diamond Head...)")
3. See geographic distribution of communities

---

### 🙏 Religion Filter
**What it does**: Shows nodes based on religious views

**Example queries**:
- "Show Christian community members"
- "Compare spiritual vs religious practitioners"
- "Find agnostic/atheist participants"

**How to use**:
1. Click the Religion dropdown
2. Select religious views (e.g., "Christian", "Spiritual")
3. Explore religious diversity in communities

---

### 🎓 Education Filter
**What it does**: Shows nodes based on education level

**Example queries**:
- "Who has graduate degrees?"
- "Show bachelor's degree holders"
- "Compare education across communities"

**How to use**:
1. Click the Education dropdown
2. Select education levels
3. Analyze educational backgrounds

---

### 👤 Gender Filter
**What it does**: Shows nodes based on gender

**Example queries**:
- "Show female participants"
- "Compare male vs female community involvement"
- "Gender distribution in specific activities"

**How to use**:
1. Click the Gender dropdown
2. Select "Male" and/or "Female"
3. Explore gender dynamics

---

### 🏳️‍🌈 Sexuality Filter
**What it does**: Shows nodes associated with LGBTQ communities

**Example queries**:
- "Show LGBTQ-associated communities"
- "Which activities have LGBTQ presence?"

**How to use**:
1. Click the Sexuality dropdown
2. Select "LGBTQ"
3. See LGBTQ community connections

---

## 🎯 Pro Tips

### Combining Filters
Filters work together with AND logic:
- Gender: "Female" + Location: "Honolulu" = Female residents of Honolulu
- Community: "Surfing" + Education: "Bachelor's" = Surfers with bachelor's degrees

### Clearing Filters
- Click the ❌ on individual selections to remove them
- Or clear entire dropdown to see all data

### Understanding Results
- **Nodes**: Number of people/entities matching your filters
- **Edges**: Number of relationships between them
- **Density**: How interconnected the filtered network is (0-1)
- **Avg Degree**: Average number of connections per node

### Query Feature
Still works alongside filters! Type natural language questions like:
- "What is the relationship between Acroyoga and Fire Spinning?"
- "How are Surfing and LGBTQ connected?"

---

## 📊 Common Use Cases

### 1. Community Exploration
**Goal**: Understand a specific community
```
1. Select community in Community filter
2. Leave other filters empty
3. Explore all aspects of that community
```

### 2. Demographic Analysis
**Goal**: Compare demographics across communities
```
1. Select multiple communities
2. Add Gender or Education filters
3. Compare distributions
```

### 3. Geographic Patterns
**Goal**: See how location affects community participation
```
1. Select one or more locations
2. View which communities are active there
3. Compare with other locations
```

### 4. Intersection Analysis
**Goal**: Find specific intersections
```
1. Select values in multiple filter categories
2. Example: Female + Spiritual + Honolulu + Graduate degree
3. Find nodes matching all criteria
```

### 5. Diversity Assessment
**Goal**: Understand diversity in a community
```
1. Select a community
2. Check the resulting religion/education/gender mix
3. Compare with other communities
```

---

## 🐛 Troubleshooting

**Problem**: No results after filtering
- **Solution**: You may have selected incompatible filters. Try removing some.

**Problem**: Filter dropdown is empty
- **Solution**: Check that your Neo4j data contains the relevant predicates.

**Problem**: Graph is too cluttered
- **Solution**: Use more specific filters or select fewer nodes in the Advanced Filters section.

**Problem**: Filters are slow
- **Solution**: Your dataset may be large. Try filtering by predicates first to reduce data.

---

## 🎓 Learning Exercise

Try this sequence to learn the system:

1. **Start broad**: Select just "Female" in Gender
   - Notice how many female nodes appear
   
2. **Add location**: Now select "Honolulu..."
   - See how the network narrows
   
3. **Add community**: Select "Surfing"
   - Find female surfers in Honolulu
   
4. **Add education**: Select "Bachelor s degree"
   - Find female surfers in Honolulu with bachelor's degrees
   
5. **Explore connections**: Look at what else these nodes are connected to

---

## 💾 Data Notes

**Filter values are extracted from your Neo4j database**:
- If a category seems empty, check your data
- Values update when you reload the app
- Case-sensitive matching (as stored in database)

**Predicates used**:
- Community: `also_involved_in`, `associated_with`, `level_of_involvement`
- Location: `lives_in`, `originally_from`
- Religion: `has_religious_view`
- Education: `has_education_level`
- Gender: `has_the_gender`
- Sexuality: `associated_with` (containing "LGBTQ")

---

## 📞 Need Help?

- Check README.md for detailed documentation
- See ARCHITECTURE.md for technical details
- Review your Neo4j data structure
- Verify config.py has correct credentials

---

**Happy exploring! 🌺**
