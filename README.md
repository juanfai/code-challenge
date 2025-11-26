# Capital Gains

CLI to calculate capital gains taxes by reading operations from `stdin` and printing results to `stdout` as JSON. Input is streamed: each line is a JSON array of operations, and each line of output is the corresponding list of tax results.

## How to run (local)
- Requires Python 3.10+.
- Use the bundled sample input (`input.txt`) or provide your own JSON array per line:
```bash
python exercise.py < input.txt
```

## Docker
If you prefer isolation from local Python versions:
- Build the image (from repo root):
```bash
docker build -t capital-gains .
```
- Run by piping an input file (one JSON array per line):
```bash
cat input.txt | docker run -i --rm capital-gains
```
- Or run interactively to paste input manually:
```bash
docker run -i --rm capital-gains
[{"operation":"buy","unit-cost":21210,"quantity":100}]  # paste lines, then Ctrl+D
```

## Error handling
- Invalid JSON: prints an error with the line number to `stderr` and exits with status `1`.
- Structural validation: `operations` must be a list of objects containing `operation`, `unit-cost`, and `quantity`.
- Allowed operations: `buy` or `sell` only; any other kind triggers a descriptive error.
- Numeric validation: `unit-cost`, `quantity`, and internal rounding reject non-numeric or non-finite values.

## Tests
Install `pytest` if needed, then run:
```bash
pytest -q
```

## Technical decisions
- **In-memory state**: Each call starts with clean `quantity`, `weighted average`, and `accumulated loss` to match the stateless CLI model.
- **Separation of concerns**: Dedicated helpers (`handle_buy`, `handle_sell`, `calculate_tax_for_profit`, etc.) keep business rules isolated and testable.
- **Deterministic rounding**: `round2` centralizes rounding to two decimals and now enforces numeric/finite inputs to avoid subtle float surprises.
- **Validation first**: Input is validated before processing so invalid structures or unsupported operations fail fast with actionable messages.
- **Dependencies**: Python standard library only; no external packages required.
- **I/O model**: Streams via STDIN/STDOUT for easy piping and shell integration; a sample `input.txt` is included for convenience.

## Live demo
No hosted demo is provided; run locally or via Docker using the commands above.
