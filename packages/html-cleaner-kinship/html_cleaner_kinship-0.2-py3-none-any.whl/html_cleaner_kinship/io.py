#Loads the inventory from the JSON file.
import json
from pathlib import Path

def _load_inventory(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)
#Saves the inventory to the JSON file.
def _save_inventory(json_path, inventory):
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(inventory, f, indent=4)
    
