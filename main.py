#!/usr/bin/env python3
"""
Main entry point for the Python development environment.
Provides a simple command-line interface for managing files and running scripts.
"""

import os
import sys
import argparse
from utils.file_manager import FileManager
from utils.script_runner import ScriptRunner


def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(
        description="Python Development Environment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --list-scripts          # List all Python scripts
  python main.py --run script_name.py    # Run a specific script
  python main.py --install-deps          # Install dependencies from requirements.txt
  python main.py --shell                 # Start interactive Python shell
        """
    )
    
    parser.add_argument('--list-scripts', '-ls', action='store_true',
                       help='List all Python scripts in the scripts directory')
    parser.add_argument('--run', '-r', metavar='SCRIPT',
                       help='Run a specific Python script')
    parser.add_argument('--install-deps', '-i', action='store_true',
                       help='Install dependencies from requirements.txt')
    parser.add_argument('--shell', '-s', action='store_true',
                       help='Start interactive Python shell')
    parser.add_argument('--create-script', '-c', metavar='NAME',
                       help='Create a new Python script template')
    
    args = parser.parse_args()
    
    file_manager = FileManager()
    script_runner = ScriptRunner()
    
    try:
        if args.list_scripts:
            scripts = file_manager.list_scripts()
            if scripts:
                print("Available Python scripts:")
                for script in scripts:
                    print(f"  - {script}")
            else:
                print("No Python scripts found in the scripts directory.")
        
        elif args.run:
            script_runner.run_script(args.run)
        
        elif args.install_deps:
            script_runner.install_dependencies()
        
        elif args.shell:
            script_runner.start_shell()
        
        elif args.create_script:
            file_manager.create_script_template(args.create_script)
        
        else:
            # If no arguments provided, show help and available scripts
            parser.print_help()
            print("\n" + "="*50)
            scripts = file_manager.list_scripts()
            if scripts:
                print("Available scripts:")
                for script in scripts:
                    print(f"  - {script}")
            else:
                print("No scripts found. Create one with --create-script NAME")
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
