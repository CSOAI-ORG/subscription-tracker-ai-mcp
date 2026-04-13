from mcp.server.fastmcp import FastMCP

mcp = FastMCP("subscription-tracker")

SUBSCRIPTIONS = []

@mcp.tool()
def add_subscription(name: str, cost: float, cycle: str, category: str = "general") -> dict:
    """Add a subscription. Cycle: monthly or yearly."""
    if cycle not in ("monthly", "yearly"):
        return {"error": "Cycle must be monthly or yearly"}
    sub = {"name": name, "cost": cost, "cycle": cycle, "category": category}
    SUBSCRIPTIONS.append(sub)
    return {"added": sub, "total_tracked": len(SUBSCRIPTIONS)}

@mcp.tool()
def list_subscriptions(category: str = None) -> dict:
    """List subscriptions, optionally filtered by category."""
    subs = [s for s in SUBSCRIPTIONS if category is None or s["category"] == category]
    return {"subscriptions": subs, "count": len(subs)}

@mcp.tool()
def calculate_totals() -> dict:
    """Calculate monthly and yearly totals."""
    monthly = 0.0
    yearly = 0.0
    for s in SUBSCRIPTIONS:
        if s["cycle"] == "monthly":
            monthly += s["cost"]
            yearly += s["cost"] * 12
        else:
            yearly += s["cost"]
            monthly += s["cost"] / 12
    return {
        "monthly_total": round(monthly, 2),
        "yearly_total": round(yearly, 2),
        "subscription_count": len(SUBSCRIPTIONS),
    }

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
