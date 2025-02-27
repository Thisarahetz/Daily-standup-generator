"""
AI providers module for standup generator.
Provides a factory for different AI text generation providers.
"""

# Check for available providers
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Import provider implementations
from .local_provider import LocalProvider

# Conditionally import providers if available
if ANTHROPIC_AVAILABLE:
    from .anthropic_provider import AnthropicProvider
if OPENAI_AVAILABLE:
    from .openai_provider import OpenAIProvider
if GEMINI_AVAILABLE:
    from .gemini_provider import GeminiProvider

def get_ai_provider(config):
    """
    Factory function to get the appropriate AI provider based on configuration.
    
    Args:
        config (dict): Application configuration
    
    Returns:
        object: An AI provider instance
    """
    provider_name = config.get("ai_provider", "local")
    api_keys = {
        "anthropic": config.get("anthropic_api_key", ""),
        "openai": config.get("openai_api_key", ""),
        "gemini": config.get("gemini_api_key", "")
    }
    
    # Try to use the requested provider
    if provider_name == "anthropic" and ANTHROPIC_AVAILABLE and api_keys["anthropic"]:
        print("Using Anthropic Claude for standup generation...")
        return AnthropicProvider(api_keys["anthropic"])
    elif provider_name == "openai" and OPENAI_AVAILABLE and api_keys["openai"]:
        print("Using OpenAI for standup generation...")
        return OpenAIProvider(api_keys["openai"])
    elif provider_name == "gemini" and GEMINI_AVAILABLE and api_keys["gemini"]:
        print("Using Google Gemini for standup generation...")
        return GeminiProvider(api_keys["gemini"])
    
    # Fallback to any available provider
    if GEMINI_AVAILABLE and api_keys["gemini"]:
        print("Falling back to Google Gemini for standup generation...")
        return GeminiProvider(api_keys["gemini"])
    elif OPENAI_AVAILABLE and api_keys["openai"]:
        print("Falling back to OpenAI for standup generation...")
        return OpenAIProvider(api_keys["openai"])
    elif ANTHROPIC_AVAILABLE and api_keys["anthropic"]:
        print("Falling back to Anthropic Claude for standup generation...")
        return AnthropicProvider(api_keys["anthropic"])
    
    # If no API providers are available, use local template
    print("Using local template for standup generation (no AI APIs available)...")
    return LocalProvider()