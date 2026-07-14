import os
import glob
import re

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find 'adk create some-name'
    # We want to replace the dash with an underscore in 'some-name'
    def adk_replace(match):
        full_match = match.group(0)
        prefix = match.group(1)
        name = match.group(2)
        # only replace dashes in the name part
        new_name = name.replace('-', '_')
        return prefix + new_name

    new_content = re.sub(r'(adk create\s+(?:--type=[a-z]+\s+)?)([a-zA-Z0-9_-]+)', adk_replace, content)
    
    # Also find 'cd some-name' if they contain dashes and might correspond to the adk create command
    def cd_replace(match):
        full_match = match.group(0)
        prefix = match.group(1)
        name = match.group(2)
        new_name = name.replace('-', '_')
        return prefix + new_name
        
    new_content = re.sub(r'(cd\s+)([a-zA-Z0-9_-]+)', cd_replace, new_content)

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed dashes in {filepath}")

for root, _, files in os.walk('training'):
    for file in files:
        if file.endswith('.md') or file.endswith('.py') or file.endswith('.yaml'):
            process_file(os.path.join(root, file))
