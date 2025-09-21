# This module contains 2 functions:
#   ->  build_model_index
#   ->  get_full_lineage
# ================================= build_model_index =======================================
#
# Starting from the provided path of the artifact manifest.json it generate a dictionary
# containing ONLY the models with all their properties
#
# ===========================================================================================
#
# ================================= get_full_lineage ========================================
#
# Starting from a model id it finds the dependencies backwards and returns a list of all the
# dependencies (models) found
#
# TO DO: find the dependencies forward
#
# ===========================================================================================
import os
import sys
try: 
    import ijson
except:
    print(f"""Errore nell'import della libreria ijson.\n
          Verifica che sia correttamente installato son il comando 'pip show ijson'\n
          Eventualmente installalo con 'pip install ijson'
          Puoi anche lanciare il comando 'pip install -r requirements.txt' dalla cartella del progetto\n""")
    sys.exit(-1)




def build_model_index(manifest_path:str) -> dict:
    """
    Reads the manifest (only one time) and build an in-memory index.
    This function reads the manifest.json received in input and creates an in-memory index with only the model nodes.
    Every element of the index can be referred through model unique id and contains the deps and SQL code for each model
    """
    print(f"🤖 [Dora Exploradora]: 🔍 Caricamento modelli da '{manifest_path}'...\n")
    model_index = {}
    try:
        with open(manifest_path, 'rb') as f:
            nodes_iterator = ijson.kvitems(f, 'nodes')
            for node_id, node_data in nodes_iterator:
                if node_data.get('resource_type') == 'model':
                    dependencies = node_data.get('depends_on', {}).get('nodes', [])
                    compiled_code = node_data.get('raw_code','Code not available')
                    #compiled_code = node_data.get('compiled_code') or node_data.get('compiled_sql', 'SQL code not available.')
                    compiled_code= compiled_code.replace('\r\n',os.linesep)
                    model_index[node_id] = {
                        'depends_on_nodes': dependencies,
                        'compiled_code': compiled_code
                    }
    except FileNotFoundError:
        print(f"🤖 [Dora Exploradora]: ❌ ERRORE: File non trovato: '{manifest_path}'\n")
        return None
    except ijson.common.IncompleteJSONError as e:
        print(f"🤖 [Dora Exploradora]: ❌ ERRORE: File JSON non valido {e}")
        return None
    print(f"[Dora Exploradora]: 🎯 Indice caricato. Trovati {len(model_index)} modelli dbt.")
    return model_index

def get_full_lineage(model_index: dict, start_model_id: str) -> list:
    """
    Every element of model_index can be referred through model unique id and contains the deps and SQL code for each model.
    This function go through the index "model_index" and finds the full lineage of the given start_model_id
    """
    print(f"🤖 [Dora Exploradora]: 🔍 Elaborazione del lineage per: '{start_model_id}'")
    
    if start_model_id not in model_index:
        print(f"""🤖 [Dora Exploradora]: ❌ ERRORE: Modello '{start_model_id}' non trovato tra quelli disponibili nel 
              manifest.""")
        return None

    # Struttura dati per l'output finale
    lineage_results_list = []
    # Struttura dati per lo stack dei nodi da esplorare. Inserisco in partenza il primo nodo perché voglio che venga 
    # espanso con il dettaglio del codice SQL
    nodes_to_visit = [start_model_id]
    #struttura dati per tenere traccia dei nodi già esplorati (evitando di esplorare nodi già esplorati)
    visited_nodes = set()

    initial_parents = model_index[start_model_id]['depends_on_nodes']
    for dep_id in initial_parents:
        if dep_id.startswith('model.'):
            nodes_to_visit.append(dep_id)

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