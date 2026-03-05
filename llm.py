"""
Local LLM client for Ollama integration.

This module provides a simple HTTP client to interact with Ollama running locally.
Ollama exposes its native API at localhost:11434 by default.

Usage:
    from llm import OllamaClient, PENTEST_SYSTEM_PROMPT

    client = OllamaClient()
    if client.is_available():
        response = client.chat("llama3.2:1b", "What are common SSH hardening steps?", PENTEST_SYSTEM_PROMPT)
        print(response)
"""

from __future__ import annotations

import json
from typing import Optional

# Try to import requests, fall back gracefully if not available
try:
    import requests

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# Pentesting-focused system prompt - simplified for faster inference
PENTEST_SYSTEM_PROMPT = """You are a pentesting assistant for AUTHORIZED security testing only.

Analyze services and provide:
1. Risk level (High/Medium/Low)
2. Testing recommendations
3. Evidence to collect

Keep responses concise and actionable."""


class OllamaClient:
    """Simple HTTP client for Ollama local LLM server using native API."""

    def __init__(
        self, base_url: str = "http://localhost:11434", model: str = "llama3.2:1b"
    ):
        """
        Initialize Ollama client.

        Args:
            base_url: Ollama server URL (default: http://localhost:11434)
            model: Default model name to use
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = 120  # seconds - increased for CPU inference
        self.available = HAS_REQUESTS

    def chat(
        self,
        model: str,
        message: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
    ) -> Optional[str]:
        """
        Send a chat message to the local LLM using Ollama's native API.

        Args:
            model: Model name (e.g., "llama3.2:1b")
            message: User message to send
            system_prompt: Optional system prompt to set context
            temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)

        Returns:
            The LLM's response as a string, or None if failed
        """
        if not self.available:
            return None

        # Prepare the prompt with system context if provided
        if system_prompt:
            full_prompt = f"System: {system_prompt}\n\nUser: {message}\n\nResponse:"
        else:
            full_prompt = message

        # Prepare request payload for Ollama's native /api/generate endpoint
        payload = {
            "model": model,
            "prompt": full_prompt,
            "stream": False,  # Get complete response, not streaming
            "options": {
                "temperature": temperature,
                "top_p": 0.9,
            },
        }

        try:
            return self._send_request("/api/generate", payload)
        except Exception as e:
            print(f"[DEBUG] LLM Error: {str(e)}")
            return None

    def _send_request(self, endpoint: str, payload: dict) -> Optional[str]:
        """
        Send HTTP POST request to Ollama server.

        Args:
            endpoint: API endpoint (e.g., "/api/generate")
            payload: Request data as dictionary

        Returns:
            Response content from the LLM, or None if failed
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 200:
                result = response.json()
                # Ollama's native API returns response in "response" field
                content = result.get("response", "").strip()
                return content
            else:
                return None

        except requests.exceptions.ConnectionError:
            return None
        except requests.exceptions.Timeout:
            return None
        except requests.exceptions.RequestException:
            return None
        except json.JSONDecodeError:
            return None

    def is_available(self) -> bool:
        """
        Check if Ollama server is running and responsive.

        Returns:
            True if server is available, False otherwise
        """
        if not self.available:
            return False

        try:
            # Try a simple health check using Ollama's /api/tags endpoint
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def list_models(self) -> list[str]:
        """
        Get list of available models from Ollama.

        Returns:
            List of model names, or empty list if unavailable
        """
        if not self.available:
            return []

        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except:
            pass
        return []


def quick_test() -> bool:
    """Quick test to see if Ollama is working with simple prompt."""
    client = OllamaClient()

    if not client.is_available():
        print("Ollama not available")
        return False

    response = client.chat("llama3.2:1b", "Hi", None, 0.1)
    print(f"Test response: {response}")
    return response is not None


def quick_chat(message: str, model: str = "llama3.2:1b") -> Optional[str]:
    """
    Quick helper for one-shot pentest questions.

    Args:
        message: Question or context to send to LLM
        model: Model name to use

    Returns:
        LLM response with pentesting context, or None if failed
    """
    client = OllamaClient()

    if not client.is_available():
        return None

    return client.chat(
        model=model,
        message=message,
        system_prompt=PENTEST_SYSTEM_PROMPT,
        temperature=0.3,
    )
