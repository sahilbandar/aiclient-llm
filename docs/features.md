# Features

## Local LLMs (Ollama & LMStudio) 🏠

`aiclient-llm` supports routing requests to local inference servers using the `provider:model` syntax.

### Usage
Default (Ollama):
```python
# Connects to http://localhost:11434/v1
response = client.chat("ollama:llama3").generate("Hi")
```

Custom URL (e.g., LMStudio, remote server):
```python
client = Client(ollama_base_url="http://192.168.1.5:1234/v1")
response = client.chat("ollama:mistral").generate("Hi")
```

## Agents & Tool Use 🤖

Build powerful agents using the `Agent` class, which implements a ReAct loop.

```python
from aiclient import Client, Agent

def get_weather(city: str):
    return f"Sunny in {city}"

client = Client()
agent = Agent(
    model=client.chat("gpt-4o"),
    tools=[get_weather],
    max_steps=10
)

result = agent.run("What's the weather in Tokyo?")
print(result)
```

## Multimodal (Vision) 👁️

Send images easily to models that support it (GPT-4o, Claude 3, Gemini, etc.).

```python
from aiclient.types import UserMessage, Text, Image

msg = UserMessage(content=[
    Text(text="Analyze this diagram"),
    Image(path="./chart.png") # Automatically base64 encoded
])

response = client.chat("gpt-4o").generate([msg])
```

## Structured Output (Pydantic) 📦

Validate responses against a schema.

```python
from pydantic import BaseModel

class UserInfo(BaseModel):
    name: str
    age: int

user = client.chat("gpt-4o").generate(
    "John is 25 years old", 
    response_model=UserInfo
)
print(user.name, user.age)
```
