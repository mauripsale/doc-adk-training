import os
import re

def fix_renames(filepath):
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Replace 21.5 and 39.5 dir references in markdown links
        new_content = content.replace('module21.5-custom-agents', 'module21_5-custom-agents')
        
        if new_content != content:
            with open(filepath, 'w') as f:
                f.write(new_content)
    except:
        pass

for root, _, files in os.walk('.'):
    for file in files:
        if file.endswith('.md') or file.endswith('.js'):
            fix_renames(os.path.join(root, file))

