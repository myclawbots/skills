# Search tools

Exa AI search engine.

## Exa AI search

A high-quality AI search engine for technical documentation, official examples, and relevant web pages.

```bash
mcporter call exa.web_search_exa query="query" numResults=5
mcporter call exa.web_search_exa query="library API code example" numResults=5
```

### Use cases

| Use case | Parameters |
|-----|------|
| Web search | `web_search_exa(query: "...", numResults: 5)` |
| Technical/code resources | `web_search_exa(query: "framework name API example", numResults: 5)` |

> Exa MCP's `get_code_context_exa` is deprecated and is not registered by default. Use
> `web_search_exa` for code questions too; for precise searches within repositories,
> use the GitHub search commands in `dev.md`.

### Features

- Strong results for English-language content and technical documentation
- Query terms can target official documentation and code examples
- High-quality results

## Comparison with other search tools

| Tool | Source | Use case |
|-----|------|---------|
| Exa | agent-reach | English-language/technical/code search |
| Zhipu Search | my-mcp-tools | Chinese-language search |
| GitHub search | agent-reach (dev.md) | Repository/code search |
