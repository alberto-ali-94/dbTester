import json

def load_lineage():
    """Carica il database JSON."""
    file_path =  'lineage.json'
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)