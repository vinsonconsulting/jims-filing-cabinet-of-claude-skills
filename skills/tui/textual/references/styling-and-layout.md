# Styling & layout (Textual CSS)

TCSS is CSS for the terminal: selectors, a box model, and layout. It lives in a `CSS` class
attribute, a `CSS_PATH` (`.tcss` file), or a widget's `DEFAULT_CSS`. Edit it live with
`textual run --dev` for hot-reload. Verified against **8.2.7**.

## Where CSS lives

```python
class MyApp(App):
    CSS_PATH = "app.tcss"        # external file (preferred for big apps)
    CSS = """                    # or inline
    Screen { align: center middle; }
    """

class MyWidget(Widget):
    DEFAULT_CSS = """            # ships with the widget; app CSS overrides it
    MyWidget { height: auto; }
    """
```

App `CSS` overrides a widget's `DEFAULT_CSS`; later/more-specific rules win, like web CSS.

## Selectors

| Selector | Matches |
| --- | --- |
| `Button` | every widget of type `Button` (and subclasses) |
| `#save` | the widget with `id="save"` (ids are unique) |
| `.row` | widgets with the CSS class `row` (`classes="row"`, or `add_class`/`toggle_class`) |
| `Button.-active` | combine type + class |
| `#sidebar Button` | descendant combinator |
| `Button:hover`, `Input:focus`, `*:disabled` | pseudo-classes |

Toggle classes from code to restyle: `widget.add_class("error")`, `widget.toggle_class("open")`.

## Box model & common properties

`width`/`height`, `min-/max-` variants; `padding`, `margin`, `border`. Sizes use **units**:

- integer = **cells** (`width: 24`)
- `%` = percent of the parent
- `fr` = fraction of leftover space (`width: 1fr`; two `1fr` siblings split 50/50)
- `auto` = size to content
- `vw`/`vh` = percent of the viewport

```css
#panel {
    width: 1fr;
    height: auto;
    padding: 1 2;                 /* vertical horizontal */
    border: round $primary;       /* style + color */
    background: $surface;
}
```

## Layout

Each container lays out its children by its `layout`:

- `layout: vertical` (default) / `layout: horizontal` — stack down / across.
- `layout: grid` — with `grid-size: <cols> <rows>`, `grid-columns`, `grid-rows`,
  `grid-gutter`, and per-cell `column-span`/`row-span`.

```css
#dash { layout: grid; grid-size: 2 2; grid-gutter: 1; }
```

`dock` pins a widget to an edge so it doesn't scroll with siblings — ideal for headers, footers,
sidebars:

```css
#topbar  { dock: top;    height: 1; }
#status  { dock: bottom; height: 1; }
#sidebar { dock: left;   width: 24; }
```

`align: <h> <v>` centers children (`align: center middle`); `content-align` aligns a widget's own
content; `offset: x y` nudges; `layer`/`layers` controls z-order (used for popups/overlays).

## Containers

From `textual.containers` — group children and give them a layout for free:

| Container | Use |
| --- | --- |
| `Container` | generic block |
| `Vertical` / `Horizontal` | explicit stacking direction |
| `VerticalGroup` / `HorizontalGroup` | stack with `height: auto` (no scroll) |
| `VerticalScroll` / `HorizontalScroll` | scrollable region (anchor target for streaming) |
| `ScrollableContainer` | scroll in both axes |
| `Grid` / `ItemGrid` | grid layout / auto-flowing grid |
| `Center` / `Middle` / `CenterMiddle` / `Right` | alignment helpers |

```python
with Horizontal():
    yield Static("nav", id="sidebar")        # width: 24
    yield VerticalScroll(id="body")          # width: 1fr → fills the rest
```

## Theme variables

Colors come from the active theme as `$`-variables: `$primary`, `$secondary`, `$accent`,
`$background`, `$surface`, `$panel`, `$boost`, `$success`, `$warning`, `$error`, plus
`$text`, `$text-muted`, `$text-disabled`. Use them instead of hard-coded colors so the app
respects the theme.

Set the theme via the `App.theme` reactive (a string). Builtin themes include `textual-dark`,
`textual-light`, `nord`, `gruvbox`, `dracula`, `tokyo-night`, `monokai`, `catppuccin-mocha`,
`solarized-dark`, `rose-pine`, `flexoki`, `ansi-dark`, and more (21 total at 8.2.7). Register a
custom `Theme` with `App.register_theme(...)`. Explore the palette with `textual colors`.

## Tips

- Iterate styling with `textual run --dev app.py` — TCSS reloads on save without restarting.
- Reach for `dock` + `fr` before doing any manual width arithmetic.
- `display: none` removes a widget from layout; `visibility: hidden` keeps its space.
- Scrollbars are styleable (`scrollbar-size`, `scrollbar-color`, gutter) but rarely need it.
