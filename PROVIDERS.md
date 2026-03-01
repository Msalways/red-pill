# Redpill LLM Providers

Redpill supports multiple LLM providers through a unified interface. This document covers all available providers and how to create custom ones.

---

## Available Providers

| Provider | Name(s) | Description |
|-----------|----------|-------------|
| OpenAI | `openai` | OpenAI GPT models |
| Anthropic | `anthropic` | Claude models |
| Amazon Bedrock | `bedrock`, `amazon`, `aws` | AWS-hosted models |
| Ollama | `ollama`, `local` | Local models |
| Azure OpenAI | `azure`, `azureopenai` | Azure-hosted OpenAI |
| Google Gemini | `google`, `gemini` | Google Gemini models |
| Cohere | `cohere` | Cohere models |
| HuggingFace | `huggingface`, `hf` | HuggingFace Inference API |
| Custom | `custom` | Any OpenAI-compatible API |

---

## Quick Start

### OpenAI

```python
from redpill import Redpill

rp = (
    Redpill()
    .provider("openai")
    .api_key("sk-...")
    .model("gpt-4o")
    .build()
)
```

### Anthropic

```python
rp = (
    Redpill()
    .provider("anthropic")
    .api_key("sk-ant-...")
    .model("claude-3-5-sonnet-20241022")
    .build()
)
```

### Amazon Bedrock

```python
rp = (
    Redpill()
    .provider("bedrock")
    .model("anthropic.claude-3-sonnet-20240229-v1:0")
    .region("us-east-1")
    .credentials_profile_name("default")  # optional
    .build()
)
```

### Ollama (Local)

```python
rp = (
    Redpill()
    .provider("ollama")
    .base_url("http://localhost:11434")
    .model("llama3.2")
    .build()
)
```

### Azure OpenAI

```python
rp = (
    Redpill()
    .provider("azure")
    .api_key("your-azure-key")
    .base_url("https://your-resource.openai.azure.com")
    .model("gpt-4o")
    .api_version("2024-02-15-preview")
    .### Google Gemini

build()
)
```

```python
rp = (
    Redpill()
    .provider("gemini")
    .api_key("your-google-api-key")
    .model("gemini-2.0-flash")
    .build()
)
```

### Cohere

```python
rp = (
    Redpill()
    .provider("cohere")
    .api_key("your-cohere-key")
    .model("command-r-plus")
    .build()
)
```

### HuggingFace

```python
rp = (
    Redpill()
    .provider("hf")
    .api_key("your-hf-token")
    .model("meta-llama/Llama-3.2-1B-Instruct")
    .build()
)
```

---

## Creating Custom Providers

### Option 1: Using CustomProvider (OpenAI-Compatible)

For APIs that follow OpenAI's chat completion format:

```python
from redpill.providers.custom import CustomProvider, ProviderFactory

class MyLLMProvider(CustomProvider):
    """My custom LLM provider."""
    
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.myllm.com/v1",
        model: str = "my-model",
        **kwargs
    ) -> None:
        super().__init__(model=model, **kwargs)
        self.api_key = api_key
        self.base_url = base_url

# Register your provider
ProviderFactory.register("mylLM", MyLLMProvider)

# Use it
rp = (
    Redpill()
    .provider("mylLM")
    .api_key("your-api-key")
    .model("your-model")
    .build()
)
```

### Option 2: Extending CustomProvider with Custom Response Parsing

If your API has a different response format:

```python
from redpill.providers.custom import CustomProvider, ProviderFactory

class MyCustomProvider(CustomProvider):
    """Provider with custom response parsing."""
    
    def _parse_response(self, response: dict) -> str:
        # Customize how to extract text from API response
        return response.get("output", {}).get("text", "")

ProviderFactory.register("mycustom", MyCustomProvider)
```

### Option 3: Full Custom Implementation

For completely custom APIs:

```python
from typing import Any, Type
from redpill.providers.base import LLMProvider, ProviderFactory
from pydantic import BaseModel
import httpx

class FullyCustomProvider(LLMProvider):
    """Fully custom provider implementation."""
    
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.example.com",
        model: str = "default",
        **kwargs: Any
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.kwargs = kwargs
    
    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> str:
        # Implement your own API call
        url = f"{self.base_url}/generate"
        
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "prompt": prompt,
            "model": self.model,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        with httpx.Client() as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
        
        return response.json()["text"]
    
    def generate_json(
        self,
        prompt: str,
        response_schema: Type[BaseModel],
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> BaseModel:
        # Implement JSON generation
        text = self.generate(prompt, system_prompt, temperature, max_tokens)
        import json
        return response_schema(**json.loads(text))

# Register
ProviderFactory.register("fullycustom", FullyCustomProvider)
```

---

## Custom Provider Template

Here's a template you can copy to create new providers:

```python
"""Custom provider for [Your LLM Service]."""

from typing import Any, Type

import httpx
from pydantic import BaseModel

from redpill.providers.base import LLMProvider, ProviderFactory


class YourProviderNameProvider(LLMProvider):
    """Provider for [Your LLM Service].
    
    Description of what this provider supports.
    """
    
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.yourservice.com/v1",
        model: str = "default-model",
        timeout: float = 60.0,
        **kwargs: Any,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.kwargs = kwargs
    
    def _get_headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    def _parse_response(self, response: dict) -> str:
        # Customize this for your API
        choices = response.get("choices", [])
        if choices:
            return choices[0].get("message", {}).get("content", "")
        return ""
    
    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> str:
        url = f"{self.base_url}/chat/completions"
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                url, 
                json=payload, 
                headers=self._get_headers()
            )
            response.raise_for_status()
            data = response.json()
        
        return self._parse_response(data)
    
    def generate_json(
        self,
        prompt: str,
        response_schema: Type[BaseModel],
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> BaseModel:
        import json
        text = self.generate(prompt, system_prompt, temperature, max_tokens)
        return response_schema(**json.loads(text))


# Register the provider
ProviderFactory.register("yourprovider", YourProviderNameProvider)
```

---

## Base API Reference

### LLMProvider (Abstract Base Class)

```python
class LLMProvider(ABC):
    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> str:
        """Generate text response."""
    
    @abstractmethod
    def generate_json(
        self,
        prompt: str,
        response_schema: Type[BaseModel],
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> BaseModel:
        """Generate JSON response with schema validation."""
```

### ProviderFactory

```python
# Register a new provider
ProviderFactory.register("name", ProviderClass)

# Create a provider
provider = ProviderFactory.create(
    name="openai",
    api_key="...",
    base_url="...",
    model="..."
)

# List available providers
providers = ProviderFactory.available_providers()
```

---

## Environment Variables

Some providers support environment variables:

| Provider | Variables |
|----------|-----------|
| Bedrock | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION` |
| Azure | `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT` |
| Ollama | None required (uses localhost) |

---

## Installation

```bash
# Core dependencies (included)
pip install redpill

# With all provider dependencies
pip install redpill[all]

# Individual provider dependencies
pip install langchain-aws        # Bedrock
pip install langchain-ollama     # Ollama
pip install google-generativeai  # Gemini
pip install cohere              # Cohere
```
