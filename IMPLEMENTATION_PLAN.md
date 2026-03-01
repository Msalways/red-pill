# ChartGen SDK - Implementation Plan

## Overview

A generic, AI-powered SDK that transforms any JSON data into chart-ready data using LLM for schema inference and Polars for data transformation.

## Problem Statement

- Developers integrate with 3rd party services (Composio, Zapier, etc.) but don't know data schema
- Writing custom visualization code for each provider's unique schema is unsustainable
- The boom of AI/LLM makes this possible generically

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER APPLICATION                               │
│                                                                          │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────────────────────┐ │
│   │   RAW DATA  │    │    PROMPT  │    │         SPEC (stored)       │ │
│   │  (any JSON) │    │  "show me  │    │                             │ │
│   │  from any   │    │  tickets   │    │                             │ │
│   │  provider   │    │  by status │    │                             │ │
│   └──────┬──────┘    └──────┬──────┘    └─────────────────────────────┘ │
│          │                  │                       ▲                    │
│          │                  │                       │                    │
│          ▼                  ▼                       │                    │
│   ╔═════════════════════════════════════════════════╧═══════════════╗   │
│   ║                      CHARTGEN SDK                       ║          │
│   ╠══════════════════════════════════════════════════════════════════╣  │
│   ║                                                                   ║  │
│   ║  PHASE 1              PHASE 2              PHASE 3              ║  │
│   ║  ┌──────────┐    ┌─────────────┐    ┌──────────────────┐       ║  │
│   ║  │Processor │    │   AGENTS    │    │    Executor      │       ║  │
│   ║  │(Flatten) │───▶│  (LLM Loop) │───▶│   (Polars)       │       ║  │
│   ║  └──────────┘    └─────────────┘    └──────────────────┘       ║  │
│   ║        │               │                     │                    ║  │
│   ║        │               │    ┌────────────────┘                    ║  │
│   ║        │               ▼    ▼                                     ║  │
│   ║        │         ┌─────────────────────────────────┐             ║  │
│   ║        │         │  Intent Parser + Spec Generator │             ║  │
│   ║        │         │           (Agent 1)            │             ║  │
│   ║        │         └─────────────────────────────────┘             ║  │
│   ║        │               │                                          ║  │
│   ║        │         ┌─────────────┐                                 ║  │
│   ║        │         │  Validator  │                                 ║  │
│   ║        └────────▶│   (Agent 2) │                                 ║  │
│   ║                  └─────────────┘                                 ║  │
│   ║                                                                   ║  │
│   ╚══════════════════════════════════════════════════════════════════╝  │
│                                    │                                    │
│                                    ▼                                    │
│                         ┌──────────────────┐                           │
│                         │   CHART-READY    │                           │
│                         │       DATA        │                           │
│                         │  (any chart lib)  │                           │
│                         └──────────────────┘                           │
└─────────────────────────────────────────────────────────────────────────┘
```

## Three Phases

### Phase 1: Data Processor

**Purpose**: Flatten nested JSON into table format + generate data profile for LLM

**Input**:
```json
{"users": [{"name": "John", "address": {"city": "NYC"}}]}
[{"id": 1, "items": [{"product": "A", "qty": 2}]}]
```

**Output**:
```json
{
  "flat_data": [
    {"users.name": "John", "users.address.city": "NYC"},
    {"id": 1, "items.product": "A", "items.qty": 2, "_row_index": 0}
  ],
  "profile": {
    "columns": {
      "users.name": {"type": "string", "unique_count": 50, "sample": ["John", "Jane"]},
      "users.address.city": {"type": "string", "unique_count": 20},
      "id": {"type": "int", "min": 1, "max": 1000},
      "items.product": {"type": "string"},
      "items.qty": {"type": "int", "min": 1, "max": 100}
    },
    "row_count": 1000,
    "flattened_row_count": 2500
  }
}
```

**Key Features**:
- Flatten nested objects with dot-notation keys
- Explode arrays into multiple rows (with index tracking)
- Preserve data types
- Generate column profile (type, unique count, min/max, samples)

**Data Handling Strategy**:
- For LLM: Flatten only sample (50-200 rows)
- For Executor: Use Polars Lazy API (no full flatten upfront)

---

### Phase 2: LLM Agents

**Purpose**: Analyze data + prompt → generate chart spec with runtime params

#### Agent 1: Intent Parser + Spec Generator (Combined)

**Input**:
- User prompt: "show me tickets by status for last 24 hours"
- Data profile from Phase 1

**Output**:
```json
{
  "spec": {
    "version": "1.0",
    "chartType": "bar",
    "xAxis": {"field": "status", "label": "Status", "type": "categorical"},
    "yAxis": {"field": "count", "label": "Tickets", "aggregation": "count"},
    "series": {"field": "priority", "label": "Priority"},
    "options": {"title": "Tickets by Status", "stacked": false}
  },
  "params": {
    "timeField": "created_at",
    "filters": [
      {"field": "created_at", "operator": "gte", "value": "now-24h"}
    ]
  }
}
```

#### Agent 2: Validator

**Purpose**: Validate spec + dry-run with sample data

**Logic**:
1. Validate spec syntax against schema
2. Dry-run with sample data using Polars
3. If fail → retry Agent 1 (max 3 attempts)
4. Return validated spec or raise error

---

### Phase 3: Executor

**Purpose**: Transform full data using spec → chart-ready output

**Input**:
- Stored spec (with params)
- Full data (potentially huge)

**Output**:
```json
{
  "data": [
    {"x": "open", "y": 150, "series": "high"},
    {"x": "open", "y": 80, "series": "medium"},
    {"x": "closed", "y": 200, "series": "high"}
  ],
  "metadata": {
    "chartType": "bar",
    "xAxis": {"field": "status", "label": "Status"},
    "yAxis": {"field": "count", "label": "Tickets"},
    "series": {"field": "priority"}
  }
}
```

**Polars Operations**:
1. Apply time filters (if timeField specified)
2. Apply other filters
3. Group by (xAxis + series)
4. Aggregate (count/sum/avg as specified)
5. Sort and limit
6. Transform to chart-ready format

---

## Supported Chart Types

| Type | Description | X-Axis | Y-Axis | Series |
|------|-------------|--------|--------|--------|
| bar | Bar chart | categorical | quantitative | optional |
| line | Line chart | time/categorical | quantitative | optional |
| pie | Pie chart | categorical | quantitative | - |
| scatter | Scatter plot | quantitative | quantitative | optional |
| area | Area chart | time/categorical | quantitative | optional |

---

## Spec Format

```json
{
  "version": "1.0",
  "chartType": "bar",
  "xAxis": {
    "field": "status",
    "label": "Status",
    "type": "categorical"
  },
  "yAxis": {
    "field": "count",
    "label": "Tickets",
    "aggregation": "count",
    "aggregationField": "id"
  },
  "series": {
    "field": "priority",
    "label": "Priority"
  },
  "options": {
    "title": "Tickets by Status",
    "stacked": false,
    "orientation": "vertical"
  },
  "params": {
    "timeField": "created_at",
    "filters": [
      {"field": "status", "operator": "in", "value": ["open", "closed"]}
    ],
    "limit": 100,
    "sort": {"field": "count", "direction": "desc"}
  }
}
```

---

## Provider Abstraction

**Supported**: OpenAI (custom baseURL), Anthropic

**Interface**:
```python
class LLMProvider(Protocol):
    def generate(self, prompt: str, schema: dict) -> dict: ...
    def generate_with_structured_output(self, prompt: str, schema: type) -> dict: ...
```

**Factory**:
```python
def get_provider(name: str, **kwargs) -> LLMProvider:
    if name == "openai": return OpenAIProvider(**kwargs)
    if name == "anthropic": return AnthropicProvider(**kwargs)
    raise ValueError(f"Unknown provider: {name}")
```

---

## SDK Interface

### Python SDK

```python
from chartgen import ChartGen

# Initialize with builder pattern
cg = (
    ChartGen()
    .provider("openai")
    .base_url("https://api.openai.com/v1")  # optional, for custom endpoints
    .api_key(os.getenv("OPENAI_API_KEY"))
    .model("gpt-4o")
    .max_retries(3)
    .timeout(60)
    .build()
)

# Generate spec (one-time)
result = cg.generate_spec(
    data=sample_data,
    prompt="show me tickets by status with priority breakdown"
)
# result: {spec, profile}

# Store result.spec

# Execute (many times)
chart_data = cg.execute(
    spec=stored_spec,
    data=full_data
)
# chart_data: {data: [...], metadata: {...}}

# Async variant for huge datasets
async for chunk in cg.execute_async(
    spec=stored_spec,
    data=large_dataset,
    batch_size=10000
):
    process(chunk)
```

### JS SDK (Node.js)

```typescript
import { ChartGen } from '@chartgen/chartgen';

const cg = new ChartGen({
  provider: 'openai',
  apiKey: process.env.OPENAI_API_KEY,
  model: 'gpt-4o'
});

// Generate spec
const { spec, profile } = await cg.generateSpec({
  data: sampleData,
  prompt: 'show me tickets by status'
});

// Execute
const chartData = await cg.execute({
  spec: storedSpec,
  data: fullData
});
```

---

## Project Structure

```
packages/
├── python/
│   ├── chartgen/
│   │   ├── __init__.py
│   │   ├── client.py              # Main ChartGen client
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   └── builder.py          # Fluent config builder
│   │   ├── processor/
│   │   │   ├── __init__.py
│   │   │   ├── flattener.py        # Flatten nested JSON
│   │   │   └── profiler.py         # Generate data profile
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # Base agent class
│   │   │   ├── intent_spec_agent.py # Agent 1 (Intent + Spec)
│   │   │   └── validator.py        # Agent 2 (Validation)
│   │   ├── executor/
│   │   │   ├── __init__.py
│   │   │   ├── polars_executor.py  # Phase 3
│   │   │   └── async_executor.py   # Async variant
│   │   ├── providers/
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # Provider interface
│   │   │   ├── openai.py
│   │   │   ├── anthropic.py
│   │   │   └── factory.py          # Provider factory
│   │   ├── spec/
│   │   │   ├── __init__.py
│   │   │   ├── schema.py           # Pydantic models
│   │   │   └── validators.py       # Spec validation
│   │   └── prompts/
│   │       ├── __init__.py
│   │       ├── intent_spec.py      # Prompt templates
│   │       └── validation.py
│   ├── pyproject.toml
│   └── README.md
│
└── js/
    ├── packages/
    │   ├── chartgen-core/           # Shared types (TypeScript)
    │   │   ├── index.ts
    │   │   ├── spec.ts
    │   │   └── schema.ts
    │   │
    │   └── chartgen/                # Node.js SDK
    │       ├── index.ts
    │       ├── client.ts
    │       ├── config.ts
    │       ├── processor/           # Flatten + profile
    │       ├── executor/            # Polars WASM executor
    │       └── providers/          # HTTP client to Python SDK
    │
    ├── package.json
    └── README.md
```

---

## Implementation Order

### Phase 1: Core Infrastructure
1. Project setup (Python + JS)
2. Spec schema (Pydantic + TypeScript)
3. Config builder pattern
4. Provider abstraction (OpenAI + Anthropic)

### Phase 2: Data Processor
1. JSON flattener
2. Data profiler
3. Sample extraction logic

### Phase 3: LLM Agents
1. Prompt templates
2. Intent Parser + Spec Generator agent
3. Validator agent
4. Retry logic (max 3)

### Phase 4: Executor
1. Polars executor (sync)
2. Filter application (timeRange, filters)
3. GroupBy + aggregation
4. Async executor variant

### Phase 5: Integration
1. Main client (generate_spec + execute)
2. Error handling
3. Tests

### Phase 6: JS SDK
1. Shared types
2. Polars WASM integration
3. HTTP client wrapper (optional)

---

## Error Handling

| Scenario | Strategy |
|----------|----------|
| Invalid JSON data | Raise with field causing issue |
| LLM timeout | Retry with backoff (max 3) |
| Invalid spec from LLM | Retry spec generation (max 3) |
| Spec validation fails | Retry with corrected prompt |
| Executor transformation fails | Raise with details |
| Data lacks required fields | Raise with missing fields |

---

## Future Enhancements

- Custom spec parameters (override filters at runtime)
- Caching layer for specs
- More chart types (heatmap, treemap, etc.)
- Additional LLM providers (Ollama, Gemini)
- Browser SDK via HTTP calls to Python backend
- MCP integration for external tools
