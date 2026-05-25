import os
import re

def update_sidebar_positions():
    training_dir = 'training'
    module_dirs = [d for d in os.listdir(training_dir) if d.startswith('module')]
    
    for d in module_dirs:
        # Extract module number
        # Matches 'module01', 'module04_5', etc.
        match = re.search(r'module(\d+)(?:_(\d+))?', d)
        if match:
            major = int(match.group(1))
            minor = match.group(2)
            
            if minor:
                pos = float(f"{major}.{minor}")
            else:
                pos = major
                
            readme_path = os.path.join(training_dir, d, 'README.md')
            if os.path.exists(readme_path):
                with open(readme_path, 'r') as f:
                    content = f.read()
                
                # Update sidebar_position in frontmatter
                # We target the one in the README.md which acts as the category index
                new_content = re.sub(r'sidebar_position: \d+(\.\d+)?', f'sidebar_position: {pos}', content)
                
                if new_content != content:
                    print(f"Updating {readme_path} to pos {pos}")
                    with open(readme_path, 'w') as f:
                        f.write(new_content)
                else:
                    # If it doesn't exist, we might need to add it or it's already correct
                    if 'sidebar_position:' not in content:
                        print(f"Warning: No sidebar_position found in {readme_path}, adding it.")
                        # Insert after first ---
                        new_content = content.replace('---\n', f'---\nsidebar_position: {pos}\n', 1)
                        with open(readme_path, 'w') as f:
                            f.write(new_content)

if __name__ == "__main__":
    update_sidebar_positions()
