# Overview

A Python development environment that provides a command-line interface for managing and executing Python scripts, with specialized web scraping tools for Pacific Giftware product automation. This is a plain Python environment focused on local development, script organization, and dependency management without any web frameworks or servers. The system offers file management capabilities, script execution, interactive shell access, template creation, and comprehensive web scraping automation tools.

## Recent Changes (August 2025)

- Added Pacific Giftware web scraping project with Selenium automation
- Created interactive web scraper tool with menu-driven interface  
- Implemented simple HTTP fallback scraper for basic product information
- Added user item file processing (12238, 11358, 11982)
- Set up browser automation dependencies (chromium, chromedriver)
- Created comprehensive scraping documentation and guides
- **COMPLETED: Full Pacific Giftware integration with successful login automation**
- **Successfully extracted complete product data: names, wholesale prices, and case quantities**
- **Fixed Material-UI login form compatibility and price extraction selectors**
- **CONFIRMED: Working wholesale price extraction using environment variables and scripts/final_scraper.py**
- **URL Structure Update: Pacific Giftware now uses /product/ instead of /item/ URLs**
- **Authentication Success: junscre@outlook.com credentials confirmed working for wholesale pricing**

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Structure
- **Modular Design**: The application follows a clean separation of concerns with utility modules handling specific responsibilities
- **Command-Line Interface**: Uses argparse for a comprehensive CLI that supports multiple operations (listing scripts, running scripts, installing dependencies, interactive shell)
- **File Organization**: Implements a structured approach with dedicated directories for scripts and utilities

## Key Components

### Entry Point (main.py)
- Central command dispatcher that handles all user interactions
- Provides comprehensive help and examples for CLI usage
- Coordinates between file management and script execution modules

### File Management (utils/file_manager.py)
- **FileManager Class**: Handles directory structure, script listing, and template creation
- **Directory Management**: Ensures required directories exist and maintains organization
- **Script Templates**: Provides boilerplate code generation for new scripts

### Script Execution (utils/script_runner.py)
- **ScriptRunner Class**: Manages script execution with proper error handling
- **Process Management**: Uses subprocess for isolated script execution
- **Interactive Features**: Supports both script execution and interactive shell access

### Scripts Organization
- Dedicated `scripts/` directory for user Python scripts
- Example script demonstrates environment capabilities and best practices
- Package structure with proper `__init__.py` files

## Design Patterns
- **Factory Pattern**: Utility classes instantiated in main.py coordinate operations
- **Template Method**: Script templates provide consistent structure for new scripts
- **Command Pattern**: CLI arguments map to specific operations through method dispatch

## Error Handling Strategy
- Comprehensive exception handling for file operations and script execution
- User-friendly error messages with actionable feedback
- Graceful handling of interrupts and edge cases

# External Dependencies

## Python Standard Library
- **argparse**: Command-line argument parsing and help generation
- **os**: File system operations and environment variable access
- **sys**: Python interpreter interaction and path management
- **subprocess**: External script execution with proper isolation
- **shutil**: Advanced file operations for template management
- **code**: Interactive Python shell functionality
- **datetime**: Timestamp generation for example scripts

## Package Management
- **requirements.txt**: Dependency specification (referenced but not present in current structure)
- **pip integration**: Built-in support for installing packages from requirements file

## File System Dependencies
- Local file system for script storage and organization
- No external databases or remote storage systems
- Pure Python environment with no web server dependencies