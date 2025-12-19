from typing import Protocol, Union, List, Any
from .types import BaseMessage, ModelResponse, Usage

class Middleware(Protocol):
    def before_request(self, model: str, prompt: Union[str, List[BaseMessage]]) -> Union[str, List[BaseMessage]]:
        """
        Intercept and modify the request before it is sent to the provider.
        Returns the modified prompt (or messages).
        """
        ...

    def after_response(self, response: ModelResponse) -> ModelResponse:
        """
        Intercept and modify the response after it is received from the provider.
        Returns the modified response.
        """
        ...

class CostTrackingMiddleware:
    """
    Middleware to track total usage/cost across requests.
    (Note: Cost calculation requires pricing tables, here we track tokens as a proxy/proof of concept)
    """
    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def before_request(self, model: str, prompt: Union[str, List[BaseMessage]]) -> Union[str, List[BaseMessage]]:
        # Passthrough
        return prompt

    def after_response(self, response: ModelResponse) -> ModelResponse:
        if response.usage:
            self.total_input_tokens += response.usage.input_tokens
            self.total_output_tokens += response.usage.output_tokens
        return response
