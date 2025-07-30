"""
Nvidia NIM Provider for Strands Agents SDK

A minimal custom provider that fixes message formatting between 
Strands structured content and Nvidia NIM's string format.
"""

from typing import Any, Iterable, Optional, TypedDict
from typing_extensions import Unpack, override

import litellm

from strands.types.models import Model
from strands.types.content import Messages, ContentBlock
from strands.types.streaming import StreamEvent
from strands.types.tools import ToolConfig
from strands.types.exceptions import ContextWindowOverflowException


class NvidiaNIM(Model):
    """Nvidia NIM provider for Strands - fixes message formatting issues."""

    class Config(TypedDict, total=False):
        model_id: str
        params: Optional[dict[str, Any]]

    def __init__(self, api_key: str, **config: Unpack[Config]) -> None:
        """Initialize Nvidia NIM provider.
        
        Args:
            api_key: Nvidia NIM API key
            **config: Model configuration (model_id, params)
        """
        self.config = config
        self.api_key = api_key

    @override
    def update_config(self, **config: Unpack[Config]) -> None:
        """Update model configuration."""
        self.config.update(config)

    @override
    def get_config(self) -> Config:
        """Get current model configuration."""
        return self.config

    def _extract_text(self, content_blocks: list[ContentBlock]) -> str:
        """Extract text from Strands content blocks."""
        return " ".join(block["text"] for block in content_blocks if "text" in block).strip()

    @override
    def format_request(
        self,
        messages: Messages,
        tool_specs: Optional[ToolConfig] = None,
        system_prompt: Optional[str] = None
    ) -> dict[str, Any]:
        """Convert Strands messages to Nvidia NIM format."""
        formatted_messages = []
        
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        
        for message in messages:
            content = self._extract_text(message["content"])
            if content:
                formatted_messages.append({"role": message["role"], "content": content})

        return {
            "model": self.config["model_id"],
            "messages": formatted_messages,
            "stream": True,
            **self.config.get("params", {})
        }

    @override
    def format_chunk(self, event: Any) -> StreamEvent:
        """Convert Nvidia NIM response to Strands format."""
        if hasattr(event, 'choices') and event.choices:
            choice = event.choices[0]
            
            if hasattr(choice, 'delta') and choice.delta and hasattr(choice.delta, 'content'):
                if choice.delta.content:
                    return {"contentBlockDelta": {"delta": {"text": choice.delta.content}}}
            
            if hasattr(choice, 'finish_reason') and choice.finish_reason:
                return {"messageStop": {"stopReason": "end_turn"}}

        return {"contentBlockDelta": {"delta": {"text": ""}}}

    @override
    def stream(self, request: dict[str, Any]) -> Iterable[Any]:
        """Stream from Nvidia NIM API."""
        try:
            response = litellm.completion(
                api_key=self.api_key,
                base_url="https://integrate.api.nvidia.com/v1",
                **request
            )
            
            yield {"messageStart": {"role": "assistant"}}
            yield {"contentBlockStart": {"start": {}}}
            
            for chunk in response:
                if chunk:
                    yield chunk
                    
            yield {"contentBlockStop": {}}
            
        except Exception as e:
            if any(word in str(e).lower() for word in ["context", "token", "length"]):
                raise ContextWindowOverflowException() from e
            raise
