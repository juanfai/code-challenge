import json

import pytest

from exercise import process_operations, round2


def run_ops(json_str):
    """Helper: parses JSON string and runs process_operations()."""
    operations = json.loads(json_str)
    return process_operations(operations)


def test_case_1():
    """Tests simple buy and small sells with no taxable events (all under 20k)."""
    ops = """
    [
        {"operation":"buy", "unit-cost":10.00, "quantity":100},
        {"operation":"sell", "unit-cost":15.00, "quantity":50},
        {"operation":"sell", "unit-cost":15.00, "quantity":50}
    ]
    """
    result = run_ops(ops)
    assert result == [
        {"tax": 0.0},
        {"tax": 0.0},
        {"tax": 0.0}
    ]


def test_case_2():
    """Tests profit taxable event followed by a loss event."""
    ops = """
    [
        {"operation":"buy", "unit-cost":10.00, "quantity":10000},
        {"operation":"sell", "unit-cost":20.00, "quantity":5000},
        {"operation":"sell", "unit-cost":5.00, "quantity":5000}
    ]
    """
    result = run_ops(ops)
    assert result == [
        {"tax": 0.0},
        {"tax": 10000.0},
        {"tax": 0.0}
    ]


def test_case_3():
    """Tests loss accumulation followed by partial profit that becomes taxable after loss deduction."""
    ops = """
    [
        {"operation":"buy", "unit-cost":10.00, "quantity":10000},
        {"operation":"sell", "unit-cost":5.00, "quantity":5000},
        {"operation":"sell", "unit-cost":20.00, "quantity":3000}
    ]
    """
    result = run_ops(ops)
    assert result == [
        {"tax": 0.0},
        {"tax": 0.0},
        {"tax": 1000.0}
    ]


def test_case_4():
    """Tests weighted average recalculation leading to a break-even sell (no profit, no tax)."""
    ops = """
    [
        {"operation":"buy", "unit-cost":10.00, "quantity":10000},
        {"operation":"buy", "unit-cost":25.00, "quantity":5000},
        {"operation":"sell", "unit-cost":15.00, "quantity":10000}
    ]
    """
    result = run_ops(ops)
    assert result == [
        {"tax": 0.0},
        {"tax": 0.0},
        {"tax": 0.0}
    ]


def test_case_5():
    """Tests multiple buys and sells where the first sell breaks even and the second generates taxable profit."""
    ops = """
    [
        {"operation":"buy", "unit-cost":10.00, "quantity":10000},
        {"operation":"buy", "unit-cost":25.00, "quantity":5000},
        {"operation":"sell", "unit-cost":15.00, "quantity":10000},
        {"operation":"sell", "unit-cost":25.00, "quantity":5000}
    ]
    """
    result = run_ops(ops)
    assert result == [
        {"tax": 0.0},
        {"tax": 0.0},
        {"tax": 0.0},
        {"tax": 10000.0}
    ]


def test_case_6():
    """Tests large initial loss, multiple subsequent sells consuming the loss, ending with a taxable profit."""
    ops = """
    [
        {"operation":"buy", "unit-cost":10.00, "quantity":10000},
        {"operation":"sell", "unit-cost":2.00, "quantity":5000},
        {"operation":"sell", "unit-cost":20.00, "quantity":2000},
        {"operation":"sell", "unit-cost":20.00, "quantity":2000},
        {"operation":"sell", "unit-cost":25.00, "quantity":1000}
    ]
    """
    result = run_ops(ops)
    assert result == [
        {"tax": 0.0},
        {"tax": 0.0},
        {"tax": 0.0},
        {"tax": 0.0},
        {"tax": 3000.0}
    ]


def test_case_7():
    """Tests complex sequence with losses, multiple sells, a new buy resetting average, and new profit deductions."""
    ops = """
    [
        {"operation":"buy", "unit-cost":10.00, "quantity":10000},
        {"operation":"sell", "unit-cost":2.00, "quantity":5000},
        {"operation":"sell", "unit-cost":20.00, "quantity":2000},
        {"operation":"sell", "unit-cost":20.00, "quantity":2000},
        {"operation":"sell", "unit-cost":25.00, "quantity":1000},
        {"operation":"buy", "unit-cost":20.00, "quantity":10000},
        {"operation":"sell", "unit-cost":15.00, "quantity":5000},
        {"operation":"sell", "unit-cost":30.00, "quantity":4350},
        {"operation":"sell", "unit-cost":30.00, "quantity":650}
    ]
    """
    result = run_ops(ops)
    assert result == [
        {"tax": 0.0},
        {"tax": 0.0},
        {"tax": 0.0},
        {"tax": 0.0},
        {"tax": 3000.0},
        {"tax": 0.0},
        {"tax": 0.0},
        {"tax": 3700.0},
        {"tax": 0.0}
    ]


def test_case_8():
    """Tests a scenario with large profits on both sells, each generating taxable gains."""
    ops = """
    [
        {"operation":"buy", "unit-cost":10.00, "quantity":10000},
        {"operation":"sell", "unit-cost":50.00, "quantity":10000},
        {"operation":"buy", "unit-cost":20.00, "quantity":10000},
        {"operation":"sell", "unit-cost":50.00, "quantity":10000}
    ]
    """
    result = run_ops(ops)
    assert result == [
        {"tax": 0.0},
        {"tax": 80000.0},
        {"tax": 0.0},
        {"tax": 60000.0}
    ]


def test_case_9():
    """Tests mixed high-value buys, partial loss, non-taxable sells under 20k, and final taxed profits."""
    ops = """
    [
        {"operation":"buy", "unit-cost":5000.00, "quantity":10},
        {"operation":"sell", "unit-cost":4000.00, "quantity":5},
        {"operation":"buy", "unit-cost":15000.00, "quantity":5},
        {"operation":"buy", "unit-cost":4000.00, "quantity":2},
        {"operation":"buy", "unit-cost":23000.00, "quantity":2},
        {"operation":"sell", "unit-cost":20000.00, "quantity":1},
        {"operation":"sell", "unit-cost":12000.00, "quantity":10},
        {"operation":"sell", "unit-cost":15000.00, "quantity":3}
    ]
    """
    result = run_ops(ops)
    assert result == [
        {"tax": 0.0},
        {"tax": 0.0},
        {"tax": 0.0},
        {"tax": 0.0},
        {"tax": 0.0},
        {"tax": 0.0},
        {"tax": 1000.0},
        {"tax": 2400.0}
    ]


def test_operations_must_be_list():
    with pytest.raises(ValueError, match="operations must be a list"):
        process_operations({"operation": "buy"})


def test_operations_must_not_be_empty():
    with pytest.raises(ValueError, match="operations must not be empty"):
        process_operations([])


def test_invalid_operation_kind():
    ops = """
    [
        {"operation":"hold", "unit-cost":10.00, "quantity":5}
    ]
    """
    with pytest.raises(ValueError, match="Unsupported operation 'hold'"):
        run_ops(ops)


def test_non_numeric_quantity():
    ops = """
    [
        {"operation":"buy", "unit-cost":10.00, "quantity":"a lot"}
    ]
    """
    with pytest.raises(ValueError, match="quantity \\(operation 1\\) must be a numeric value"):
        run_ops(ops)


def test_round2_rejects_non_numeric():
    with pytest.raises(ValueError, match="value must be a numeric value"):
        round2("abc")
