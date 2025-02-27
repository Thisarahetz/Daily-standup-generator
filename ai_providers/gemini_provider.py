"""
Google Gemini AI provider for standup generator.
"""

import requests
import google.generativeai as genai

class GeminiProvider:
    """Google Gemini AI provider for standup generation."""
    
    def __init__(self, api_key):
        """
        Initialize the Gemini provider.
        
        Args:
            api_key (str): Google Gemini API key
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)
    
    def generate_standup_speech(self, commits):
        """
        Generate a standup speech using Google's Gemini API.
        
        Args:
            commits (list): List of commit data
        
        Returns:
            str: Generated standup speech
        """
        if not commits:
            return "No commits found for the specified time period."
        
        # Format commits for the prompt
        commits_text = self._format_commits_for_prompt(commits)
        
        # Format the system instruction and prompt
        system_instruction = "You are an assistant that helps developers create concise and informative standup speeches based on their GitHub commits."
        
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
        
        full_prompt = f"{system_instruction}\n\n{prompt}"
        
        try:
            # Try using the REST API first (with updated model name)
            return self._generate_with_rest_api(system_instruction, prompt)
        except Exception as e:
            print(f"Error with Gemini REST API: {str(e)}")
            try:
                # Fall back to Python SDK
                return self._generate_with_sdk(full_prompt)
            except Exception as e2:
                print(f"Error with Gemini SDK: {str(e2)}")
                return self._generate_fallback_speech(commits)
    
    def _generate_with_sdk(self, full_prompt):
        """
        Generate using the Gemini Python SDK.
        
        Args:
            full_prompt (str): Complete prompt with system instruction
            
        Returns:
            str: Generated text
        """
        try:
            # Try with gemini-1.5-flash first
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            print(f"Error with gemini-1.5-flash model: {str(e)}")
            try:
                # Fall back to gemini-1.0-pro
                model = genai.GenerativeModel('gemini-1.0-pro')
                response = model.generate_content(full_prompt)
                return response.text
            except Exception as e:
                print(f"Error with gemini-1.0-pro model: {str(e)}")
                raise
    
    def _generate_with_rest_api(self, system_instruction, prompt):
        """
        Generate using direct REST API calls to Gemini with updated model name.
        
        Args:
            system_instruction (str): System instruction
            prompt (str): User prompt
            
        Returns:
            str: Generated text
        """
        # Try with gemini-2.0-flash first (as shown in your working example)
        model_name = "gemini-2.0-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"{system_instruction}\n\n{prompt}"
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1024,
                "topP": 0.95,
                "topK": 40
            }
        }
        
        # Make the HTTP request
        response = requests.post(url, headers=headers, json=data)
        
        # Check if the request was successful
        if response.status_code == 200:
            response_json = response.json()
            
            # Extract the text from the response
            try:
                text = response_json.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                if text:
                    return text
                else:
                    raise ValueError(f"No text found in the response: {response_json}")
            except (IndexError, KeyError) as e:
                raise ValueError(f"Error parsing response: {e}, Response JSON: {response_json}")
        # If gemini-2.0-flash fails, try alternative models
        elif response.status_code == 404:
            # Try with gemini-1.5-flash instead
            alt_model_name = "gemini-1.5-flash"
            alt_url = f"https://generativelanguage.googleapis.com/v1beta/models/{alt_model_name}:generateContent?key={self.api_key}"
            alt_response = requests.post(alt_url, headers=headers, json=data)
            
            if alt_response.status_code == 200:
                alt_response_json = alt_response.json()
                try:
                    text = alt_response_json.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    if text:
                        return text
                except (IndexError, KeyError):
                    pass
        
        # If all attempts fail, raise an error
        raise ValueError(f"Request failed with status code {response.status_code}, Response: {response.text}")
    
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