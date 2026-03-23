# webinar-march

Small Python project: a command-line calculator that reads an arithmetic expression (for example `(5+8)*2`) and prints the result.

Expressions are evaluated by parsing an AST and walking only allowed numeric operations. **`eval()` and `exec()` are not used.**

## Setup

Install [uv](https://docs.astral.sh/uv/), then from this directory:

```bash
uv sync
```

## Run

Interactive prompt:

```bash
uv run calculator
```

Pipe input:

```bash
echo "(5+8)*2" | uv run calculator
```

Or run the module:

```bash
uv run python -m app.calculator
```

## Tests

```bash
uv run pytest
```

## Layout

- `app/calculator.py` — evaluation logic and CLI entrypoint
- `tests/test_calculator.py` — pytest suite
