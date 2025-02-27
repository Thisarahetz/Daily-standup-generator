"""
Configuration management for GitHub Standup Generator.
Handles loading/saving configuration and interactive user input.
"""

import os
import json
from pathlib import Path

CONFIG_FILE = Path.home() / '.github_standup_config.json'

def save_config(config):
    """Save configuration to file."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        os.chmod(CONFIG_FILE, 0o600)  # Set permissions to user read/write only
        return True
    except Exception as e:
        print(f"Error saving config: {str(e)}")
        return False

def load_config():
    """Load configuration from file or environment variables."""
    config = {}
    
    # Try to load from file
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
        except Exception as e:
            print(f"Error loading config file: {str(e)}")
    
    # Check environment variables to override or set values
    env_vars = {
        "GITHUB_TOKEN": "github_token",
        "ANTHROPIC_API_KEY": "anthropic_api_key",
        "OPENAI_API_KEY": "openai_api_key",
        "GEMINI_API_KEY": "gemini_api_key"
    }
    
    for env_var, config_key in env_vars.items():
        if os.environ.get(env_var):
            config[config_key] = os.environ.get(env_var)
    
    return config

def get_user_input(reset_config=False):
    """Get repository and other info interactively from the user."""
    print("\n--- GitHub Standup Speech Generator ---\n")
    
    # Load saved config
    config = load_config()
    first_run = not config
    
    # If reset config flag was set, clear the config
    if reset_config:
        config = {}
        first_run = True
        print("Configuration reset. You'll need to enter your credentials again.")
    
    # Get or use saved GitHub token
    github_token = config.get("github_token", "")
    if not github_token:
        print("Your GitHub token will be saved locally for future use.")
        print("Note: The token will be visible while typing/pasting")
        github_token = input("Enter your GitHub Personal Access Token: ").strip()
    
    # Get AI provider preference
    saved_provider = config.get("ai_provider", "gemini")
    
    if first_run:
        print("\nSelect AI provider for generating standup speech:")
        print("1. Gemini (Google's AI - free tier available)")
        print("2. OpenAI (GPT models - free tier available for new accounts)")
        print("3. Anthropic (Claude models - requires paid API access)")
        print("4. Local (Basic template, no AI - completely free)")
        provider_choice = input(f"Choose provider [1-4, default: 1]: ").strip()
        
        if provider_choice == "2":
            ai_provider = "openai"
        elif provider_choice == "3":
            ai_provider = "anthropic"
        elif provider_choice == "4":
            ai_provider = "local"
        else:
            ai_provider = "gemini"
    else:
        ai_provider = saved_provider
        print(f"\nUsing saved AI provider: {ai_provider}")
        change_provider = input("Would you like to change the AI provider? (y/n) [n]: ").strip().lower()
        if change_provider.startswith("y"):
            print("\nSelect AI provider for generating standup speech:")
            print("1. Gemini (Google's AI - free tier available)")
            print("2. OpenAI (GPT models - free tier available for new accounts)")
            print("3. Anthropic (Claude models - requires paid API access)")
            print("4. Local (Basic template, no AI - completely free)")
            provider_choice = input(f"Choose provider [1-4, default: 1]: ").strip()
            
            if provider_choice == "2":
                ai_provider = "openai"
            elif provider_choice == "3":
                ai_provider = "anthropic"
            elif provider_choice == "4":
                ai_provider = "local"
            else:
                ai_provider = "gemini"
    
    # Get API keys based on selected provider
    anthropic_api_key = config.get("anthropic_api_key", "")
    openai_api_key = config.get("openai_api_key", "")
    gemini_api_key = config.get("gemini_api_key", "")
    
    if ai_provider == "anthropic" and not anthropic_api_key:
        print("Your Anthropic API key will be saved locally for future use.")
        print("Note: The API key will be visible while typing/pasting")
        anthropic_api_key = input("Enter your Anthropic API Key: ").strip()
    elif ai_provider == "openai" and not openai_api_key:
        print("Your OpenAI API key will be saved locally for future use.")
        print("Note: The API key will be visible while typing/pasting")
        openai_api_key = input("Enter your OpenAI API Key: ").strip()
    elif ai_provider == "gemini" and not gemini_api_key:
        print("Your Google Gemini API key will be saved locally for future use.")
        print("Note: The API key will be visible while typing/pasting")
        gemini_api_key = input("Enter your Google Gemini API Key: ").strip()
        print("You can get a free API key from https://aistudio.google.com/app/apikey")
    
    # Get or use saved username
    saved_username = config.get("username", "")
    username = ""
    if first_run or not saved_username:
        username = input("\nEnter your GitHub username to filter commits (optional): ").strip()
    else:
        use_saved = input(f"\nUse saved username '{saved_username}'? (y/n) [y]: ").strip().lower()
        if not use_saved or use_saved.startswith("y"):
            username = saved_username
        else:
            username = input("Enter your GitHub username: ").strip()
    
    # Get repositories - always ask for this
    saved_repos = config.get("repos", [])
    saved_branches = config.get("branches", {})
    repos = []
    branches = {}
    
    if saved_repos:
        print("\nPreviously used repositories:")
        for i, repo in enumerate(saved_repos, 1):
            branch = saved_branches.get(repo, "default")
            branch_display = f" (branch: {branch})" if branch != "default" else ""
            print(f"{i}. {repo}{branch_display}")
        
        use_saved = input("\nUse these repositories? (y/n/select) [y]: ").strip().lower()
        
        if not use_saved or use_saved.startswith("y"):
            repos = saved_repos
            branches = saved_branches
        elif use_saved == "select":
            indices = input("Enter the numbers of repos to use (comma-separated): ").strip()
            try:
                selected_indices = [int(i.strip()) - 1 for i in indices.split(",")]
                repos = [saved_repos[i] for i in selected_indices if 0 <= i < len(saved_repos)]
                branches = {repo: saved_branches.get(repo, "default") for repo in repos}
            except:
                print("Invalid selection. Please enter repository information manually.")
                repos = []
                branches = {}
    
    if not repos:
        print("\nEnter the repositories to fetch commits from (format: owner/repo)")
        print("Enter a blank line when done")
        
        while True:
            repo = input("Repository (owner/repo): ").strip()
            if not repo:
                break
            if "/" not in repo:
                print("Invalid format. Please use format 'owner/repo'")
                continue
            
            branch = input(f"Branch for {repo} (leave empty for default branch): ").strip()
            repos.append(repo)
            branches[repo] = branch if branch else "default"
    
    if not repos:
        print("You must enter at least one repository.")
        return get_user_input(reset_config)
    
    # Get days
    days_input = input("\nNumber of days to look back for commits [1]: ").strip()
    days = int(days_input) if days_input else 1
    
    # Get output format
    saved_output = config.get("output", "text")
    if first_run:
        output_input = input(f"\nOutput format (text/json) [text]: ").strip().lower()
        output_format = output_input if output_input in ["text", "json"] else "text"
    else:
        output_format = saved_output
    
    # Ask about saving
    saved_save = config.get("save", False)
    if first_run:
        save_input = input("\nSave output to file? (y/n) [n]: ").strip().lower()
        save = save_input.startswith("y")
    else:
        save = saved_save
    
    # Save configuration for future use
    new_config = {
        "github_token": github_token,
        "anthropic_api_key": anthropic_api_key,
        "openai_api_key": openai_api_key,
        "gemini_api_key": gemini_api_key,
        "ai_provider": ai_provider,
        "username": username,
        "repos": repos,
        "branches": branches,
        "output": output_format,
        "save": save,
        "days": days
    }
    save_config(new_config)
    
    return new_config