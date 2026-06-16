# Web deploy (the Textual-only divergence)

Textual's trick the siblings don't have: the **same app** that runs in a terminal can be served
to a browser, unchanged. This is genuinely in scope for this skill — a request to "put my
Textual app in a browser" is a Textual task, not a web-framework task. Verified against
**textual-serve 1.1.3** / Textual **8.2.7**.

## `textual serve` (self-hosted — the default answer)

`textual serve` (from `textual-dev`) runs a local web server that renders your app in the
browser over a websocket. No code changes:

```bash
textual serve "python -m myapp"        # serve a command
textual serve myapp.py                  # or a module/app
# --host 0.0.0.0 --port 8000 to expose it
```

For embedding in your own ASGI/web app, the **`textual-serve`** library exposes a `Server` you
can mount. The app you serve is the *same* `App` subclass — your `compose`, TCSS, reactives, and
workers all run server-side; the browser is a thin terminal emulator over a websocket.

## What works in the browser

- Full keyboard/mouse, layout, TCSS, animations, widgets — the rendered output is the same grid of cells.
- Each browser connection is a server-side app **instance** (state lives on the server), so plan capacity like any stateful websocket app — one running process per session.
- No terminal graphics protocols (Sixel/Kitty images) in the browser path.

## The honest deployment read

`textual serve` keeps a **long-lived, stateful websocket + a running Python process per user**.
That maps to a **VM, container, or stateful PaaS** (Fly.io, Railway, Render, a plain Docker host,
Kubernetes). It is **not** a fit for edge/serverless (Cloudflare Workers, Lambda, Vercel
functions): those are short-lived, stateless, and don't hold a persistent process per
connection. Don't promise a serverless deploy.

## Textual Web (hosted) — verify before relying on it

**Textual Web** was Textualize's hosted service for publishing apps via a public URL without
running your own server. After the company wound down (mid-2025), **treat its hosted status as
unverified** — check the `textual-web` repo and whether sign-ups still work before recommending
it. Do not assert the hosted service is live. The reliable, in-your-control path is self-hosted
`textual serve` on a VM/container/PaaS as above.
