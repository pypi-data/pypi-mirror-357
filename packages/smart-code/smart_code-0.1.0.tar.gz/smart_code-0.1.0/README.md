# smart_code

Static code optimizer that analyzes Python code to suggest algorithmic efficiency improvements.

## Installation

```bash
pip install smart-code
```

## Usage

```bash
smart-code path/to/file.py
```

Or in Python:

```python
from smart_code.analyzer import analyze_code
from smart_code.suggestor import format_suggestions

code = "..."
sugs = analyze_code(code)
print(format_suggestions(sugs))
```
