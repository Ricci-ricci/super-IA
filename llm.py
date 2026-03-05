"""
Local LLM client for Ollama integration.

This module provides a simple HTTP client to interact with Ollama running locally.
Ollama exposes an OpenAI-compatible API at localhost:11434 by default.

Usage:
    from llm import OllamaClient

    client = OllamaClient()
    response = client.chat("llama3.1:8b", "What are common SSH hardening steps?")
    print(response)
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class LLMResponse:
    """Response from the LLM with metadata."""

    content: str
    model: str
    finish_reason: str
    usage: Optional[Dict[str, Any]] = None


class OllamaClient:
    """Simple HTTP client for Ollama local LLM server."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama client.

        Args:
            base_url: Ollama server URL (default: http://localhost:11434)
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = 60  # seconds

    def chat(
        self,
        model: str,
        message: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
    ) -> str:
        """
        Send a chat message to the local LLM.

        Args:
            model: Model name (e.g., "llama3.1:8b", "qwen2.5:7b")
            message: User message to send
            system_prompt: Optional system prompt to set context
            temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)

        Returns:
            The LLM's response as a string

        Raises:
            ConnectionError: If Ollama server is not reachable
            ValueError: If the response is invalid
        """
        # Build messages array (OpenAI format)
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": message})

        # Prepare request payload
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": False,  # Get complete response, not streaming
        }

        try:
            return self._send_request("/v1/chat/completions", payload)
        except Exception as e:
            # Fallback error message if LLM fails
            return f"[LLM Error] Could not generate response: {str(e)}"

    def _send_request(self, endpoint: str, payload: Dict[str, Any]) -> str:
        """
        Send HTTP POST request to Ollama server.

        Args:
            endpoint: API endpoint (e.g., "/v1/chat/completions")
            payload: Request data as dictionary

        Returns:
            Response content from the LLM
        """
        url = f"{self.base_url}{endpoint}"

        # Encode payload as JSON
        data = json.dumps(payload).encode("utf-8")

        # Create HTTP request
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )

        try:
            # Send request with timeout
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                response_data = response.read().decode("utf-8")

            # Parse JSON response
            result = json.loads(response_data)

            # Extract content from OpenAI-compatible response
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                raise ValueError(f"Unexpected response format: {result}")

        except urllib.error.URLError as e:
            raise ConnectionError(
                f"Cannot connect to Ollama at {url}. Is Ollama running? Error: {e}"
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from Ollama: {e}")

    def is_available(self) -> bool:
        """
        Check if Ollama server is running and responsive.

        Returns:
            True if server is available, False otherwise
        """
        try:
            # Try a simple health check (Ollama has a /api/tags endpoint)
            req = urllib.request.Request(f"{self.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=5):
                return True
        except:
            return False

    def list_models(self) -> list[str]:
        """
        Get list of available models from Ollama.

        Returns:
            List of model names, or empty list if unavailable
        """
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode("utf-8"))
                return [model["name"] for model in data.get("models", [])]
        except:
            return []


# Pentesting-focused system prompt
PENTEST_SYSTEM_PROMPT = """You are a cybersecurity assistant that helps with AUTHORIZED penetration testing and defensive security analysis.

CRITICAL RULES:
- Only provide guidance for AUTHORIZED testing with explicit permission and scope
- Always emphasize safety, non-destructive methods, and proper documentation
- Refuse any request for unauthorized access, illegal activity, or harmful actions
- Focus on defensive security, risk assessment, and remediation guidance

Your expertise areas:
- Service enumeration and configuration analysis
- Vulnerability assessment and risk prioritization
- Security hardening recommendations
- Professional security reporting
- Compliance frameworks (OWASP, NIST, etc.)

Always ask for scope/authorization details if missing, and provide practical, actionable advice within authorized boundaries."""


def create_pentest_client(model: str = "llama3.1:8b") -> OllamaClient:
    """
    Create a pre-configured Ollama client for pentesting use.

    Args:
        model: Default model to use (should be pulled in Ollama first)

    Returns:
        Configured OllamaClient instance
    """
    return OllamaClient()


def quick_chat(message: str, model: str = "llama3.1:8b") -> str:
    """
    Quick helper for one-shot pentest questions.

    Args:
        message: Question or context to send to LLM
        model: Model name to use

    Returns:
        LLM response with pentesting context
    """
    client = OllamaClient()

    if not client.is_available():
        return "[Error] Ollama server not available. Please start Ollama and ensure the model is pulled."

    return client.chat(
        model=model,
        message=message,
        system_prompt=PENTEST_SYSTEM_PROMPT,
        temperature=0.3,  # Slightly creative but focused
    )
