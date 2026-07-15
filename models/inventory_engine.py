def calculate_inventory_metrics(
    forecast_demand,
    current_inventory,
    lead_time_days=7,
    avg_daily_demand=0,
    outstanding_orders=0
):

    # Safety Stock
    safety_stock = avg_daily_demand * 7

    # Lead Time Demand
    lead_time_demand = avg_daily_demand * lead_time_days

    # Reorder Point
    reorder_point = (
        lead_time_demand +
        safety_stock
    )

    # Replenishment Qty

    replenish_qty = (
        forecast_demand +
        safety_stock -
        current_inventory -
        outstanding_orders
    )

    replenish_qty = max(
        replenish_qty,
        0
    )

    return {
        "Safety Stock": round(safety_stock),
        "Lead Time Demand": round(lead_time_demand),
        "ROP": round(reorder_point),
        "Replenishment Qty": round(replenish_qty)
    }