import json
import sys
import dbt_manifest_parser.dbt_manifest_parser as parser


# --- Esecuzione Principale  ---

# sys.argv[0] = nome script
# sys.argv[1] = path manifest.json
# sys.argv[2] = model id

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Correct input: python get_lineage.py <manifest.json> <model_unique_id>")
        sys.exit(1)

    manifest_file_path = sys.argv[1]
    input_model_id = sys.argv[2]
    output_file_name = "lineage.json"

    index = parser.build_model_index(manifest_file_path)

    if index:
        full_lineage_list = parser.get_full_lineage(index, input_model_id)
        
        if full_lineage_list is not None:
            print(f"\n3. Saving lineage in the file: '{output_file_name}'")
            try:
                # Scrittura su file JSON
                with open(output_file_name, 'w', encoding='utf-8') as f:
                    json.dump(full_lineage_list, f, indent=2, ensure_ascii=True)
                print("   -> Completed.")
            except IOError as e:
                print(f"   -> ERROR: {e}")
