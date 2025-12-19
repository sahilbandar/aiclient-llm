import pytest
from aiclient import Client
from aiclient.middleware import Middleware
from aiclient.types import UserMessage, ModelResponse, Usage
from tests.test_client import MockTransport # Reuse mock transport logic

class SuffixMiddleware:
    def before_request(self, model, prompt):
        # prompt is List[BaseMessage]
        last_msg = prompt[-1]
        last_msg.content += " [SUFFIX]"
        return prompt

    def after_response(self, response):
        return response

def test_middleware_modifies_request():
    # Setup Client
    client = Client(openai_api_key="sk-test", transport_factory=lambda **kwargs: MockTransport(**kwargs, response_data={
        "choices": [{"message": {"content": "Hello"}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
    }))
    
    # Add Middleware
    client.add_middleware(SuffixMiddleware())
    
    # Chat
    model = client.chat("gpt-4")
    response = model.generate("Hello")
    
    # Verify Middleware ran (by checking what was sent)
    # The MockTransport stores sent_data
    sent_data = model.transport.sent_data
    assert len(sent_data) > 0
    last_req = sent_data[-1]
    url, data, headers = last_req
    
    messages = data["messages"]
    assert messages[0]["content"] == "Hello [SUFFIX]"

from aiclient.middleware import CostTrackingMiddleware

def test_cost_tracking_middleware():
    client = Client(openai_api_key="sk-test", transport_factory=lambda **kwargs: MockTransport(**kwargs, response_data={
        "choices": [{"message": {"content": "Hello"}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
    }))
    
    tracker = CostTrackingMiddleware()
    client.add_middleware(tracker)
    
    model = client.chat("gpt-4")
    model.generate("Hello")
    
    assert tracker.total_input_tokens == 10
    assert tracker.total_output_tokens == 5
