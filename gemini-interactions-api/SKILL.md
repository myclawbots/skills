---
name: gemini_interactions_api
description: Use the Gemini Interactions API for stateful multi-turn conversations, background deep research tasks, streaming responses, function calling, and agentic workflows. The recommended way to build with Gemini for complex, multi-step agent tasks.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: ai
tags: [gemini, google, agents, deep-research]
suggested_template: research_agent
---

# Gemini Interactions API Skill

The Interactions API provides stateful, multi-turn conversation management with support for background deep research agents, function calling, and streaming. Use this for agent workflows that require maintaining conversation state across multiple requests.

## Dependencies

| Dependency | Required? | Why |
|---|---|---|
| `gemini-api` skill | No | Recommended: for understanding basic Gemini setup |
| `$GEMINI_KEY` | Yes | Stand-in for the user's Gemini key (use with `vault-curl`) |
| `google-genai >= 1.55.0` | No | Python SDK (or `@google/genai >= 1.33.0` for JavaScript): only with the vault proxy (see below) |

**Pre-flight checks:**
- `[ -n "$GEMINI_KEY" ] && echo present || vault-curl --secrets`
- Not in your env but listed by `vault-curl --secrets` (added after you started): use that entry's `surrogate` string in place of `$GEMINI_KEY`. No restart is needed.
- Agents not yet moved to the vault: if there is no `GEMINI_KEY` anywhere but a `GEMINI_API_KEY` variable is set, it holds a real key: use plain `curl` with that variable in the same `x-goog-api-key` header. Never print it.
- Nothing found: ask the user to add a Gemini key in **MyClawBots → Settings → Integrations → Google AI** (free at [aistudio.google.com](https://aistudio.google.com/apikey)). Never ask them to paste a key into chat.
- Verify Python 3.9+ or Node.js 18+ is installed
- Verify `google-genai >= 1.55.0` is installed: `pip list | grep google-genai`
- Ensure `gemini-api` skill documentation is available for reference

## Prerequisites

- A Gemini key saved in MyClawBots (you get the stand-in `$GEMINI_KEY`; see "Your Gemini key" below)
- Python 3.9+ or Node.js 18+
- `google-genai >= 1.55.0` (Python) or `@google/genai >= 1.33.0` (JavaScript)

## Your Gemini key

You never see the real key: `$GEMINI_KEY` holds a stand-in (`mcb_sec_…`) that only works through **`vault-curl`**, which swaps in the real key on the way to `generativelanguage.googleapis.com`. Put it **only** in the `x-goog-api-key` header (never `?key=`, the body or a file), and never print it. Don't use OpenClaw's built-in secrets tool: these keys are not stored there.

REST with `vault-curl` always works:

```bash
vault-curl -sS "https://generativelanguage.googleapis.com/v1beta/interactions" \
  -H "x-goog-api-key: $GEMINI_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gemini-3-flash-preview","input":"Explain async/await in Python"}'
```

The Python examples below send the stand-in straight from the SDK, so they work **only when AGENTS.md says plain `curl` and SDKs work** (the MyClawBots vault proxy is on). Otherwise use the REST form above.

## Installation

```bash
pip install google-genai
```

## Current Supported Models

Use these models with the Interactions API:

- **gemini-3.1-pro-preview** - Advanced reasoning, longest context (128K)
- **gemini-3-flash-preview** - Fast, efficient, multimodal
- **deep-research-pro-preview-12-2025** - For background research tasks (async)

**Deprecated:** gemini-3-flash, gemini-3-pro are no longer recommended.

## Quick Start: Basic Interaction

```python
import os
from google import genai

# The stand-in for the user's key; needs the vault proxy (see "Your Gemini key")
if not os.environ.get('GEMINI_KEY'):
    raise ValueError("GEMINI_KEY not set. Run `vault-curl --secrets` or ask the user to add a Gemini key in MyClawBots.")

client = genai.Client(api_key=os.environ['GEMINI_KEY'])

# Create a single interaction
response = client.models.create_interaction(
    model="gemini-3.1-pro-preview",
    system_instruction="You are a helpful coding assistant.",
    user_input="Explain async/await in Python"
)

# Access outputs
for output in response.outputs:
    if output.text:
        print(output.text)

# Save to gws for persistence
interaction_id = response.interaction_id
print(f"Interaction ID: {interaction_id}")
```

## Stateful Conversations with Memory

Use `previous_interaction_id` to continue a conversation:

```python
# First turn
response1 = client.models.create_interaction(
    model="gemini-3.1-pro-preview",
    system_instruction="You are a Python tutor.",
    user_input="What is a decorator?"
)
interaction_id = response1.interaction_id

# Second turn - continue with conversation history
response2 = client.models.create_interaction(
    model="gemini-3.1-pro-preview",
    user_input="Can you show me an example?",
    previous_interaction_id=interaction_id
)

for output in response2.outputs:
    if output.text:
        print(output.text)
```

## Deep Research Agent (Background Task)

Use the `deep-research-pro-preview-12-2025` agent for long-running analysis:

```python
# Start async research
response = client.models.create_interaction(
    model="deep-research-pro-preview-12-2025",
    user_input="Research the latest advances in quantum computing",
    config={"background": True}  # Runs asynchronously
)

interaction_id = response.interaction_id
print(f"Research started. Interaction ID: {interaction_id}")

# Later, poll for results
import time
while True:
    result = client.models.get_interaction(interaction_id)
    if result.state == "COMPLETED":
        for output in result.outputs:
            if output.text:
                print(output.text)
        break
    print("Still researching...")
    time.sleep(5)
```

## Streaming Responses

For real-time output streaming:

```python
response = client.models.create_interaction_stream(
    model="gemini-3.1-pro-preview",
    user_input="Write a Python function to sort a list"
)

for chunk in response:
    for output in chunk.outputs:
        if output.text:
            print(output.text, end="", flush=True)
print()
```

## Function Calling

Define tools for the model to call:

```python
response = client.models.create_interaction(
    model="gemini-3.1-pro-preview",
    user_input="What's the weather in San Francisco?",
    tools=[
        {
            "name": "get_weather",
            "description": "Gets weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                }
            }
        }
    ]
)

# Check for function calls in outputs
for output in response.outputs:
    if output.function_call:
        print(f"Called: {output.function_call.name}")
        print(f"Args: {output.function_call.args}")
```

## Data Model: Output Types

Each interaction returns an `outputs` array with multiple possible types:

- **text** - Plain text response
- **thought** - Internal reasoning (from deep-research agent)
- **function_call** - Tool invocation with arguments
- **image** - Generated or analyzed image
- **code_execution_result** - Output from code interpreter

## Key Differences from generateContent

- **Stateful:** Interactions maintain conversation history via `interaction_id`
- **Async support:** Deep research agents run in background
- **Structured outputs:** Consistent `outputs` array structure
- **No streaming limit:** Interactions support unlimited streaming
- **Cost**: Interactions may be cheaper per token for repeated turns

For simple one-shot requests, see the `gemini-api` skill for basic `generateContent`.

## Storage & Interaction Scope

- Interactions are stored temporarily per request
- Save `interaction_id` to `gws` for long-term persistence
- Interaction-scoped config applies only within that conversation
- Use `system_instruction` at interaction creation for context

## Documentation Lookup

For additional capabilities:
- [Official Interactions API docs](https://ai.google.dev/api/python/google/genai/types/Interaction)
- Check `llms.txt` in this skill directory for model capabilities
- See `gemini-api` skill for basic text/image generation, multimodal understanding

## Cost

Interactions API pricing:
- **Input tokens:** $0.05 per 1M (gemini-3.1-pro)
- **Output tokens:** $0.15 per 1M (gemini-3.1-pro)
- Deep research: Usage-based, may incur higher costs

Costs are the same as the consumer Gemini API.

## Related Skills

- **gemini-api:** Basic text/image generation and multimodal understanding
- **gemini-live-api:** Real-time voice/video streaming
- **vertex-ai-api:** Enterprise Interactions API with Vertex AI

## Example: Content Writer Agent

```python
# Create an interaction for iterative content writing
response = client.models.create_interaction(
    model="gemini-3.1-pro-preview",
    system_instruction="You are a professional content writer.",
    user_input="Write a blog post intro about AI in healthcare"
)

# Get feedback and refine
if response.outputs[0].text:
    draft = response.outputs[0].text

    # Continue with feedback
    response2 = client.models.create_interaction(
        model="gemini-3.1-pro-preview",
        user_input="Make it more engaging and add statistics",
        previous_interaction_id=response.interaction_id
    )

    refined = response2.outputs[0].text
    print(refined)
```
