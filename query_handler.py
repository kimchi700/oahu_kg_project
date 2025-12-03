import re
from dash import dcc
from config import client

def query_relationships(query_text, graph_df, nodes):
    query_lower = query_text.lower()
    match = re.search(r'(?:between\s+)?(.+?)\s+and\s+(.+?)(?:\?|$|connected|related)', query_lower)
    if not match:
        return "Invalid query format."

    node1_query, node2_query = match.group(1).strip(), match.group(2).strip()
    node1 = next((n for n in nodes if node1_query.lower() in n.lower()), None)
    node2 = next((n for n in nodes if node2_query.lower() in n.lower()), None)
    if not node1 or not node2: return "Could not find nodes."

    rels = graph_df[((graph_df['subject']==node1)&(graph_df['object']==node2))|
                    ((graph_df['subject']==node2)&(graph_df['object']==node1))]
    prompt = f"Summarize relationships between {node1} and {node2} based on {len(rels)} connections."
    gpt_summary = "API not configured."
    if client:
        try:
            resp = client.chat.completions.create(model="gpt-4o-mini",
                messages=[{"role": "system", "content": "You analyze graphs."},
                          {"role": "user", "content": prompt}],
                max_tokens=200, temperature=0.7)
            gpt_summary = resp.choices[0].message.content.strip()
        except Exception as e:
            gpt_summary = f"Error: {e}"

    response = f"### {node1} ↔ {node2}\n\n{gpt_summary}"
    return dcc.Markdown(response)
