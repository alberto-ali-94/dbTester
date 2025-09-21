import json
import sys
from .dbt_manifest_parser import build_model_index, get_full_lineage
from typing import Tuple, List
from pathlib import Path


def Dora_Exploradora(model_id: str, manifest_path: str = 'manifest.json') -> Tuple[bool, List[str]]:
    if not Path(manifest_path).exists() and not Path(manifest_path).is_file():
        print("❌ Manifest path non valido")
        sys.exit(1)
    
    manifest_file_path = manifest_path
    input_model_id = model_id
    output_file_name = "lineage.json"

    print(f"🤖 [Dora Exploradora]: caricamento modelli in memoria...\n")
    index = build_model_index(manifest_file_path)
    print(f"🤖 [Dora Exploradora]: 💾 {manifest_path} caricato in memoria con successo!\n")

    if index:
        full_lineage_list = get_full_lineage(index, input_model_id)
        
        if full_lineage_list is not None:
            
            print(f"🤖 [Dora Exploradora]: ✅ lineage caricato con successo!\n")
            print(f"🤖 [Dora Exploradora]: 📦 salvataggio il lineage in '{output_file_name}'...")

            try:
                # Scrittura su file JSON
                with open(output_file_name, 'w', encoding='utf-8') as f:
                    json.dump(full_lineage_list, f, indent=2, ensure_ascii=True)
                print("\t-> Completato.")
                return True, full_lineage_list
            except IOError as e:
                print(f"\t-> ERRORE: {e}")
                return False, [0]
