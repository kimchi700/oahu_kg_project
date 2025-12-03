from dash import Dash
import pandas as pd
from config import KG_FILE
# from data_loader import load_triples
from data_loader import load_triples_from_neo4j
from layout import get_layout
from callbacks import register_callbacks

# KG_FILE = "data/kg_pairs_list.txt"

app = Dash(__name__)
triples = load_triples_from_neo4j()
df = pd.DataFrame(triples, columns=['subject', 'predicate', 'object'])
predicates = sorted(df['predicate'].dropna().unique().astype(str))
all_nodes = sorted(set(df['subject'].dropna().astype(str)) | set(df['object'].dropna().astype(str)))
app.layout = get_layout(predicates, all_nodes)
register_callbacks(app, df, predicates, all_nodes)


if __name__ == '__main__':
    app.run(debug=True, port=8050)