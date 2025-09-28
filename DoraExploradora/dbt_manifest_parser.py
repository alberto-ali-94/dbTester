# This module contains 4 functions:
#   ->  build_model_index
#   ->  get_full_lineage (supports upstream, downstream, and bidirectional lineage)
#   ->  get_downstream_lineage
#   ->  _get_upstream_lineage_internal (internal function)
# ================================= build_model_index =======================================
#
# Starting from the provided path of the artifact manifest.json it generate a dictionary
# containing ONLY the models with all their properties. Now also builds an inverse index
# for downstream dependencies.
#
# ===========================================================================================
#
# ================================= get_full_lineage ========================================
#
# Starting from a model id it finds the dependencies in the specified direction:
# - 'upstream': dependencies backwards (default for backward compatibility)
# - 'downstream': dependencies forward (models that depend on the start model)
# - 'both': both upstream and downstream dependencies
#
# ===========================================================================================
#
# ================================ get_downstream_lineage ===================================
#
# Starting from a model id it finds the dependencies forward and returns a list of all the
# dependent models (models that are affected by changes to the start model)
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




def _build_model_index(manifest_path:str="manifest.json") -> dict:
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
                        'depends_on': dependencies,
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


def _build_children_map(model_index: dict) -> dict:
    """
    Builds a mapping of each model to the list of models that depend on it (downstream dependencies).
    This function creates an inverse index to facilitate downstream lineage analysis.
    """
    children_map = {}
    for unique_id, node in model_index.items():
        for parent_id in node['depends_on']:
            if parent_id not in children_map:
                children_map[parent_id] = []
            children_map[parent_id].append(unique_id)
    return children_map

def _get_SQL_code(model_index: dict, model_id: str) -> str:
    """
    Retrieves the SQL code for a given model ID from the model index.
    """
    model_info = model_index.get(model_id)
    if model_info:
        return model_info['compiled_code']
    return "SQL code not available."

def _get_downstream_lineage (model_index: dict, children_map: dict, start_model_id: str) -> list:
    """
    Internal function to find all downstream dependencies (models that depend on the start model)
    by traversing the children_map. Returns a list of models that are affected by changes to the start_model_id.
    """
    print(f"🤖 [Dora Exploradora]: 🔍 Elaborazione del lineage downstream per: '{start_model_id}'")

    if start_model_id not in model_index:
        print(f"""🤖 [Dora Exploradora]: ❌ ERRORE: Modello '{start_model_id}' non trovato tra quelli disponibili nel
              manifest.""")
        return None
    #Struttura dati per output finale
    lineage_results_list = []
    #Struttura dati per lo stack dei nodi da esplorare. Inserisco in partenza il primo nodo perché voglio che venga
    #espanso con il dettaglio del codice SQL
    queue = [start_model_id]
    #struttura dati per tenere traccia dei nodi già esplorati (evitando di esplorare nodi già esplorati anche se
    #il DAG dbt dovrebbe evitare cicli)
    visited_nodes = set()

    while queue:
        current_model_id = queue.pop(0)
        if current_model_id in visited_nodes:
            continue
        children = children_map.get(current_model_id, [])
        for child in children:
            if child not in visited_nodes:
                visited_nodes.add(child)
                queue.append(child)
                lineage_results_list.append(
                    {"model_id": child, "SQL_code": _get_SQL_code(model_index, child)}
                )
    return lineage_results_list


def _get_upstream_lineage (model_index: dict, start_model_id: str) -> list:
    """
    Internal function to find all upstream dependencies (models that the start model depends on)
    by traversing the depends_on_nodes. Returns a list of models that are dependencies of the start_model_id.
    """
    print(f"🤖 [Dora Exploradora]: 🔍 Elaborazione del lineage upstream per: '{start_model_id}'")

    if start_model_id not in model_index:
        print(f"""🤖 [Dora Exploradora]: ❌ ERRORE: Modello '{start_model_id}' non trovato tra quelli disponibili nel
              manifest.""")
        return None
    #Struttura dati per output finale
    lineage_results_list = []
    #Struttura dati per lo stack dei nodi da esplorare. Inserisco in partenza il primo nodo perché voglio che venga
    #espanso con il dettaglio del codice SQL
    queue = [start_model_id]
    #struttura dati per tenere traccia dei nodi già esplorati (evitando di esplorare nodi già esplorati)
    visited_nodes = set()

    while queue:
        current_model_id = queue.pop(0)
        if current_model_id in visited_nodes:
            continue
        visited_nodes.add(current_model_id)
        model_info = model_index[current_model_id]
        for dependency in model_info['depends_on']:
            if dependency not in visited_nodes and dependency.startswith('model.'):
                queue.append(dependency)
            # Aggiunta del risultato nella lista con il formato "model_id","SQL_code"
            lineage_results_list.append({
                "model_id": current_model_id,
                "SQL_code": model_info['compiled_code']
            })
    return lineage_results_list




def get_full_lineage(manifest_path: str, start_model_id: str, direction: str = 'both') -> list:
    """
    Every element of model_index can be referred through model unique id and contains the deps and SQL code for each model.
    This function go through the index "model_index" and finds the full lineage of the given start_model_id

    Args:
        model_index: Dictionary containing the model index built by build_model_index
        start_model_id: The model ID to start the lineage analysis from
        direction: Direction for lineage analysis. Options:
                  - 'upstream': finds dependencies backwards (default for backward compatibility)
                  - 'downstream': finds dependencies forward (models that depend on start_model)
                  - 'both': finds both upstream and downstream dependencies

    Returns:
        List of dictionaries with model_id and SQL_code for all models in the lineage
    """
    if direction not in ['upstream', 'downstream', 'both']:
        raise ValueError("direction must be 'upstream', 'downstream', or 'both'")
    
    print(f"🤖 [Dora Exploradora]: caricamento modelli in memoria...\n")
    model_index = _build_model_index(manifest_path)
    if model_index is None:
        return None
    
    if start_model_id not in model_index:
        raise ValueError(f"""🤖 [Dora Exploradora]: ❌ ERRORE: Modello '{start_model_id}' non trovato tra quelli disponibili nel
              manifest.""")


    children_map = _build_children_map(model_index)
    if children_map is None:
        return None

    print(f"🤖 [Dora Exploradora]: 🔍 Elaborazione del lineage {direction} per: '{start_model_id}'")
    
    if direction == 'upstream':
        return _get_upstream_lineage(model_index, start_model_id)
    elif direction == 'downstream':
        return _get_downstream_lineage(model_index, children_map, start_model_id)
    elif direction == 'both':
        # Combina upstream e downstream, evitando duplicati
        upstream_results = _get_upstream_lineage(model_index, start_model_id)
        downstream_results = _get_downstream_lineage(model_index, children_map, start_model_id)

        # Crea un set per evitare duplicati basato sul model_id
        seen_models = set()
        combined_results = []

        # Aggiungi risultati upstream
        for result in upstream_results:
            if result['model_id'] not in seen_models:
                seen_models.add(result['model_id'])
                combined_results.append(result)

        # Aggiungi risultati downstream (evitando duplicati)
        for result in downstream_results:
            if result['model_id'] not in seen_models:
                seen_models.add(result['model_id'])
                combined_results.append(result)

        return combined_results