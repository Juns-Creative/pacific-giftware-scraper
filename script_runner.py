"""
Script execution utilities for the Python development environment.
"""

import os
import sys
import subprocess
import code
from typing import Optional


class ScriptRunner:
    """Handles script execution and environment management."""
    
    def __init__(self):
        self.scripts_dir = "scripts"
    
    def run_script(self, script_name: str, args: Optional[list] = None):
        """Run a Python script with optional arguments."""
        if not script_name.endswith('.py'):
            script_name += '.py'
        
        script_path = os.path.join(self.scripts_dir, script_name)
        
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Script not found: {script_name}")
        
        # Prepare command
        cmd = [sys.executable, script_path]
        if args:
            cmd.extend(args)
        
        print(f"Running: {script_name}")
        print("-" * 40)
        
        try:
            # Run the script
            result = subprocess.run(cmd, check=False, capture_output=False)
            print("-" * 40)
            print(f"Script completed with exit code: {result.returncode}")
            
            if result.returncode != 0:
                print(f"Script {script_name} exited with non-zero status.")
            
            return result.returncode
            
        except KeyboardInterrupt:
            print("\nScript execution interrupted by user.")
            return 130
        except Exception as e:
            print(f"Error running script: {e}")
            return 1
    
    def install_dependencies(self):
        """Install dependencies from requirements.txt."""
        if not os.path.exists("requirements.txt"):
            print("No requirements.txt found. Creating empty one...")
            with open("requirements.txt", 'w') as f:
                f.write("# Add your dependencies here\n")
            return
        
        print("Installing dependencies from requirements.txt...")
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], check=False)
            
            if result.returncode == 0:
                print("Dependencies installed successfully!")
            else:
                print("Some dependencies failed to install. Check the output above.")
                
        except Exception as e:
            print(f"Error installing dependencies: {e}")
    
    def start_shell(self):
        """Start an interactive Python shell."""
        print("Starting interactive Python shell...")
        print("Type 'exit()' or press Ctrl+D to exit.")
        print("-" * 40)
        
        # Add current directory to path
        if os.getcwd() not in sys.path:
            sys.path.insert(0, os.getcwd())
        
        # Create interactive console
        try:
            console = code.InteractiveConsole(locals={
                '__name__': '__console__',
                '__doc__': None,
                'os': os,
                'sys': sys,
            })
            console.interact()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting Python shell.")
    
    def check_syntax(self, script_name: str) -> bool:
        """Check syntax of a Python script without executing it."""
        if not script_name.endswith('.py'):
            script_name += '.py'
        
        script_path = os.path.join(self.scripts_dir, script_name)
        
        if not os.path.exists(script_path):
            print(f"Script not found: {script_name}")
            return False
        
        try:
            with open(script_path, 'r') as f:
                source = f.read()
            
            compile(source, script_path, 'exec')
            print(f"Syntax check passed for {script_name}")
            return True
            
        except SyntaxError as e:
            print(f"Syntax error in {script_name}:")
            print(f"  Line {e.lineno}: {e.text.strip() if e.text else ''}")
            print(f"  {' ' * (e.offset - 1 if e.offset else 0)}^")
            print(f"  {e.msg}")
            return False
        except Exception as e:
            print(f"Error checking syntax: {e}")
            return False
