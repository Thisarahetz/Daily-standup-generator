"""
GitHub API client module for standup generator.
Handles fetching commits from GitHub repositories.
"""

import sys
from github import Github

def get_commits_since_date(github_token, repos, since_date, username=None, branches=None):
    """
    Fetch commits from specified repos since the given date.
    Optionally filter by username and branch.
    
    Args:
        github_token (str): GitHub personal access token
        repos (list): List of repository names in 'owner/repo' format
        since_date (datetime): Date to fetch commits from
        username (str, optional): GitHub username to filter by
        branches (dict, optional): Dict mapping repo names to branch names
    
    Returns:
        list: List of commit dictionaries with metadata
    """
    if branches is None:
        branches = {}
    
    # Connect to GitHub API
    print(f"Connecting to GitHub API...")
    github_client = Github(github_token)
    
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