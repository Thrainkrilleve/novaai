"""
Simple script to extract Discord token from browser
Run this and it will try to find your token
"""

import os
import json
import base64
from pathlib import Path

def find_discord_token():
    """Try to find Discord token from common locations"""
    
    # Common Discord data paths
    paths = [
        Path(os.getenv('APPDATA')) / 'discord' / 'Local Storage' / 'leveldb',
        Path(os.getenv('APPDATA')) / 'discordcanary' / 'Local Storage' / 'leveldb',
        Path(os.getenv('APPDATA')) / 'discordptb' / 'Local Storage' / 'leveldb',
    ]
    
    tokens = []
    
    for path in paths:
        if not path.exists():
            continue
            
        print(f"Checking: {path}")
        
        for file in path.glob('*.ldb'):
            try:
                with open(file, 'r', errors='ignore') as f:
                    content = f.read()
                    # Look for token patterns
                    for line in content.split('\n'):
                        if 'authorization' in line.lower():
                            # Extract token-like strings
                            words = line.split()
                            for word in words:
                                if len(word) > 50 and '.' in word:
                                    tokens.append(word)
            except:
                pass
    
    if tokens:
        print("\n✅ Found potential tokens:")
        for i, token in enumerate(set(tokens), 1):
            print(f"{i}. {token[:50]}...")
    else:
        print("\n❌ No tokens found in Discord app data")
        print("\nTry the Network tab method:")
        print("1. Open Discord in browser")
        print("2. F12 → Network tab")
        print("3. Filter: 'users/@me'")
        print("4. Click any server/channel")
        print("5. Click the request → Headers → Request Headers → authorization")

if __name__ == "__main__":
    print("Discord Token Finder")
    print("=" * 50)
    find_discord_token()
