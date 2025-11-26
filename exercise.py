"""
Capital Gains Tax Calculator (CLI)

This module processes stock market buy/sell operations and computes
the tax owed for each transaction according to the rules defined in
the take-home challenge. It supports weighted average price updates,
loss accumulation, and correct tax application based on thresholds.
"""

import sys
import json

TAX_RATE = 0.20
TAX_FREE_THRESHOLD = 20000.00


def round2(value):
    """Round a float to two decimal places."""
    return round(value, 2)


def process_operations(operations):
    """
    Process a list of buy/sell operations and compute the tax for each one.

    Args:
        operations (list[dict]): Stock operations as parsed JSON objects.
            Contains "operation", "unit-cost", and "quantity" keys.

    Returns:
        list[dict]: A list of {"tax": float} entries matching each operation.
    """
    quantity = 0.0
    weighted_avg = 0.0
    accumulated_loss = 0.0

    taxes = []

    for op in operations:
        kind = op["operation"]
        unit_cost = float(op["unit-cost"])
        qty = float(op["quantity"])

        if kind == "buy":
            quantity, weighted_avg, tax = handle_buy(quantity, weighted_avg, qty, unit_cost)
        elif kind == "sell":
            quantity, accumulated_loss, tax = handle_sell(
                quantity, weighted_avg, accumulated_loss, qty, unit_cost
            )

        taxes.append({"tax": tax})

    return taxes


def handle_buy(quantity, weighted_avg, qty, unit_cost):
    """
    Handle a buy operation: update the weighted average price and total quantity.

    Returns:
        tuple: (new_quantity, new_weighted_avg, tax_for_this_operation)
    """
    total_old = quantity * weighted_avg
    total_new = qty * unit_cost
    quantity_new = quantity + qty

    if quantity_new > 0:
        weighted_avg = round2((total_old + total_new) / quantity_new)
    else:
        weighted_avg = 0.0

    return quantity_new, weighted_avg, 0.0


def handle_sell(quantity, weighted_avg, accumulated_loss, qty, unit_cost):
    """
    Handle a sell operation: compute profit or loss, update accumulated losses,
    and calculate taxes when applicable.

    Returns:
        tuple: (updated_quantity, updated_accumulated_loss, tax)
    """
    total_amount = unit_cost * qty
    gross_profit = (unit_cost - weighted_avg) * qty

    if gross_profit < 0:
        # Loss always accumulates regardless of total_amount threshold
        accumulated_loss += -gross_profit
        tax = 0.0
    else:
        tax, accumulated_loss = calculate_tax_for_profit(
            total_amount, gross_profit, accumulated_loss
        )

    return quantity - qty, accumulated_loss, tax


def calculate_tax_for_profit(total_amount, gross_profit, accumulated_loss):
    """
    Determine whether a profitable sell is taxable and compute the correct tax.

    Rules:
      - No tax if total sell amount <= 20,000.
      - Otherwise, deduct accumulated losses before applying tax.

    Returns:
        tuple: (tax, updated_accumulated_loss)
    """
    if total_amount <= TAX_FREE_THRESHOLD:
        return 0.0, accumulated_loss

    net_profit, updated_loss = apply_accumulated_loss(gross_profit, accumulated_loss)
    tax = compute_tax(net_profit)
    return tax, updated_loss


def apply_accumulated_loss(gross_profit, accumulated_loss):
    """
    Apply accumulated losses to reduce gross profit.

    Returns:
        tuple: (net_profit_after_deduction, updated_accumulated_loss)
    """
    if accumulated_loss >= gross_profit:
        return 0.0, accumulated_loss - gross_profit
    return gross_profit - accumulated_loss, 0.0


def compute_tax(net_profit):
    """
    Compute tax (20%) for a net profit greater than zero.

    Returns:
        float: tax amount
    """
    if net_profit > 0:
        return round2(net_profit * TAX_RATE)
    return 0.0


def main():
    """
    CLI entrypoint: reads JSON operations from stdin line by line,
    processes each batch, and prints the corresponding tax list.
    """
    for line in sys.stdin:
        line = line.strip()
        if not line:
            break

        operations = json.loads(line)
        taxes = process_operations(operations)
        print(json.dumps(taxes))


if __name__ == "__main__":
    main()
