import json
import sys
from .dbt_manifest_parser import get_full_lineage
from typing import Tuple, List
from pathlib import Path


def Dora_Exploradora(model_id: str, manifest_path: str = 'manifest.json', direction: str = 'both') -> Tuple[bool, List[str]]:
    """
    Analyzes dbt model lineage in the specified direction.

    Args:
        model_id: The dbt model ID to analyze
        manifest_path: Path to the dbt manifest.json file
        direction: Direction for lineage analysis:
                  - 'upstream': finds dependencies backwards (default for backward compatibility)
                  - 'downstream': finds dependencies forward (models that depend on model_id)
                  - 'both': finds both upstream and downstream dependencies

    Returns:
        Tuple[bool, List[str]]: Success status and list of models in the lineage
    """
    if not Path(manifest_path).exists() and not Path(manifest_path).is_file():
        print("❌ Manifest path non valido")
        sys.exit(1)


    input_model_id = model_id

    # Generate appropriate output filename based on direction
    if direction == 'upstream':
        output_file_name = "lineage_upstream.json"
    elif direction == 'downstream':
        output_file_name = "lineage_downstream.json"
    elif direction == 'both':
        output_file_name = "lineage.json"
    else:
        print(f"❌ Direzione non valida: {direction}. Usa 'upstream', 'downstream', o 'both'")
        return False, []
    
    lineage_list = get_full_lineage(manifest_path,input_model_id, direction)

    if lineage_list is not None:
        print(f"🤖 [Dora Exploradora]: ✅ lineage {direction} caricato con successo!\n")
        print(f"🤖 [Dora Exploradora]: 📦 salvataggio il lineage in '{output_file_name}'...")
        try:
            # Scrittura su file JSON
            with open(output_file_name, 'w', encoding='utf-8') as f:
                json.dump(lineage_list, f, indent=2, ensure_ascii=True)
            print("\t-> Completato.")
            return True, lineage_list
        except IOError as e:
            print(f"\t-> ERRORE: {e}")
            return False, [0]
