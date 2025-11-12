"""
AI-powered reply generation for Twitter mentions.

Supports multiple AI providers:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Local models (Ollama)
- Groq (fast inference)

Setup:
1. Choose your provider and set the corresponding environment variable:
   - OpenAI: export OPENAI_API_KEY="your-key"
   - Anthropic: export ANTHROPIC_API_KEY="your-key"
   - Groq: export GROQ_API_KEY="your-key"
   - Ollama: Run locally (no API key needed)

2. Configure your provider in the GUI or by setting AI_PROVIDER env var
"""

from __future__ import annotations

import os
from typing import Optional
from enum import Enum


class AIProvider(Enum):
    """Supported AI providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    GROQ = "groq"
    NONE = "none"  # Fallback to template-based replies


class AIReplyGenerator:
    """Generate contextual AI replies to Twitter mentions."""

    def __init__(
        self,
        provider: AIProvider = AIProvider.NONE,
        model: Optional[str] = None,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
    ):
        """
        Initialize AI reply generator.

        Args:
            provider: AI provider to use
            model: Model name (provider-specific)
            temperature: Response randomness (0.0-1.0)
            system_prompt: Custom instructions for the AI
        """
        self.provider = provider
        self.temperature = temperature

        # Default models per provider
        if model is None:
            model = self._get_default_model(provider)
        self.model = model

        # Default system prompt
        if system_prompt is None:
            system_prompt = self._get_default_system_prompt()
        self.system_prompt = system_prompt

        # Initialize client based on provider
        self.client = None
        if provider != AIProvider.NONE:
            self._initialize_client()

    def _get_default_model(self, provider: AIProvider) -> str:
        """Get default model for each provider."""
        defaults = {
            AIProvider.OPENAI: "gpt-4-turbo-preview",
            AIProvider.ANTHROPIC: "claude-3-5-sonnet-20241022",
            AIProvider.OLLAMA: "llama3.2",
            AIProvider.GROQ: "llama-3.3-70b-versatile",
            AIProvider.NONE: "",
        }
        return defaults.get(provider, "")

    def _get_default_system_prompt(self) -> str:
        """Default instructions for the AI."""
        return """You are a friendly, professional Twitter account manager.
Your job is to reply to mentions in a helpful, engaging way.

Guidelines:
- Keep replies under 280 characters
- Be concise and natural
- Match the tone of the mention (friendly, professional, etc.)
- If it's a question, try to answer helpfully
- If it's positive feedback, thank them warmly
- If it's a complaint, be empathetic and helpful
- Avoid controversial topics
- Don't include hashtags unless the original mention had them
- Be authentic and human-like

Respond ONLY with the tweet reply text, nothing else."""

    def _initialize_client(self):
        """Initialize the appropriate AI client."""
        try:
            if self.provider == AIProvider.OPENAI:
                import openai
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY environment variable not set")
                self.client = openai.OpenAI(api_key=api_key)

            elif self.provider == AIProvider.ANTHROPIC:
                import anthropic
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    raise ValueError("ANTHROPIC_API_KEY environment variable not set")
                self.client = anthropic.Anthropic(api_key=api_key)

            elif self.provider == AIProvider.OLLAMA:
                import ollama
                # Ollama runs locally, no API key needed
                self.client = ollama.Client()

            elif self.provider == AIProvider.GROQ:
                import groq
                api_key = os.getenv("GROQ_API_KEY")
                if not api_key:
                    raise ValueError("GROQ_API_KEY environment variable not set")
                self.client = groq.Groq(api_key=api_key)

        except ImportError as e:
            raise ImportError(
                f"Required package for {self.provider.value} not installed. "
                f"Install with: pip install {self._get_package_name()}"
            ) from e

    def _get_package_name(self) -> str:
        """Get pip package name for current provider."""
        packages = {
            AIProvider.OPENAI: "openai",
            AIProvider.ANTHROPIC: "anthropic",
            AIProvider.OLLAMA: "ollama",
            AIProvider.GROQ: "groq",
        }
        return packages.get(self.provider, "")

    def generate_reply(
        self,
        mention_text: str,
        mention_author: str,
        context: Optional[str] = None,
    ) -> str:
        """
        Generate an AI reply to a mention.

        Args:
            mention_text: The text of the mention/tweet
            mention_author: Username of the person who mentioned you
            context: Optional additional context about your account/brand

        Returns:
            Generated reply text (without the @mention prefix)
        """
        if self.provider == AIProvider.NONE:
            return self._generate_template_reply(mention_text, mention_author)

        try:
            # Build the prompt
            user_prompt = self._build_user_prompt(mention_text, mention_author, context)

            # Generate based on provider
            if self.provider == AIProvider.OPENAI:
                return self._generate_openai(user_prompt)
            elif self.provider == AIProvider.ANTHROPIC:
                return self._generate_anthropic(user_prompt)
            elif self.provider == AIProvider.OLLAMA:
                return self._generate_ollama(user_prompt)
            elif self.provider == AIProvider.GROQ:
                return self._generate_groq(user_prompt)

        except Exception as e:
            print(f"AI generation failed: {e}. Falling back to template.")
            return self._generate_template_reply(mention_text, mention_author)

    def _build_user_prompt(
        self,
        mention_text: str,
        mention_author: str,
        context: Optional[str],
    ) -> str:
        """Build the user prompt for AI."""
        prompt = f"Someone (@{mention_author}) mentioned you on Twitter:\n\n"
        prompt += f'"{mention_text}"\n\n'

        if context:
            prompt += f"Context about your account: {context}\n\n"

        prompt += "Generate a reply (without the @username prefix - that will be added automatically)."
        return prompt

    def _generate_openai(self, user_prompt: str) -> str:
        """Generate reply using OpenAI."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self.temperature,
            max_tokens=100,
        )
        return response.choices[0].message.content.strip()

    def _generate_anthropic(self, user_prompt: str) -> str:
        """Generate reply using Anthropic Claude."""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=100,
            temperature=self.temperature,
            system=self.system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ],
        )
        return message.content[0].text.strip()

    def _generate_ollama(self, user_prompt: str) -> str:
        """Generate reply using local Ollama."""
        response = self.client.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            options={
                "temperature": self.temperature,
            }
        )
        return response['message']['content'].strip()

    def _generate_groq(self, user_prompt: str) -> str:
        """Generate reply using Groq."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self.temperature,
            max_tokens=100,
        )
        return response.choices[0].message.content.strip()

    def _generate_template_reply(self, mention_text: str, mention_author: str) -> str:
        """Fallback template-based reply."""
        mention_lower = mention_text.lower()

        # Simple keyword-based responses
        if any(word in mention_lower for word in ["thanks", "thank you", "appreciate"]):
            return "You're very welcome! Glad I could help! 😊"
        elif any(word in mention_lower for word in ["help", "how", "?"]):
            return "Happy to help! Feel free to DM me if you need more details."
        elif any(word in mention_lower for word in ["great", "awesome", "love", "amazing"]):
            return "Thank you so much! Really appreciate the kind words! 🙌"
        elif any(word in mention_lower for word in ["problem", "issue", "bug", "error"]):
            return "Sorry to hear that! Let me look into this for you. Can you DM me more details?"
        else:
            return "Thanks for reaching out! I appreciate you connecting with me."


def create_reply_generator_from_config(
    provider_name: str = "none",
    model: Optional[str] = None,
    temperature: float = 0.7,
    custom_prompt: Optional[str] = None,
) -> AIReplyGenerator:
    """
    Factory function to create AIReplyGenerator from config.

    Args:
        provider_name: Name of the provider ("openai", "anthropic", "ollama", "groq", "none")
        model: Optional model override
        temperature: Response randomness
        custom_prompt: Optional custom system prompt

    Returns:
        Configured AIReplyGenerator instance
    """
    # Parse provider name
    provider_map = {
        "openai": AIProvider.OPENAI,
        "anthropic": AIProvider.ANTHROPIC,
        "claude": AIProvider.ANTHROPIC,
        "ollama": AIProvider.OLLAMA,
        "groq": AIProvider.GROQ,
        "none": AIProvider.NONE,
        "": AIProvider.NONE,
    }

    provider = provider_map.get(provider_name.lower(), AIProvider.NONE)

    return AIReplyGenerator(
        provider=provider,
        model=model,
        temperature=temperature,
        system_prompt=custom_prompt,
    )


# Example usage
if __name__ == "__main__":
    # Example 1: Using OpenAI
    print("Example 1: OpenAI GPT-4")
    try:
        generator = create_reply_generator_from_config("openai")
        reply = generator.generate_reply(
            mention_text="Hey, loving your app! Can you add dark mode?",
            mention_author="techfan123",
        )
        print(f"Reply: {reply}\n")
    except Exception as e:
        print(f"Error: {e}\n")

    # Example 2: Using template fallback (no API key needed)
    print("Example 2: Template-based (no AI)")
    generator = create_reply_generator_from_config("none")
    reply = generator.generate_reply(
        mention_text="Thanks so much for the help!",
        mention_author="happyuser",
    )
    print(f"Reply: {reply}\n")

    # Example 3: Using Anthropic Claude
    print("Example 3: Anthropic Claude")
    try:
        generator = create_reply_generator_from_config("anthropic")
        reply = generator.generate_reply(
            mention_text="Your pizza app is broken, nothing works!",
            mention_author="frustrated_user",
        )
        print(f"Reply: {reply}\n")
    except Exception as e:
        print(f"Error: {e}\n")

