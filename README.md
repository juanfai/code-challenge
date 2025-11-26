# Capital Gains

CLI to calculate capital gains taxes by reading operations from `stdin` and printing results to `stdout` as JSON.

## Technical decisions
- **In-memory state**: Each call to `process_operations` starts fresh (`quantity`, `weighted average`, `accumulated loss`); no databases or files.
- **Separation of concerns**: `exercise.py` splits logic into small helpers (`handle_buy`, `handle_sell`, etc.) for clarity and maintainability.
- **Rounding**: Monetary calculations are rounded to two decimals via `round2`.
- **Dependencies**: Python standard library only; no extra frameworks.

## Run
Requires Python 3. Read from `stdin`:
```bash
python exercise.py < input.txt
```
Each input line must be a JSON array of operations; output is an array of objects containing the tax per operation.

## Tests
Install `pytest` if needed, then run:
```bash
pytest -q
```

## Notes
- Assumes well-formed input (no parsing error handling).
- Numbers in output remain numeric (not strings), allowing JSON libraries to omit trailing zeros if they do so by default.
