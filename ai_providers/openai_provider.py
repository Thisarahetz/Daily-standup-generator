"""
OpenAI provider for standup generator.
"""

import openai

class OpenAIProvider:
    """OpenAI provider for standup generation."""
    
    def __init__(self, api_key):
        """
        Initialize the OpenAI provider.
        
        Args:
            api_key (str): OpenAI API key
        """
        self.api_key = api_key
        openai.api_key = api_key
    
    def generate_standup_speech(self, commits):
        """
        Generate a standup speech using OpenAI's API.
        
        Args:
            commits (list): List of commit data
        
        Returns:
            str: Generated standup speech
        """
        if not commits:
            return "No commits found for the specified time period."
        
        # Format commits for the prompt
        commits_text = self._format_commits_for_prompt(commits)
        
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
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
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
            return self._generate_fallback_speech(commits)
    
    def _format_commits_for_prompt(self, commits):
        """
        Format commits for inclusion in the prompt.
        
        Args:
            commits (list): List of commit data
            
        Returns:
            str: Formatted commits text
        """
        commits_text = ""
        for i, commit in enumerate(commits, 1):
            branch_info = f" [{commit.get('branch', 'default')}]" if 'branch' in commit else ""
            commits_text += f"{i}. [{commit['repo']}{branch_info}] {commit['message']} (sha: {commit['sha']})\n"
        return commits_text
    
    def _generate_fallback_speech(self, commits):
        """
        Generate a basic fallback speech if the API fails.
        
        Args:
            commits (list): List of commit data
            
        Returns:
            str: Basic fallback speech
        """
        # Count commits per repository
        repos = {}
        for commit in commits:
            repo = commit['repo']
            if repo not in repos:
                repos[repo] = 0
            repos[repo] += 1
        
        # Generate a simple summary
        summary = "# Daily Standup Summary\n\n"
        summary += "## Work completed:\n\n"
        
        for repo, count in repos.items():
            summary += f"- Made {count} commits to {repo}\n"
        
        summary += "\n## Details:\n"
        summary += f"- Worked across {len(repos)} repositories\n"
        summary += f"- Total of {len(commits)} commits\n"
        
        summary += "\n## Plan for today:\n"
        summary += "- Continue working on the ongoing tasks\n"
        
        return summary