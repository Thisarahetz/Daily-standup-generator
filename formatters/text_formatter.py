"""
Text formatter for standup generator output.
"""

def format_as_text(standup_speech, commits):
    """
    Format the standup speech and commits as text.
    
    Args:
        standup_speech (str): The generated standup speech
        commits (list): List of commit data
    
    Returns:
        str: Text formatted output
    """
    result = standup_speech
    
    # Add a separator
    result += "\n\n" + "-" * 40 + "\n"
    result += "COMMIT DETAILS:\n" + "-" * 40 + "\n\n"
    
    # Group commits by repository
    repo_commits = {}
    for commit in commits:
        repo = commit["repo"]
        if repo not in repo_commits:
            repo_commits[repo] = []
        repo_commits[repo].append(commit)
    
    # Format commits by repository
    for repo, repo_commits_list in repo_commits.items():
        result += f"Repository: {repo}\n"
        if any("branch" in commit for commit in repo_commits_list):
            for commit in repo_commits_list:
                branch = commit.get("branch", "default")
                result += f"  [{branch}] {commit['message']} (sha: {commit['sha']})\n"
        else:
            for commit in repo_commits_list:
                result += f"  {commit['message']} (sha: {commit['sha']})\n"
        result += "\n"
    
    return result