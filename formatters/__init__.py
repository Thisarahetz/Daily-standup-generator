"""
Formatters module for standup generator.
Provides different output format options.
"""

import json
import datetime
from .text_formatter import format_as_text
from .json_formatter import format_as_json

def format_output(standup_speech, commits, output_format="text"):
    """
    Format the final output with the standup speech and commit list.
    
    Args:
        standup_speech (str): The generated standup speech
        commits (list): List of commit data
        output_format (str): The desired output format ('text' or 'json')
    
    Returns:
        str: Formatted output
    """
    if output_format == "json":
        return format_as_json(standup_speech, commits)
    else:
        return format_as_text(standup_speech, commits)