# promptutils

`clean_prompt()` removes comments (lines starting with #) and extra whitespace from messy prompts.

```python
from promptutils import clean_prompt
clean_prompt("  # comment\n    hello world  ") # -> "hello world"
```

Install: `uv pip install git+https://github.com/testy-cool/promptutils.git@main`

## Installation

Install directly from GitHub using your preferred installer. With **uv** (recommended):
