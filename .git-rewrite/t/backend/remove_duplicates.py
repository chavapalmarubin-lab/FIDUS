#!/usr/bin/env python3
"""
Remove duplicate calculate_simulation_projections functions from server.py
Keep only the first corrected version.
"""

import re

def remove_duplicates():
    with open('/app/backend/server.py', 'r') as f:
        content = f.read()
    
    # Find all function definitions
    pattern = r'def calculate_simulation_projections.*?(?=\n(?:def |class |@|\Z))'
    matches = list(re.finditer(pattern, content, re.DOTALL))
    
    print(f"Found {len(matches)} calculate_simulation_projections functions")
    
    if len(matches) > 1:
        # Keep only the first function, remove the others
        # Start from the end to preserve line numbers
        for i in range(len(matches) - 1, 0, -1):
            start = matches[i].start()
            end = matches[i].end()
            print(f"Removing function {i+1} from position {start} to {end}")
            content = content[:start] + content[end:]
    
    # Also remove duplicate API endpoints
    api_pattern = r'@api_router\.post\("/investments/simulate"\).*?(?=\n@|\n#|\nclass |\ndef |\Z)'
    api_matches = list(re.finditer(api_pattern, content, re.DOTALL))
    
    print(f"Found {len(api_matches)} /investments/simulate API endpoints")
    
    if len(api_matches) > 1:
        # Keep only the first API endpoint, remove the others  
        # Start from the end to preserve line numbers
        for i in range(len(api_matches) - 1, 0, -1):
            start = api_matches[i].start()
            end = api_matches[i].end()
            print(f"Removing API endpoint {i+1} from position {start} to {end}")
            content = content[:start] + content[end:]
    
    # Write back the cleaned content
    with open('/app/backend/server.py', 'w') as f:
        f.write(content)
    
    print("Duplicates removed successfully")

if __name__ == "__main__":
    remove_duplicates()