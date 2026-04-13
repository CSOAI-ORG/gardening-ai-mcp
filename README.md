# Gardening AI MCP Server

**Horticulture Intelligence**

Built by [MEOK AI Labs](https://meok.ai)

---

An MCP server for gardeners and horticulturists. Identify plants, generate watering schedules adjusted for climate and season, analyze soil conditions, check companion planting compatibility, and diagnose pests with organic treatment plans.

## Tools

| Tool | Description |
|------|-------------|
| `identify_plant` | Identify plants from characteristics and get full care profiles |
| `generate_watering_schedule` | Climate and season-adjusted watering schedules |
| `analyze_soil` | Soil analysis with amendment recommendations and plant compatibility |
| `companion_planting` | Check companion planting compatibility for plant groups |
| `diagnose_pest` | Diagnose garden pests from symptoms with organic and chemical treatments |

## Quick Start

```bash
pip install gardening-ai-mcp
```

### Claude Desktop

```json
{
  "mcpServers": {
    "gardening-ai": {
      "command": "python",
      "args": ["-m", "server"],
      "cwd": "/path/to/gardening-ai-mcp"
    }
  }
}
```

### Direct Usage

```bash
python server.py
```

## Rate Limits

| Tier | Requests/Hour |
|------|--------------|
| Free | 60 |
| Pro | 5,000 |

## License

MIT - see [LICENSE](LICENSE)

---

*Part of the MEOK AI Labs MCP Marketplace*
