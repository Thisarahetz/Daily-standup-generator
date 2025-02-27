"""
Utility functions for standup generator.
"""

import os
import sys
import datetime

def check_environment():
    """
    Check if the environment is properly set up.
    Verifies Python version and essential packages.
    
    Returns:
        bool: Whether environment check passed
    """
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 6):
        print("Error: Python 3.6 or higher is required")
        return False
    
    # Check for required packages
    required_packages = ["github"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Error: Missing required packages: {', '.join(missing_packages)}")
        print("Install them using: pip install -r requirements.txt")
        return False
    
    return True

def get_date_string(days_ago=0, format="%Y-%m-%d"):
    """
    Get a formatted date string for a given number of days ago.
    
    Args:
        days_ago (int): Number of days in the past
        format (str): Date format string
    
    Returns:
        str: Formatted date string
    """
    date = datetime.datetime.now() - datetime.timedelta(days=days_ago)
    return date.strftime(format)

def safe_filename(base_name, extension):
    """
    Create a safe filename that doesn't overwrite existing files.
    
    Args:
        base_name (str): Base filename
        extension (str): File extension
    
    Returns:
        str: Safe filename
    """
    filename = f"{base_name}.{extension}"
    count = 1
    
    while os.path.exists(filename):
        filename = f"{base_name}_{count}.{extension}"
        count += 1
    
    return filename