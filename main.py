#!/usr/bin/env python3
"""
Daily Standup Generator using GitHub commits and AI
-----------------------------------------
This script fetches your GitHub commits from the previous day and generates
a concise standup speech using AI models.
"""

import sys
import datetime
import argparse
from config import load_config, save_config, get_user_input
from github_client import get_commits_since_date
from ai_providers import get_ai_provider
from formatters import format_output

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate daily standup from GitHub commits")
    parser.add_argument("--github-token", help="GitHub Personal Access Token")
    parser.add_argument("--anthropic-api-key", help="Anthropic API Key")
    parser.add_argument("--openai-api-key", help="OpenAI API Key")
    parser.add_argument("--gemini-api-key", help="Google Gemini API Key")
    parser.add_argument("--ai-provider", choices=["anthropic", "openai", "gemini", "local"], default="gemini", 
                        help="AI provider to use for generating standup (default: gemini)")
    parser.add_argument("--repos", nargs="+", help="List of repositories to fetch commits from (format: owner/repo)")
    parser.add_argument("--branches", nargs="+", help="List of branches for each repo (in same order as repos)")
    parser.add_argument("--days", type=int, default=1, help="Number of days to look back for commits (default: 1)")
    parser.add_argument("--username", help="GitHub username to filter commits by")
    parser.add_argument("--output", choices=["text", "json"], default="text", help="Output format (default: text)")
    parser.add_argument("--save", action="store_true", help="Save the output to a file")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--reset-config", action="store_true", help="Reset saved configuration")
    parser.add_argument("--local", action="store_true", help="Use local templating (no API calls)")
    
    return parser.parse_args()

def main():
    """Main function to run the script."""
    args = parse_arguments()
    
    # Get configuration from interactive mode, args, or saved config
    if args.interactive:
        config = get_user_input(args.reset_config)
    else:
        config = load_config()
        
        # Override with command line arguments
        if args.github_token:
            config["github_token"] = args.github_token
        if args.anthropic_api_key:
            config["anthropic_api_key"] = args.anthropic_api_key
        if args.openai_api_key:
            config["openai_api_key"] = args.openai_api_key
        if args.gemini_api_key:
            config["gemini_api_key"] = args.gemini_api_key
        if args.ai_provider:
            config["ai_provider"] = args.ai_provider
        if args.repos:
            config["repos"] = args.repos
        if args.username:
            config["username"] = args.username
        if args.output:
            config["output"] = args.output
        if args.save:
            config["save"] = args.save
        
        # Handle branches from command line args
        if args.branches and args.repos and len(args.branches) == len(args.repos):
            config["branches"] = {repo: branch for repo, branch in zip(args.repos, args.branches)}
        elif args.branches:
            print("Warning: Number of branches must match number of repos. Using default branches.")
            
        config["days"] = args.days or 1
        
        # Force local mode if specified
        if args.local:
            config["ai_provider"] = "local"
    
    # Validate essential configuration
    if not config.get("github_token"):
        sys.exit("GitHub token is required. Set GITHUB_TOKEN environment variable, use --github-token, or run with --interactive")
    
    if not config.get("repos"):
        sys.exit("At least one repository is required. Use --repos owner/repo1 owner/repo2 or run with --interactive")
    
    # Calculate the date to fetch commits since
    today = datetime.datetime.now()
    since_date = today - datetime.timedelta(days=config["days"])
    
    # Fetch commits from GitHub
    print(f"Fetching commits since {since_date.strftime('%Y-%m-%d')}")
    commits = get_commits_since_date(
        config["github_token"], 
        config["repos"], 
        since_date, 
        config.get("username"), 
        config.get("branches", {})
    )
    
    if not commits:
        print("No commits found for the specified time period.")
        return
    
    print(f"Found a total of {len(commits)} commits")
    
    # Generate standup speech using selected AI provider
    ai_provider = get_ai_provider(config)
    standup_speech = ai_provider.generate_standup_speech(commits)
    
    # Format the output
    formatted_output = format_output(standup_speech, commits, config["output"])
    
    # Save or print result
    if config.get("save"):
        filename = f"standup_{today.strftime('%Y%m%d')}.{config['output']}"
        with open(filename, "w") as f:
            f.write(formatted_output)
        print(f"Standup saved to {filename}")
    
    print("\n--- GENERATED STANDUP ---\n")
    print(formatted_output)
    print("\n------------------------\n")

if __name__ == "__main__":
    main()