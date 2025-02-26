#!/usr/bin/env python3
"""
Daily Standup Generator using GitHub commits and Anthropic API
-----------------------------------------
This script fetches your GitHub commits from the previous day and generates
a concise standup speech using Anthropic's Claude API.
"""

import os
import sys
import json
import datetime
import argparse
import requests
import getpass
from pathlib import Path
from github import Github

# Import different AI providers
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


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
    """Load configuration from file."""
    if not CONFIG_FILE.exists():
        return {}
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {str(e)}")
        return {}


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


def get_user_input():
    """Get repository and other info interactively from the user."""
    print("\n--- GitHub Standup Speech Generator ---\n")
    
    # Load saved config
    config = load_config()
    first_run = not config
    
    # If reset config flag was set, clear the config
    args = parse_arguments()
    if args.reset_config:
        config = {}
        first_run = True
        print("Configuration reset. You'll need to enter your credentials again.")
    
    # Get or use saved GitHub token
    github_token = os.environ.get("GITHUB_TOKEN") or config.get("github_token", "")
    if not github_token:
        print("Your GitHub token will be saved locally for future use.")
        print("Note: The token will be visible while typing/pasting")
        github_token = input("Enter your GitHub Personal Access Token: ").strip()
    
    # Get AI provider preference
    saved_provider = config.get("ai_provider", "gemini")
    ai_provider_choices = ["gemini", "openai", "anthropic", "local"]
    
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
    anthropic_api_key = ""
    openai_api_key = ""
    gemini_api_key = ""
    
    if ai_provider == "anthropic":
        anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY") or config.get("anthropic_api_key", "")
        if not anthropic_api_key:
            print("Your Anthropic API key will be saved locally for future use.")
            print("Note: The API key will be visible while typing/pasting")
            anthropic_api_key = input("Enter your Anthropic API Key: ").strip()
    elif ai_provider == "openai":
        openai_api_key = os.environ.get("OPENAI_API_KEY") or config.get("openai_api_key", "")
        if not openai_api_key:
            print("Your OpenAI API key will be saved locally for future use.")
            print("Note: The API key will be visible while typing/pasting")
            openai_api_key = input("Enter your OpenAI API Key: ").strip()
    elif ai_provider == "gemini":
        gemini_api_key = os.environ.get("GEMINI_API_KEY") or config.get("gemini_api_key", "")
        if not gemini_api_key:
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
        return get_user_input()
    
    # Get days
    days_input = input("\nNumber of days to look back for commits [1]: ").strip()
    days = int(days_input) if days_input else 1
    
    # Get output format - use saved or default
    saved_output = config.get("output", "text")
    output_format = saved_output
    
    if first_run:
        output_input = input(f"\nOutput format (text/json) [text]: ").strip().lower()
        if output_input in ["text", "json"]:
            output_format = output_input
    
    # Ask about saving - use saved or default
    saved_save = config.get("save", False)
    save = saved_save
    
    if first_run:
        save_input = input("\nSave output to file? (y/n) [n]: ").strip().lower()
        save = save_input.startswith("y")
    
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
        "save": save
    }
    save_config(new_config)
    
    return {
        "github_token": github_token,
        "anthropic_api_key": anthropic_api_key,
        "openai_api_key": openai_api_key,
        "gemini_api_key": gemini_api_key,
        "ai_provider": ai_provider,
        "repos": repos,
        "username": username,
        "days": days,
        "output": output_format,
        "save": save,
        "branches": branches
    }


def get_commits_since_date(github_client, repos, since_date, username=None, branches=None):
    """
    Fetch commits from specified repos since the given date.
    Optionally filter by username and branch.
    """
    if branches is None:
        branches = {}
    
    all_commits = []
    
    for repo_name in repos:
        try:
            print(f"Fetching commits from {repo_name}...")
            repo = github_client.get_repo(repo_name)
            
            # Get branch if specified
            branch = branches.get(repo_name, "default")
            branch_param = None if branch == "default" else branch
            
            # Show which branch we're using
            if branch_param:
                print(f"  Using branch: {branch_param}")
            else:
                print(f"  Using default branch: {repo.default_branch}")
            
            # Get commits with optional branch parameter
            commits = repo.get_commits(since=since_date, sha=branch_param)
            
            repo_commits = 0
            for commit in commits:
                # Skip merge commits
                if len(commit.parents) > 1:
                    continue
                
                # Filter by username if specified
                if username and commit.author and commit.author.login != username:
                    continue
                
                commit_data = {
                    "repo": repo_name,
                    "sha": commit.sha[:7],
                    "message": commit.commit.message,
                    "date": commit.commit.author.date.isoformat(),
                    "author": commit.author.login if commit.author else "Unknown",
                    "url": commit.html_url,
                    "branch": branch_param or repo.default_branch
                }
                all_commits.append(commit_data)
                repo_commits += 1
            
            print(f"Found {repo_commits} commits in {repo_name}")
                
        except Exception as e:
            print(f"Error fetching commits from {repo_name}: {str(e)}", file=sys.stderr)
    
    # Sort commits by date (newest first)
    all_commits.sort(key=lambda x: x["date"], reverse=True)
    return all_commits


def generate_standup_speech(api_keys, commits, provider="gemini"):
    """Generate a standup speech using an AI provider."""
    if not commits:
        return "No commits found for the specified time period."
    
    # Format commits for the prompt
    commits_text = ""
    for i, commit in enumerate(commits, 1):
        branch_info = f" [{commit.get('branch', 'default')}]" if 'branch' in commit else ""
        commits_text += f"{i}. [{commit['repo']}{branch_info}] {commit['message']} (sha: {commit['sha']})\n"
    
    prompt = f"""
I need to give a daily standup speech based on my GitHub commits. 
Here are the commits:

{commits_text}

Please generate a concise and professional standup speech that:
1. Summarizes what I accomplished based on these commits
2. Groups related work together
3. Explains the impact of the changes where possible
4. Mentions any challenges I faced if they're apparent from the commit messages
5. Includes what I plan to work on next (you can infer this from the commits)

Keep it under 2 minutes when spoken aloud.
"""
    
    # Try different providers in order of preference
    if provider == "gemini" and GEMINI_AVAILABLE and api_keys.get("gemini"):
        return generate_with_gemini(api_keys["gemini"], prompt)
    elif provider == "anthropic" and ANTHROPIC_AVAILABLE and api_keys.get("anthropic"):
        return generate_with_anthropic(api_keys["anthropic"], prompt)
    elif provider == "openai" and OPENAI_AVAILABLE and api_keys.get("openai"):
        return generate_with_openai(api_keys["openai"], prompt)
    else:
        # Fallback to whatever is available
        if GEMINI_AVAILABLE and api_keys.get("gemini"):
            return generate_with_gemini(api_keys["gemini"], prompt)
        elif OPENAI_AVAILABLE and api_keys.get("openai"):
            return generate_with_openai(api_keys["openai"], prompt)
        elif ANTHROPIC_AVAILABLE and api_keys.get("anthropic"):
            return generate_with_anthropic(api_keys["anthropic"], prompt)
        else:
            return generate_with_local_template(commits)

def generate_with_gemini(api_key, prompt):
    """Generate using Google's Gemini API."""
    try:
        print("Generating standup speech with Gemini...")
        genai.configure(api_key=api_key)
        
        # Configure the generative model
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1024,
        }
        
        model = genai.GenerativeModel(
            model_name="gemini-pro",
            generation_config=generation_config
        )
        
        system_instruction = "You are an assistant that helps developers create concise and informative standup speeches based on their GitHub commits."
        
        response = model.generate_content(
            [system_instruction, prompt]
        )
        
        if hasattr(response, 'text'):
            return response.text
        elif hasattr(response, 'parts'):
            return response.parts[0].text
        else:
            print("Unexpected response format from Gemini")
            return None
    except Exception as e:
        print(f"Error with Gemini API: {str(e)}")
        return None

def generate_with_anthropic(api_key, prompt):
    """Generate using Anthropic's Claude API."""
    try:
        print("Generating standup speech with Claude...")
        client = Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-3-sonnet-20240229",  # Using a more widely available model
            max_tokens=1000,
            temperature=0.7,
            system="You are an assistant that helps developers create concise and informative standup speeches based on their GitHub commits.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
    except Exception as e:
        print(f"Error with Anthropic API: {str(e)}")
        return None

def generate_with_openai(api_key, prompt):
    """Generate using OpenAI's API."""
    try:
        print("Generating standup speech with OpenAI...")
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Using a more affordable model
            messages=[
                {"role": "system", "content": "You are an assistant that helps developers create concise and informative standup speeches based on their GitHub commits."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error with OpenAI API: {str(e)}")
        return None

def generate_with_local_template(commits):
    """Generate a basic standup summary without using an external API."""
    print("Generating a basic standup summary locally (no AI API available)...")
    
    # Group commits by repository
    repos = {}
    for commit in commits:
        repo = commit['repo']
        if repo not in repos:
            repos[repo] = []
        repos[repo].append(commit)
    
    # Generate a basic summary
    summary = "# Daily Standup Summary\n\n"
    summary += f"## Work completed on {datetime.datetime.now().strftime('%Y-%m-%d')}\n\n"
    
    for repo, repo_commits in repos.items():
        summary += f"### Repository: {repo}\n"
        for commit in repo_commits:
            summary += f"- {commit['message']} ({commit['sha']})\n"
        summary += "\n"
    
    summary += "## Plan for today\n"
    summary += "- Continue work on the tasks above\n"
    summary += "- Address any feedback or issues that arise\n"
    
    return summary


def main():
    """Main function to run the script."""
    args = parse_arguments()
    
    # Use interactive mode if specified
    if args.interactive:
        user_input = get_user_input()
        github_token = user_input["github_token"]
        anthropic_api_key = user_input.get("anthropic_api_key", "")
        openai_api_key = user_input.get("openai_api_key", "")
        gemini_api_key = user_input.get("gemini_api_key", "")
        ai_provider = user_input.get("ai_provider", "gemini")
        repos = user_input["repos"]
        username = user_input["username"]
        days = user_input["days"]
        output_format = user_input["output"]
        save = user_input["save"]
        branches = user_input.get("branches", {})
    else:
        # Get credentials from arguments, environment variables, or saved config
        config = load_config()
        github_token = args.github_token or os.environ.get("GITHUB_TOKEN") or config.get("github_token", "")
        anthropic_api_key = args.anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY") or config.get("anthropic_api_key", "")
        openai_api_key = args.openai_api_key or os.environ.get("OPENAI_API_KEY") or config.get("openai_api_key", "")
        gemini_api_key = args.gemini_api_key or os.environ.get("GEMINI_API_KEY") or config.get("gemini_api_key", "")
        ai_provider = args.ai_provider or config.get("ai_provider", "gemini")
        repos = args.repos or config.get("repos", [])
        username = args.username or config.get("username", "")
        days = args.days
        output_format = args.output or config.get("output", "text")
        save = args.save or config.get("save", False)
        
        # Handle branches from command line args
        branches = config.get("branches", {})
        if args.branches and args.repos and len(args.branches) == len(args.repos):
            branches = {repo: branch for repo, branch in zip(args.repos, args.branches)}
        elif args.branches:
            print("Warning: Number of branches must match number of repos. Using default branches.")
        
        # Force local mode if specified
        if args.local:
            ai_provider = "local"
    
    if not github_token:
        sys.exit("GitHub token is required. Set GITHUB_TOKEN environment variable, use --github-token, or run with --interactive")
    
    if not repos:
        sys.exit("At least one repository is required. Use --repos owner/repo1 owner/repo2 or run with --interactive")
    
    # Verify API keys for selected provider
    if ai_provider == "anthropic" and not anthropic_api_key and not args.local:
        print("Warning: Anthropic API key not provided. Falling back to local template.")
        ai_provider = "local"
    elif ai_provider == "openai" and not openai_api_key and not args.local:
        print("Warning: OpenAI API key not provided. Falling back to local template.")
        ai_provider = "local"
    elif ai_provider == "gemini" and not gemini_api_key and not args.local:
        print("Warning: Gemini API key not provided. Falling back to local template.")
        ai_provider = "local"
    
    # Calculate the date to fetch commits since
    today = datetime.datetime.now()
    since_date = today - datetime.timedelta(days=days)
    
    # Connect to GitHub API
    print(f"Connecting to GitHub API...")
    github_client = Github(github_token)
    
    # Fetch commits
    print(f"Fetching commits since {since_date.strftime('%Y-%m-%d')}")
    commits = get_commits_since_date(github_client, repos, since_date, username, branches)
    
    if not commits:
        print("No commits found for the specified time period.")
        return
    
    print(f"Found a total of {len(commits)} commits")
    
    # Prepare API keys
    api_keys = {
        "anthropic": anthropic_api_key,
        "openai": openai_api_key,
        "gemini": gemini_api_key
    }
    
    # Generate standup speech
    standup_speech = generate_standup_speech(api_keys, commits, ai_provider)
    
    # Fallback to local if AI generation fails
    if not standup_speech:
        print("AI-based generation failed. Falling back to local template.")
        standup_speech = generate_with_local_template(commits)
    
    # Output results
    if output_format == "json":
        output = {
            "speech": standup_speech,
            "commits": commits,
            "generated_at": datetime.datetime.now().isoformat(),
            "params": {
                "repos": repos,
                "days": days,
                "username": username
            }
        }
        result = json.dumps(output, indent=2)
    else:
        result = standup_speech
    
    # Save or print result
    if save:
        filename = f"standup_{today.strftime('%Y%m%d')}.{output_format}"
        with open(filename, "w") as f:
            f.write(result)
        print(f"Standup saved to {filename}")
    
    print("\n--- GENERATED STANDUP ---\n")
    print(result)
    print("\n------------------------\n")


if __name__ == "__main__":
    main()