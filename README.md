<div align="center">

# Gardening Ai MCP

**Gardening AI MCP Server - Horticulture Intelligence**

[![PyPI](https://img.shields.io/pypi/v/meok-gardening-ai-mcp)](https://pypi.org/project/meok-gardening-ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Gardening AI MCP Server - Horticulture Intelligence
Built by MEOK AI Labs | https://meok.ai

Plant identification, watering schedules, soil analysis,
companion planting, and pest diagnosis.

## Tools

| Tool | Description |
|------|-------------|
| `identify_plant` | Identify a plant from its characteristics and get care info. |
| `generate_watering_schedule` | Generate a watering schedule for your plants. |
| `analyze_soil` | Analyze soil conditions and get amendment recommendations. |
| `companion_planting` | Check companion planting compatibility for a group of plants. |
| `diagnose_pest` | Diagnose garden pests from observed symptoms and get treatment plans. |

## Installation

```bash
pip install meok-gardening-ai-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "gardening-ai": {
      "command": "python",
      "args": ["-m", "meok_gardening_ai_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 5 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
