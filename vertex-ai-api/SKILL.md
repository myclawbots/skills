---
name: vertex_ai_api
description: Use Gemini API on Google Cloud Vertex AI for enterprise workloads. Covers authentication via Application Default Credentials, Express Mode, batch prediction, context caching, model tuning, and all Gen AI SDK features in an enterprise environment.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: ai
tags: [vertex-ai, gemini, google-cloud, enterprise]
suggested_template: general_assistant
---

# Vertex AI API Skill

Use Gemini on Google Cloud Vertex AI for enterprise workloads requiring data residency, compliance controls, batch processing, and model tuning. The Gen AI SDK works seamlessly with Vertex AI.

## When to Use Vertex AI

- Running in Google Cloud environment (Compute Engine, Cloud Run, Cloud Functions)
- Compliance requirements (data residency, regulated data)
- High-volume batch processing or model tuning
- Enterprise billing and access controls
- Need for context caching or cached embeddings

**Core directive:** Always use the Gen AI SDK (google-genai), never legacy Vertex AI SDKs.

## Prerequisites

- Google Cloud project with Vertex AI API enabled
- Authentication: Application Default Credentials (ADC) or Express Mode
- Python 3.9+, Node.js 18+, Go 1.20+, Java 11+, or .NET 6+
- `google-genai >= 1.55.0`

## Authentication: ADC (Recommended)

Use Application Default Credentials for secure, automatic authentication:

```bash
# Set up ADC (run once)
gcloud auth application-default login

# Set Vertex AI environment variables
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1
export GOOGLE_GENAI_USE_VERTEXAI=true
```

```python
import os
from google import genai

# Must set before creating client
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'your-project-id'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'

# Client auto-uses ADC
client = genai.Client()

response = client.models.generate_content(
    model="gemini-3.1-pro",
    contents="Hello from Vertex AI"
)
print(response.text)
```

## Authentication: Express Mode

For quick testing without ADC setup:

```bash
# Get API key from Google AI Studio dashboard
export GOOGLE_API_KEY=your-api-key
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT=your-project-id
```

```python
import os
from google import genai

os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
# Client uses GOOGLE_API_KEY automatically
client = genai.Client()
```

## Vertex AI Models

Use the same model names as the consumer API, available in Vertex AI:

- **gemini-3.1-pro** - Advanced reasoning, 128K context
- **gemini-3-flash** - Fast, efficient, multimodal
- **gemini-3-pro** - Balanced reasoning and speed
- **text-embedding-004** - Embeddings with caching support
- **gemini-3-flash-latest** - Latest flash variant

All Interactions API and Live API models are also available.

## Quick Start: Python

```python
import os
from google import genai

# Configure for Vertex AI
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'my-project'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'

client = genai.Client()

# Generate content
response = client.models.generate_content(
    model="gemini-3.1-pro",
    contents="Explain quantum computing"
)

print(response.text)
```

## Quick Start: JavaScript/TypeScript

```typescript
import { GoogleGenerativeAI } from "@google/genai";

const client = new GoogleGenerativeAI({
  project: process.env.GOOGLE_CLOUD_PROJECT,
  location: process.env.GOOGLE_CLOUD_LOCATION,
  vertexAI: true  // Enable Vertex AI
});

const model = client.getGenerativeModel({
  model: "gemini-3.1-pro"
});

const response = await model.generateContent(
  "Explain quantum computing"
);

console.log(response.text);
```

## Quick Start: Go

```go
package main

import (
    "context"
    "fmt"
    "github.com/google/generative-ai-go/genai"
    "google.golang.org/api/option"
)

func main() {
    ctx := context.Background()

    // Use Application Default Credentials for Vertex AI
    client, err := genai.NewClient(ctx,
        option.WithQuotaProject("my-project"),
    )
    if err != nil {
        panic(err)
    }
    defer client.Close()

    model := client.GenerativeModel("gemini-3.1-pro")
    resp, err := model.GenerateContent(ctx,
        genai.Text("Explain quantum computing"))

    fmt.Println(resp.Candidates[0].Content)
}
```

## Batch Prediction

Process large datasets with Vertex AI Batch API:

```python
import os
from google import genai

os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'my-project'

client = genai.Client()

# Prepare batch request
batch_data = [
    {"contents": "What is AI?"},
    {"contents": "Explain ML"},
    {"contents": "Define deep learning"}
]

# Submit batch job (requires gs:// bucket)
response = client.models.batch_predict(
    model="gemini-3.1-pro",
    requests=batch_data,
    destination_uri="gs://my-bucket/results/"
)

print(f"Batch job: {response.name}")
# Poll for completion
```

## Context Caching

Cache system instructions and large documents to reduce latency/cost:

```python
import os
from google import genai

os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'my-project'

client = genai.Client()

# Create cached system instruction
system_instruction = "You are an expert Python developer..." * 100  # Large prompt

response = client.models.generate_content(
    model="gemini-3.1-pro",
    contents="Debug this code: [large code sample]",
    system_instruction=system_instruction,
    cache_control={"type": "ephemeral"}  # Enable caching
)

print(response.text)
# Subsequent requests within 5 minutes reuse cached content
```

## Model Tuning (Fine-Tuning)

Adapt models to your specific task:

```python
import os
from google import genai

os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'my-project'

client = genai.Client()

# Prepare training data (JSON lines format)
training_data = [
    {"input": "high quality", "output": "excellent"},
    {"input": "poor design", "output": "needs improvement"}
]

# Submit tuning job
response = client.models.create_tuned_model(
    base_model="gemini-3.1-pro",
    training_data=training_data,
    display_name="my-custom-model"
)

print(f"Tuning job: {response.name}")
# Use response.model after job completes
```

## Safety Filters

Vertex AI allows enterprise-grade safety customization:

```python
import os
from google import genai

os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'my-project'

client = genai.Client()

# Configure safety settings
safety_settings = [
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_ONLY_HIGH"
    },
    {
        "category": "HARM_CATEGORY_VIOLENCE",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    }
]

response = client.models.generate_content(
    model="gemini-3.1-pro",
    contents="User query...",
    safety_settings=safety_settings
)

print(response.text)
```

## Access Control

Vertex AI uses Google Cloud Identity & Access Management (IAM):

- **aiplatform.resourceReader** - Read model info
- **aiplatform.admin** - Full resource access
- **aiplatform.batchPredictor** - Submit batch jobs

```bash
# Grant user access to Vertex AI
gcloud projects add-iam-policy-binding my-project \
    --member=user@example.com \
    --role=roles/aiplatform.admin
```

## Embeddings with Caching

Cache embeddings for semantic search:

```python
import os
from google import genai

os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'my-project'

client = genai.Client()

# Embed large document
doc = "Long technical document..." * 100

response = client.models.embed_content(
    model="text-embedding-004",
    content=doc,
    task_type="SEMANTIC_SIMILARITY",
    cache_control={"type": "ephemeral"}
)

embedding = response.embedding
print(f"Embedding dimension: {len(embedding)}")
```

## Cost: Enterprise Pricing

Vertex AI offers enterprise pricing distinct from consumer API:

- Contact Google Cloud sales for volume discounts
- Pay-per-use or commitment discounts
- No additional charges for data residency
- Batch prediction often cheaper per-token

## Related Skills

- **gemini-api:** Consumer Gemini API (non-enterprise)
- **gemini-interactions-api:** Stateful conversations
- **gemini-live-api:** Real-time voice/video streaming

## Troubleshooting

**Error: "ADC not found"**
```bash
gcloud auth application-default login
```

**Error: "Project not set"**
```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1
```

**Error: "Vertex AI API not enabled"**
```bash
gcloud services enable aiplatform.googleapis.com
```

## Example: Enterprise Content Analysis

```python
import os
from google import genai

# Configure Vertex AI
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'enterprise-project'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'

client = genai.Client()

def analyze_document(doc_path):
    """Analyze document using cached system instructions"""

    with open(doc_path, 'r') as f:
        doc_content = f.read()

    # Cache compliance guidelines
    system = """You are a compliance officer. Analyze documents for:
    1. PII exposure
    2. Regulatory violations
    3. Security risks
    """ * 10  # Make it larger to benefit from caching

    response = client.models.generate_content(
        model="gemini-3.1-pro",
        system_instruction=system,
        contents=f"Analyze this document:\n{doc_content}",
        cache_control={"type": "ephemeral"}
    )

    return response.text

if __name__ == "__main__":
    result = analyze_document("document.txt")
    print(result)
```

## Documentation Lookup

- [Vertex AI Gen AI SDK docs](https://cloud.google.com/vertex-ai/docs/generative-ai/start/quickstarts/quickstart-multimodal)
- [Gen AI SDK for Python](https://github.com/google/generative-ai-python)
- [Authentication guide](https://cloud.google.com/docs/authentication/application-default-credentials)
- Check `llms.txt` for Vertex AI-specific model variations
