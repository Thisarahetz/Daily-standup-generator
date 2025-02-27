"""
Local template provider for standup generator.
Used when no AI APIs are available or requested.
"""

import datetime

class LocalProvider:
    """Local template provider for standup generation without AI APIs."""
    
    def __init__(self):
        """Initialize the local provider."""
        pass
    
    def generate_standup_speech(self, commits):
        """
        Generate a basic standup summary without using an external API.
        
        Args:
            commits (list): List of commit data
        
        Returns:
            str: Generated standup speech
        """
        if not commits:
            return "No commits found for the specified time period."
        
        print("Generating a basic standup summary locally (no AI API used)...")
        
        # Group commits by repository
        repos = {}
        for commit in commits:
            repo = commit['repo']
            if repo not in repos:
                repos[repo] = []
            repos[repo].append(commit)
        
        # Get date range covered by commits
        if commits:
            dates = [datetime.datetime.fromisoformat(commit["date"]) for commit in commits]
            min_date = min(dates)
            max_date = max(dates)
            date_range = f"from {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"
        else:
            date_range = "for the requested period"
        
        # Generate a basic summary
        summary = f"# Daily Standup Summary {date_range}\n\n"
        
        # Overall stats
        summary += "## Work Summary\n\n"
        summary += f"- Made {len(commits)} commits across {len(repos)} repositories\n"
        
        # Repository details
        summary += "\n## Work by Repository\n\n"
        
        for repo, repo_commits in repos.items():
            summary += f"### {repo}\n"
            summary += f"- Made {len(repo_commits)} commits\n"
            
            # Group similar commits by looking at first word
            commit_groups = {}
            for commit in repo_commits:
                # Use first word as key (often "Fix", "Add", "Update", etc.)
                message = commit['message'].strip()
                first_word = message.split(' ')[0].lower()
                if first_word not in commit_groups:
                    commit_groups[first_word] = []
                commit_groups[first_word].append(message)
            
            # Add grouped summary
            for group, messages in commit_groups.items():
                if len(messages) > 1:
                    summary += f"- Made {len(messages)} commits to {group.capitalize()} changes\n"
                else:
                    summary += f"- {messages[0]}\n"
            
            summary += "\n"
        
        # Plan for today
        summary += "## Plan for Today\n\n"
        summary += "- Continue work on active repositories\n"
        summary += "- Address any feedback or issues that arise\n"
        
        return summary