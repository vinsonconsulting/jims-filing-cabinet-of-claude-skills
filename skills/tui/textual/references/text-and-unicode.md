# Text, content markup & Unicode

How Textual renders text safely, and where the Rich boundary is. Verified against **8.2.7**
(Rich **15.0.0**).

## Content markup vs Rich

Textual styles inline text with **content markup**: `"[bold]hi[/]"`, `"[red]error[/red]"`,
`"[@click=app.quit]quit[/]"`. By default `Static`/`Label` parse markup (`markup=True`). This is
Textual's own `Content` system — prefer it over building Rich `Text` objects inside widgets.
Rich renderables (tables, panels, syntax) still work as **static** content drawn inside a
widget; a Textual widget is a **live DOM node**. Rule of thumb: live, interactive, styled-by-CSS
→ Textual widget; a one-shot richly-formatted blob → a Rich renderable passed to `Static`.

## Never f-string untrusted text into markup

User text containing `[` is interpreted as markup — an injection/clobbering risk and a frequent
source of `MarkupError`. Don't do `Static(f"[bold]{user_input}[/]")`. Instead:

```python
from textual.content import Content

# Safe templating: variables are substituted, NOT parsed as markup.
Content.from_markup("Hello [bold]$name[/]", name=user_input)

# Or render the text literally with no markup at all:
Static(user_input, markup=False)

# Or escape it:
from rich.markup import escape
Static(f"[dim]{escape(user_input)}[/]")
```

`Content.from_markup(markup, **variables)` is the canonical safe constructor — author the
template yourself and pass user data as keyword variables.

## Display width ≠ length

A terminal cell is the unit, and **one character is not always one cell**:

- CJK ideographs and many emoji are **2** cells wide.
- Combining marks are **0** cells; a flag emoji is several codepoints but 2 cells.

Textual/Rich measure and clip by **display width**, so the built-in widgets wrap and truncate
correctly — trust them. The footgun is only when *you* do column math (truncating a title,
aligning a gutter, computing a wrap point): use cell width, not `len()` or `.count()`.

```python
from rich.cells import cell_len
cols = cell_len(title)        # display columns — NOT len(title)
```

## Wrapping & overflow

Wrapping is controlled by CSS (`width`, `text-wrap`, `text-overflow`) and the widget. For a log,
`RichLog(wrap=True)` wraps long lines; for a `Static`, set a `width` and let it wrap. Don't
pre-wrap strings by hand — let the layout do it so it reflows on resize. For grapheme-correct
manual truncation with an ellipsis, accumulate `cell_len` and stop at the budget.
