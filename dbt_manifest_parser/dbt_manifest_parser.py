import ijson
import sys
import json

def build_model_index(manifest_path):
    """
    Reads the manifest (only one time) and build an in-memory index.
    This function reads the manifest.json received in input and creates an in-memory index with only the model nodes.
    Every element of the index can be referred through model unique id and contains the deps and SQL code for each model
    """
    print(f"1. Building model inxed from '{manifest_path}'...")
    model_index = {}
    try:
        with open(manifest_path, 'rb') as f:
            nodes_iterator = ijson.kvitems(f, 'nodes')
            for node_id, node_data in nodes_iterator:
                if node_data.get('resource_type') == 'model':
                    dependencies = node_data.get('depends_on', {}).get('nodes', [])
                    compiled_code = node_data.get('compiled_code') or node_data.get('compiled_sql', 'SQL code not available.')
                    model_index[node_id] = {
                        'depends_on_nodes': dependencies,
                        'compiled_code': compiled_code
                    }
    except FileNotFoundError:
        print(f"ERROR: File not found at '{manifest_path}'")
        return None
    except ijson.common.IncompleteJSONError as e:
        print(f"ERROR: Not a valid JSON file: {e}")
        return None
    print(f"   -> Index built successfully. Found {len(model_index)} models.")
    return model_index

def get_full_lineage(model_index, start_model_id):
    """
    Every element of model_index can be referred through model unique id and contains the deps and SQL code for each model.
    This function go through the index "model_index" and finds the full lineage of the given start_model_id
    """
    print(f"\n2. Elaborating the full lineage for: '{start_model_id}'")
    
    if start_model_id not in model_index:
        print(f"   -> ERROR: Model '{start_model_id}' not found in the index.")
        return None

    # Struttura dati per l'output finale
    lineage_results_list = []
    #Struttura dati per lo stack dei nodi da esplorare
    nodes_to_visit = []
    #struttura dati per tenere traccia dei nodi già esplorati (evitando di esplorare nodi già esplorati)
    visited_nodes = set()

    initial_parents = model_index[start_model_id]['depends_on_nodes']
    for dep_id in initial_parents:
        if dep_id.startswith('model.'):
            nodes_to_visit.append(dep_id)

    print(f"   -> Found {len(nodes_to_visit)} parent models. Beginning of the iteration...")

    while nodes_to_visit:
        current_model_id = nodes_to_visit.pop()

        if current_model_id in visited_nodes:
            continue
        
        visited_nodes.add(current_model_id)

        if current_model_id in model_index:
            model_info = model_index[current_model_id]
            
            # Aggiunta del risultato nella lista con il formato "model_id","SQL_code"
            lineage_results_list.append({
                "model_id": current_model_id,
                "SQL_code": model_info['compiled_code']
            })
            
            parents_of_current = model_info['depends_on_nodes']
            for parent_id in parents_of_current:
                if parent_id.startswith('model.'):
                    nodes_to_visit.append(parent_id)
        else:
            # Aggiungiamo anche i nodi non trovati per completezza
            lineage_results_list.append({
                "model_id": current_model_id,
                "SQL_code": "Definition not found (could be a source or a missing model)."
            })

    return lineage_results_list