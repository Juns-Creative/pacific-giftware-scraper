"""
File management utilities for the Python development environment.
"""

import os
import shutil
from typing import List


class FileManager:
    """Handles file operations for the development environment."""
    
    def __init__(self):
        self.scripts_dir = "scripts"
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure required directories exist."""
        if not os.path.exists(self.scripts_dir):
            os.makedirs(self.scripts_dir)
            print(f"Created directory: {self.scripts_dir}")
    
    def list_scripts(self) -> List[str]:
        """List all Python scripts in the scripts directory."""
        if not os.path.exists(self.scripts_dir):
            return []
        
        scripts = []
        for file in os.listdir(self.scripts_dir):
            if file.endswith('.py') and not file.startswith('__'):
                scripts.append(file)
        
        return sorted(scripts)
    
    def create_script_template(self, name: str):
        """Create a new Python script template."""
        if not name.endswith('.py'):
            name += '.py'
        
        script_path = os.path.join(self.scripts_dir, name)
        
        if os.path.exists(script_path):
            response = input(f"Script {name} already exists. Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("Script creation cancelled.")
                return
        
        template = '''#!/usr/bin/env python3
"""
Script: {name}
Description: Add your script description here
"""

import os
import sys


def main():
    """Main function for the script."""
    print("Hello from {name}!")
    
    # Add your code here
    pass


if __name__ == "__main__":
    main()
'''.format(name=name)
        
        try:
            with open(script_path, 'w') as f:
                f.write(template)
            print(f"Created script template: {script_path}")
        except Exception as e:
            print(f"Error creating script: {e}")
    
    def get_script_path(self, script_name: str) -> str:
        """Get the full path to a script."""
        if not script_name.endswith('.py'):
            script_name += '.py'
        
        script_path = os.path.join(self.scripts_dir, script_name)
        
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Script not found: {script_name}")
        
        return script_path
    
    def copy_file(self, source: str, destination: str):
        """Copy a file from source to destination."""
        try:
            shutil.copy2(source, destination)
            print(f"Copied {source} to {destination}")
        except Exception as e:
            print(f"Error copying file: {e}")
    
    def delete_script(self, script_name: str):
        """Delete a script file."""
        script_path = self.get_script_path(script_name)
        
        try:
            os.remove(script_path)
            print(f"Deleted script: {script_name}")
        except Exception as e:
            print(f"Error deleting script: {e}")
