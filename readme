# GitHub Standup Generator

A tool that automatically generates concise standup speeches based on your recent GitHub commits using AI. Perfect for daily standups, weekly reports, or keeping track of your work progress.

## Features

- 🔄 Fetches your recent commits from GitHub repositories
- 🤖 Uses AI to generate human-like standup summaries (supports Gemini, OpenAI, or Anthropic Claude)
- 📝 Organizes work by repository and related tasks
- 🔍 Filters commits by username and timeframe
- 💾 Saves output as text or JSON
- 🔐 Securely stores your API keys locally

## Installation

1. Clone this repository:

   ```
   git clone https://github.com/Thisarahetz/Daily-standup-generator.git
   cd github-standup-generator
   ```

2. Install requirements:
   ```
   pip install -r requirements.txt
   ```

## Getting API Keys

### GitHub Personal Access Token

1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Name your token (e.g., "daily_standup_generator-key")
4. Set an expiration period (e.g., 60 days)
5. Under "Select scopes", check "repo" for full control of private repositories
   - This includes access to commits, status, and deployments
   - You can select more specific scopes if needed (repo:status, repo:deployment, etc.)
6. Click "Generate token" and copy your token immediately (it won't be shown again)

### Google Gemini API Key (Recommended - Free Tier Available)

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key
5. You get free credits each month for API usage

### OpenAI API Key

1. Create an account at [OpenAI](https://platform.openai.com/)
2. Go to [API Keys](https://platform.openai.com/api-keys)
3. Click "Create new secret key"
4. Give it a name and copy your API key
5. New accounts get free credits, after which you'll need to add payment

### Anthropic Claude API Key

1. Create an account at [Anthropic Console](https://console.anthropic.com/)
2. Go to API Keys section
3. Click "Create API Key"
4. Enter a name and copy your API key
5. Note: Claude requires a paid account

## Usage

### Interactive Mode (Recommended for First Time)

```
python main.py --interactive
```

This walks you through setting up your GitHub token, AI provider, and repositories.

### Command Line Options

```
python main.py --ai-provider gemini --repos owner/repo1 owner/repo2 --days 3 --username your-github-username
```

### Full Options List

```
python main.py --help
```

### Reset Configuration

If you need to reset your saved configuration:

```
python main.py --interactive --reset-config
```

## Output Examples

```
# Daily Standup Summary

## Yesterday's Accomplishments

I focused on enhancing our user authentication system and fixing critical bugs:

- Implemented logout functionality and user account deletion features
- Updated TypeScript to the latest version for improved type safety
- Fixed navigation issues on the profile page
- Resolved API response handling for better error states

## Today's Plan

- Complete the remaining user profile management features
- Work on integration tests for the new authentication flows
- Start planning the upcoming feature for saved preferences

----------------------------------------
COMMIT DETAILS:
----------------------------------------
Repository: company/project
  [development] Update: TypeScript version and implement logout and delete app functionalities (sha: 5b7b921)
  [development] Fix: Profile navigation and API response handling (sha: a93f720)
```

## Configuration

The tool saves your configuration in `~/.github_standup_config.json` for convenience.

## Using without AI (Local Template)

If you don't want to use an AI API, you can use the local template mode:

```
python main.py --local
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
