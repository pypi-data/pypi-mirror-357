# langchain-qwq

This package provides LangChain integration with QwQ models and other Qwen series models from Alibaba Cloud DashScope, with enhancements for Qwen3 models.

## Features

- **QwQ Model Integration**: Full support for QwQ models with reasoning capabilities
- **Qwen3 Model Integration**: Complete support for Qwen3 series models with hybrid reasoning
- **Other Qwen Models**: Support for Qwen-Max, Qwen2.5, and other Qwen series models
- **Vision Models**: Support for Qwen-VL series vision models
- **Streaming Support**: Both sync and async streaming capabilities
- **Tool Calling**: Function calling with parallel execution support
- **Structured Output**: JSON mode and function calling for structured responses
- **Reasoning Access**: Direct access to model reasoning/thinking content

## Installation

```bash
pip install -U langchain-qwq
```

OR if you want to install additional dependencies when you clone the repo:

```bash
pip install -U langchain-qwq[docs]
pip install -U langchain-qwq[test]
pip install -U langchain-qwq[codespell]
pip install -U langchain-qwq[lint]
pip install -U langchain-qwq[typing]
```

## Environment Variables

Configure credentials by setting the following environment variables:

* `DASHSCOPE_API_KEY`: Your DashScope API key for accessing QwQ or Qwen models (required)
* `DASHSCOPE_API_BASE`: (Optional) API base URL, defaults to "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"

**Note**: For domestic Chinese users, you typically need to set `DASHSCOPE_API_BASE` to the domestic endpoint as langchain-qwq defaults to the international version of Alibaba Cloud.

## ChatQwQ

`ChatQwQ` class exposes chat models from QwQ with reasoning capabilities.

### Basic Usage

```python
from langchain_qwq import ChatQwQ

model = ChatQwQ(model="qwq-32b")
response = model.invoke("Hello, how are you?")
print(response.content)
```

### Accessing Reasoning Content

QwQ models provide reasoning/thinking content that can be accessed through `additional_kwargs`:

```python
response = model.invoke("Hello")
content = response.content
reasoning = response.additional_kwargs.get("reasoning_content", "")
print(f"Response: {content}")
print(f"Reasoning: {reasoning}")
```

### Streaming

#### Sync Streaming

```python
model = ChatQwQ(model="qwq-32b")

is_first = True
is_end = True

for msg in model.stream("Hello"):
    if hasattr(msg, 'additional_kwargs') and "reasoning_content" in msg.additional_kwargs:
        if is_first:
            print("Starting to think...")
            is_first = False   
        print(msg.additional_kwargs["reasoning_content"], end="", flush=True)
    elif hasattr(msg, 'content') and msg.content:
        if is_end:
            print("\nThinking ended")
            is_end = False
        print(msg.content, end="", flush=True)
```

#### Async Streaming

```python
is_first = True
is_end = True

async for msg in model.astream("Hello"):
    if hasattr(msg, 'additional_kwargs') and "reasoning_content" in msg.additional_kwargs:
        if is_first:
            print("Starting to think...")
            is_first = False
        print(msg.additional_kwargs["reasoning_content"], end="", flush=True)
    elif hasattr(msg, 'content') and msg.content:
        if is_end:   
            print("\nThinking ended")
            is_end = False
        print(msg.content, end="", flush=True)
```

### Convenient Reasoning Display

Use utility functions to easily display reasoning content:

```python
from langchain_qwq.utils import convert_reasoning_to_content

# Sync
for msg in convert_reasoning_to_content(model.stream("Hello")):
    print(msg.content, end="", flush=True)

# Async
from langchain_qwq.utils import aconvert_reasoning_to_content

async for msg in aconvert_reasoning_to_content(model.astream("Hello")):
    print(msg.content, end="", flush=True)
```

You can also customize the think tags:

```python
async for msg in aconvert_reasoning_to_content(
    model.astream("Hello"), 
    think_tag=("<Start>", "<End>")
):
    print(msg.content, end="", flush=True)
```

### Tool Calling

#### Basic Tool Usage

```python
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """Get the weather for a city"""
    return f"The weather in {city} is sunny."

bound_model = model.bind_tools([get_weather])
response = bound_model.invoke("What's the weather in New York?")
print(response.tool_calls)
```

#### Parallel Tool Calling

```python
# Enable parallel tool calls
response = bound_model.invoke(
    "What's the weather in New York and London?", 
    parallel_tool_calls=True
)
print(response.tool_calls)
```

### Structured Output

#### JSON Mode

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

struct_model = model.with_structured_output(User, method="json_mode")
response = struct_model.invoke("Hello, I'm John and I'm 25 years old")
print(response)  # User(name='John', age=25)
```

#### Function Calling Mode

```python
struct_model = model.with_structured_output(User, method="function_calling")
response = struct_model.invoke("My name is Alice and I'm 30")
print(response)  # User(name='Alice', age=30)
```

### Integration with LangChain Agents

```python
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

agent = create_tool_calling_agent(
    model,
    [get_weather],
    prompt=ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant"),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
)

agent_executor = AgentExecutor(agent=agent, tools=[get_weather])
result = agent_executor.invoke({"input": "What's the weather in Beijing?"})
print(result)
```

## ChatQwen

`ChatQwen` provides better support for Qwen3 and other Qwen series models, including enhanced parameter support for Qwen3's thinking functionality.

### Basic Usage

```python
from langchain_qwq import ChatQwen

# Qwen3 model
model = ChatQwen(model="qwen3-32b")
response = model.invoke("Hello")
print(response.content)

# Access reasoning content (for Qwen3)
reasoning = response.additional_kwargs.get("reasoning_content", "")
print(f"Reasoning: {reasoning}")
```

### Thinking Control (Qwen3 Only)

#### Disable Thinking Mode

For Qwen3 models, thinking is enabled by default for open-source models and disabled for proprietary models. You can control this:

```python
# Disable thinking for open-source Qwen3 models
model = ChatQwen(model="qwen3-32b", enable_thinking=False)
response = model.invoke("Hello")
print(response.content)  # No reasoning content
```

#### Enable Thinking for Proprietary Models

```python
# Enable thinking for proprietary models
model = ChatQwen(model="qwen-plus-latest", enable_thinking=True)
response = model.invoke("Hello")
reasoning = response.additional_kwargs.get("reasoning_content", "")
print(f"Reasoning: {reasoning}")
```

#### Control Thinking Length

```python
# Set thinking budget (max thinking tokens)
model = ChatQwen(model="qwen3-32b", thinking_budget=20)
response = model.invoke("Hello")
reasoning = response.additional_kwargs.get("reasoning_content", "")
print(f"Limited reasoning: {reasoning}")
```

### Other Qwen Models

#### Qwen-Max

```python
model = ChatQwen(model="qwen-max")
print(model.invoke("Hello").content)

# Tool calling
bound_model = model.bind_tools([get_weather])
response = bound_model.invoke("Weather in Shanghai and Beijing?", parallel_tool_calls=True)
print(response.tool_calls)

# Structured output
struct_model = model.with_structured_output(User, method="json_mode")
result = struct_model.invoke("I'm Bob, 28 years old")
print(result)
```

#### Qwen2.5-72B

```python
model = ChatQwen(model="qwen2.5-72b-instruct")
print(model.invoke("Hello").content)

# All features work the same as other models
bound_model = model.bind_tools([get_weather])
struct_model = model.with_structured_output(User, method="json_mode")
```

### Vision Models

```python
from langchain_core.messages import HumanMessage

model = ChatQwen(model="qwen-vl-max-latest")

messages = [
    HumanMessage(content=[
        {
            "type": "image_url",
            "image_url": {
                "url": "https://example.com/image.jpg"
            },
        },
        {"type": "text", "text": "What do you see in this image?"},
    ])
]

response = model.invoke(messages)
print(response.content)
```


## Model Comparison

| Feature | ChatQwQ | ChatQwen |
|---------|---------|----------|
| QwQ Models | ✅ Primary | ✅ Supported |
| Qwen3 Models | ✅ Basic | ✅ Enhanced |
| Other Qwen Models | ❌ | ✅ Full Support |
| Vision Models | ❌ | ✅ Supported |
| Thinking Control | ❌ | ✅ (Qwen3 only) |
| Thinking Budget | ❌ | ✅ (Qwen3 only) |

