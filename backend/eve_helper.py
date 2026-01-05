"""
EVE Online SDE Helper
Provides access to EVE Online Static Data Export for Nova
"""
import json
import os
from pathlib import Path
from typing import Optional, List, Dict
from functools import lru_cache

class EVEHelper:
    """Helper for querying EVE Online SDE data"""
    
    def __init__(self):
        self.sde_path = Path(__file__).parent.parent / "EveSDE"
        self.cache = {}
        self.indices = {}  # For faster lookups
        
    def _load_jsonl(self, filename: str) -> List[Dict]:
        """Load a JSONL file from the SDE"""
        if filename in self.cache:
            return self.cache[filename]
        
        filepath = self.sde_path / filename
        if not filepath.exists():
            print(f"Warning: {filename} not found at {filepath}")
            return []
        
        data = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        data.append(obj)
                    except json.JSONDecodeError as e:
                        print(f"Error parsing line {line_num} in {filename}: {e}")
                        continue
            self.cache[filename] = data
            print(f"✅ Loaded {len(data)} entries from {filename}")
        except Exception as e:
            print(f"❌ Error loading {filename}: {e}")
            return []
        
        return data
    
    def _get_localized_text(self, text_obj, lang: str = 'en') -> str:
        """Extract localized text from nested language object"""
        if isinstance(text_obj, dict):
            return text_obj.get(lang, text_obj.get('en', ''))
        return str(text_obj) if text_obj else ''
    
    def _build_type_index(self):
        """Build an index for faster type lookups"""
        if 'type_index' in self.indices:
            return
        
        types = self._load_jsonl("types.jsonl")
        self.indices['type_index'] = {}
        self.indices['type_name_index'] = {}
        
        for item in types:
            type_id = item.get('_key') or item.get('typeID')
            if type_id:
                self.indices['type_index'][type_id] = item
                
                # Index by name for faster searching
                name = self._get_localized_text(item.get('name', {})).lower()
                if name and name != '#system':  # Skip system entries
                    if name not in self.indices['type_name_index']:
                        self.indices['type_name_index'][name] = []
                    self.indices['type_name_index'][name].append(item)
        
        print(f"✅ Indexed {len(self.indices['type_index'])} types")
    
    def search_items(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for items/types by name"""
        self._build_type_index()
        
        query_lower = query.lower()
        results = []
        
        # Search through name index
        for name, items in self.indices['type_name_index'].items():
            if query_lower in name:
                for item in items:
                    if item.get('published', False):  # Only published items
                        type_id = item.get('_key') or item.get('typeID')
                        results.append({
                            'id': type_id,
                            'name': self._get_localized_text(item.get('name', {})),
                            'description': self._get_localized_text(item.get('description', {}))[:200],
                            'groupID': item.get('groupID'),
                            'mass': item.get('mass'),
                            'volume': item.get('volume'),
                            'published': item.get('published', False)
                        })
                        if len(results) >= limit:
                            return results
        
        return results
    
    def get_item_info(self, item_id: int) -> Optional[Dict]:
        """Get detailed info about a specific item"""
        self._build_type_index()
        
        item = self.indices['type_index'].get(item_id)
        if not item:
            return None
        
        return {
            'id': item_id,
            'name': self._get_localized_text(item.get('name', {})),
            'description': self._get_localized_text(item.get('description', {})),
            'groupID': item.get('groupID'),
            'mass': item.get('mass'),
            'volume': item.get('volume'),
            'capacity': item.get('capacity'),
            'portionSize': item.get('portionSize'),
            'published': item.get('published', False)
        }
    
    def search_groups(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for item groups"""
        groups = self._load_jsonl("groups.jsonl")
        query_lower = query.lower()
        
        results = []
        for group in groups:
            name = self._get_localized_text(group.get('name', {}))
            if query_lower in name.lower():
                group_id = group.get('_key') or group.get('groupID')
                results.append({
                    'id': group_id,
                    'name': name,
                    'categoryID': group.get('categoryID'),
                    'published': group.get('published', False)
                })
                if len(results) >= limit:
                    break
        
        return results
    
    def get_ship_info(self, ship_name: str) -> Optional[Dict]:
        """Get information about a ship"""
        # Ships are in groups 25-31, 237, 324, 358, 380, 381, 419, 420, etc
        ship_groups = [25, 26, 27, 28, 29, 30, 31, 237, 324, 358, 380, 381, 419, 420, 
                       463, 485, 513, 540, 541, 543, 547, 659, 830, 831, 832, 833, 834, 
                       883, 893, 894, 898, 900, 902, 906, 941, 963, 1022, 1201, 1202, 1283, 1527]
        
        self._build_type_index()
        query_lower = ship_name.lower()
        
        # Search through indexed types
        for name, items in self.indices['type_name_index'].items():
            if query_lower in name:
                for item in items:
                    if item.get('groupID') in ship_groups and item.get('published', False):
                        type_id = item.get('_key') or item.get('typeID')
                        return {
                            'id': type_id,
                            'name': self._get_localized_text(item.get('name', {})),
                            'description': self._get_localized_text(item.get('description', {})),
                            'groupID': item.get('groupID'),
                            'mass': item.get('mass'),
                            'volume': item.get('volume'),
                            'capacity': item.get('capacity'),
                        }
        
        return None
    
    def get_available_files(self) -> List[str]:
        """Get list of available SDE files"""
        if not self.sde_path.exists():
            return []
        return [f.name for f in self.sde_path.glob("*.jsonl")]
    
    def format_results_for_llm(self, results: List[Dict], context: str = "") -> str:
        """Format search results in a way the LLM can understand"""
        if not results:
            return f"{context}No results found."
        
        output = f"{context}Found {len(results)} results:\n\n"
        for i, result in enumerate(results, 1):
            output += f"{i}. **{result.get('name', 'Unknown')}**"
            if 'description' in result and result['description']:
                desc = result['description'][:200]
                output += f"\n   {desc}..."
            if 'id' in result:
                output += f"\n   ID: {result['id']}"
            if 'mass' in result:
                output += f" | Mass: {result.get('mass', 'N/A')}"
            if 'volume' in result:
                output += f" | Volume: {result.get('volume', 'N/A')}"
            output += "\n\n"
        
        return output

# Global instance
eve_helper = EVEHelper()
