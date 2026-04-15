#!/usr/bin/env python3
"""Subscription Tracker AI — track SaaS subscriptions, costs, renewals, and find duplicates. MEOK AI Labs."""
import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access
from persistence import ServerStore

import json
from datetime import datetime, timezone
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

_store = ServerStore("subscription-tracker-ai")

FREE_DAILY_LIMIT = 15
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day"})
    _usage[c].append(now); return None

# Category mapping for duplicate detection
_CATEGORIES = {
    "streaming": ["netflix", "hulu", "disney", "hbo", "paramount", "peacock", "apple tv", "prime video", "crunchyroll"],
    "music": ["spotify", "apple music", "tidal", "youtube music", "amazon music", "deezer"],
    "cloud_storage": ["dropbox", "google drive", "onedrive", "icloud", "box"],
    "productivity": ["notion", "todoist", "asana", "monday", "clickup", "trello"],
    "ai_tools": ["chatgpt", "claude", "midjourney", "copilot", "jasper", "grammarly"],
    "design": ["figma", "canva", "adobe", "sketch", "affinity"],
    "dev_tools": ["github", "gitlab", "vercel", "netlify", "railway", "heroku"],
    "vpn": ["nordvpn", "expressvpn", "surfshark", "protonvpn", "mullvad"],
    "fitness": ["peloton", "strava", "fitbit", "myfitnesspal", "headspace", "calm"],
    "news": ["nyt", "washington post", "wsj", "economist", "substack", "medium"],
}

mcp = FastMCP("subscription-tracker-ai", instructions="Track SaaS subscriptions, renewal dates, spending, and find duplicate services. By MEOK AI Labs.")


@mcp.tool()
def add_subscription(name: str, cost_monthly: float, billing_cycle: str = "monthly", renewal_date: str = "", category: str = "", api_key: str = "") -> str:
    """Add a subscription to track. Cost in USD/month. Billing cycle: monthly, yearly, quarterly."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err
    if cost_monthly < 0:
        return json.dumps({"error": "Cost cannot be negative"})
    billing_cycle = billing_cycle.lower()
    if billing_cycle not in ("monthly", "yearly", "quarterly"):
        return json.dumps({"error": "Billing cycle must be monthly, yearly, or quarterly"})
    # Auto-detect category if not provided
    if not category:
        name_lower = name.lower()
        for cat, services in _CATEGORIES.items():
            if any(svc in name_lower for svc in services):
                category = cat
                break
        if not category:
            category = "other"
    # Calculate effective monthly cost
    if billing_cycle == "yearly":
        effective_monthly = cost_monthly  # user provides monthly equivalent
    elif billing_cycle == "quarterly":
        effective_monthly = cost_monthly
    else:
        effective_monthly = cost_monthly
    sub = {
        "id": _store.list_length("subscriptions") + 1,
        "name": name,
        "cost_monthly": round(cost_monthly, 2),
        "billing_cycle": billing_cycle,
        "category": category,
        "renewal_date": renewal_date or "not set",
        "added_at": datetime.now(timezone.utc).isoformat(),
        "active": True,
    }
    _store.append("subscriptions", sub)
    all_subs = _store.list("subscriptions")
    total_monthly = sum(s["cost_monthly"] for s in all_subs if s["active"])
    return json.dumps({
        "added": sub,
        "total_subscriptions": sum(1 for s in _subscriptions if s["active"]),
        "total_monthly_spend": round(total_monthly, 2),
    }, indent=2)


@mcp.tool()
def get_total_spend(period: str = "monthly", api_key: str = "") -> str:
    """Calculate total subscription spend. Period: monthly, yearly, daily."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err
    active = [s for s in _store.list("subscriptions") if s["active"]]
    if not active:
        return json.dumps({"message": "No active subscriptions tracked yet.", "total": 0})
    monthly_total = sum(s["cost_monthly"] for s in active)
    period = period.lower()
    multipliers = {"daily": 1 / 30.44, "monthly": 1, "yearly": 12}
    if period not in multipliers:
        return json.dumps({"error": "Period must be daily, monthly, or yearly"})
    amount = monthly_total * multipliers[period]
    # Category breakdown
    by_category: dict[str, float] = defaultdict(float)
    for s in active:
        by_category[s["category"]] += s["cost_monthly"] * multipliers[period]
    sorted_cats = sorted(by_category.items(), key=lambda x: x[1], reverse=True)
    # Most expensive subscription
    most_expensive = max(active, key=lambda s: s["cost_monthly"])
    return json.dumps({
        "period": period,
        "total_spend": round(amount, 2),
        "currency": "USD",
        "active_subscriptions": len(active),
        "by_category": {k: round(v, 2) for k, v in sorted_cats},
        "most_expensive": {"name": most_expensive["name"], "cost_monthly": most_expensive["cost_monthly"]},
        "average_per_subscription": round(amount / len(active), 2),
    }, indent=2)


@mcp.tool()
def list_subscriptions(active_only: bool = True, sort_by: str = "cost", api_key: str = "") -> str:
    """List all tracked subscriptions. Sort by: cost, name, category, date."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err
    all_subs = _store.list("subscriptions")
    subs = all_subs if not active_only else [s for s in all_subs if s["active"]]
    if not subs:
        return json.dumps({"message": "No subscriptions found.", "subscriptions": []})
    sort_keys = {
        "cost": lambda s: s["cost_monthly"],
        "name": lambda s: s["name"].lower(),
        "category": lambda s: s["category"],
        "date": lambda s: s["added_at"],
    }
    sort_fn = sort_keys.get(sort_by.lower(), sort_keys["cost"])
    reverse = sort_by.lower() == "cost"
    sorted_subs = sorted(subs, key=sort_fn, reverse=reverse)
    total = sum(s["cost_monthly"] for s in sorted_subs)
    return json.dumps({
        "subscriptions": sorted_subs,
        "count": len(sorted_subs),
        "total_monthly": round(total, 2),
        "total_yearly": round(total * 12, 2),
        "sorted_by": sort_by,
    }, indent=2)


@mcp.tool()
def find_duplicates(api_key: str = "") -> str:
    """Find potentially duplicate or overlapping subscriptions in the same category."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err
    active = [s for s in _store.list("subscriptions") if s["active"]]
    if len(active) < 2:
        return json.dumps({"message": "Need at least 2 subscriptions to check for duplicates.", "duplicates": []})
    # Group by category
    by_cat: dict[str, list[dict]] = defaultdict(list)
    for s in active:
        by_cat[s["category"]].append(s)
    duplicates = []
    potential_savings = 0.0
    for category, subs in by_cat.items():
        if len(subs) > 1 and category != "other":
            costs = sorted(subs, key=lambda s: s["cost_monthly"])
            savings = sum(s["cost_monthly"] for s in costs[:-1])  # keep the most expensive, save the rest
            potential_savings += savings
            duplicates.append({
                "category": category,
                "services": [{"name": s["name"], "cost_monthly": s["cost_monthly"]} for s in subs],
                "count": len(subs),
                "potential_monthly_savings": round(savings, 2),
                "suggestion": f"You have {len(subs)} {category} services. Consider consolidating to save ${savings:.2f}/month.",
            })
    return json.dumps({
        "duplicates_found": len(duplicates),
        "overlapping_categories": duplicates,
        "total_potential_savings_monthly": round(potential_savings, 2),
        "total_potential_savings_yearly": round(potential_savings * 12, 2),
        "tip": "Review overlapping services and keep only the ones you actively use." if duplicates else "No obvious duplicates found!",
    }, indent=2)


if __name__ == "__main__":
    mcp.run()
