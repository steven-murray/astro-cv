# LaTeX Formatting Utilities

This module provides shared utilities for LaTeX generation across all CV sections.

## Functions

### `custom_format(string, brackets, *args, **kwargs)`

Format strings like `str.format()`, but with custom bracket delimiters instead of `{}`.

**Args:**
- `string`: Template string
- `brackets`: List of two strings `[open, close]` for custom delimiters
- `*args, **kwargs`: Values for substitution

**Example:**
```python
from astro_cv.formats.latex import custom_format

template = "Hello, [[name]]! You are [[age]] years old."
result = custom_format(template, ["[[", "]]"], name="Alice", age=30)
# Result: "Hello, Alice! You are 30 years old."
```

### `myformat(string, *args, escape_amp=True, **kwargs)`

Format LaTeX template strings with automatic escaping.

Uses custom brackets `<% %>` for template substitution and automatically escapes
ampersands (`&`) to LaTeX-safe format (`\&`) unless disabled.

**Args:**
- `string`: Template string with `<% %>` placeholders
- `*args`: Positional arguments for substitution
- `escape_amp`: Whether to escape ampersands (default: `True`)
- `**kwargs`: Keyword arguments for substitution

**Returns:**
- Formatted string with LaTeX-safe content

**Example:**
```python
from astro_cv.formats.latex import myformat

template = r"\textbf{<% name %>} & \href{mailto:<% email %>}{<% email %>}"
result = myformat(template, name="Smith & Jones", email="smith@example.com")
# Result: r"\textbf{Smith \& Jones} & \href{mailto:smith@example.com}{smith@example.com}"
```

## Usage in Sections

All section `latex.py` modules should import from this shared module:

```python
from astro_cv.formats.latex import myformat

def create_my_section(config: MySection) -> str:
    template = r"""
    \section{<% title %>}
    <% content %>
    """
    return myformat(template, title=config.title, content=config.content)
```

## Design Rationale

- **Centralized utilities**: Avoid code duplication across section modules
- **Custom delimiters**: LaTeX uses `{}` extensively, so we use `<% %>` to avoid conflicts
- **Automatic escaping**: LaTeX special characters (especially `&`) are escaped automatically
- **Extensible**: Easy to add more LaTeX formatting utilities as needed
