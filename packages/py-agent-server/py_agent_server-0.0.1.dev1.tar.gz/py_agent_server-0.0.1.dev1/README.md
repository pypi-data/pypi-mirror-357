# MCP Client SDK

[![PyPI version](https://badge.fury.io/py/mcp-client.svg)](https://badge.fury.io/py/mcp-client)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Official Python SDK for the Intelligent Agents Platform (MCP).**

## 🚧 Status: In Planning Phase

This package is currently a placeholder to reserve the name `mcp-client` on PyPI. The official SDK is under active development and will be released soon.

The goal is to provide a seamless and powerful interface to the MCP, enabling developers to optimize LLM usage for cost, speed, and quality effortlessly.

### Vision

```python
# The future of interacting with LLMs:
from mcp_client import MCPClient

client = MCPClient()
result = client.route(
    content="Analyze our Q3 financial report and highlight key risks.",
    task_type="financial_analysis",
    optimize_for="quality"
)
print(result.content)