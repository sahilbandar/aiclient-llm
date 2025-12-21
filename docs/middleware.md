# Middleware & Observability

Middleware allows you to inject custom logic before a request is sent to the LLM and after a response is received. This is useful for logging, cost tracking, prompt engineering, or PII masking.

## How it Works

A middleware is any class that implements the `Middleware` protocol:

```python
class Middleware(Protocol):
    def before_request(self, model: str, prompt: Union[str, List[BaseMessage]]) -> Union[str, List[BaseMessage]]:
        ...
    def after_response(self, response: ModelResponse) -> ModelResponse:
        ...
```

## Built-in Middleware

### CostTrackingMiddleware

Tracks estimated token usage and USD cost across all requests in a session.

```python
from aiclient import Client
from aiclient.middleware import CostTrackingMiddleware

# 1. Create tracker
tracker = CostTrackingMiddleware()

# 2. Attach to client
client = Client()
client.add_middleware(tracker)

# 3. Use client
client.chat("gpt-4o").generate("Hello")

# 4. Check stats
print(f"Total Cost: ${tracker.total_cost_usd:.4f}")
print(f"Tokens: {tracker.total_input_tokens} In / {tracker.total_output_tokens} Out")
```

## Creating Custom Middleware

### Example: Logging Middleware

```python
class LoggingMiddleware:
    def before_request(self, model, prompt):
        print(f"[LOG] Sending request to {model}")
        return prompt # Must return prompt
        
    def after_response(self, response):
        print(f"[LOG] Received {response.usage.total_tokens} tokens")
        return response # Must return response

client.add_middleware(LoggingMiddleware())
```

### Example: PII Redaction

```python
class PIIFilterMiddleware:
    def before_request(self, model, prompt):
        if isinstance(prompt, str):
            return prompt.replace("EMAIL_ADDRESS", "[REDACTED]")
        return prompt
        
    def after_response(self, response):
        return response
```
