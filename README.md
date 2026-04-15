# Subscription Tracker Ai

> By [MEOK AI Labs](https://meok.ai) — Track SaaS subscriptions, renewal dates, spending, and find duplicate services. By MEOK AI Labs.

Subscription Tracker AI — track SaaS subscriptions, costs, renewals, and find duplicates. MEOK AI Labs.

## Installation

```bash
pip install subscription-tracker-ai-mcp
```

## Usage

```bash
# Run standalone
python server.py

# Or via MCP
mcp install subscription-tracker-ai-mcp
```

## Tools

### `add_subscription`
Add a subscription to track. Cost in USD/month. Billing cycle: monthly, yearly, quarterly.

**Parameters:**
- `name` (str)
- `cost_monthly` (float)
- `billing_cycle` (str)
- `renewal_date` (str)
- `category` (str)

### `get_total_spend`
Calculate total subscription spend. Period: monthly, yearly, daily.

**Parameters:**
- `period` (str)

### `list_subscriptions`
List all tracked subscriptions. Sort by: cost, name, category, date.

**Parameters:**
- `active_only` (bool)
- `sort_by` (str)

### `find_duplicates`
Find potentially duplicate or overlapping subscriptions in the same category.


## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## Links

- **Website**: [meok.ai](https://meok.ai)
- **GitHub**: [CSOAI-ORG/subscription-tracker-ai-mcp](https://github.com/CSOAI-ORG/subscription-tracker-ai-mcp)
- **PyPI**: [pypi.org/project/subscription-tracker-ai-mcp](https://pypi.org/project/subscription-tracker-ai-mcp/)

## License

MIT — MEOK AI Labs
