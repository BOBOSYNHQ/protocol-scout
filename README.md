# BOBOSYN Protocol Scout (Frontend)

Static single-file web app that talks to the [Protocol Scout API](https://github.com/BOBOSYNHQ/protocol-scout-api).

- **Live**: https://bobosynhq.github.io/protocol-scout/
- **Backend**: https://protocol-scout-api.superhelong.workers.dev/
- **Stack**: Vanilla HTML/CSS/JS (no build step). One file: `index.html`.

## Features

- Connect wallet (SIWE / personal_sign) — no email or signup
- Analyze any Web3 protocol by DefiLlama slug (`aave-v3`, `lido`, etc.)
- AI Deep Research via Claude Haiku (3 credits)
- Watchlist with live TVL snapshots
- Price / TVL alerts
- Pay-as-you-go top-ups with USDC/USDT on Base Sepolia (mainnet later)
- Shareable public reports
- Programmatic API Keys (Bearer) — for scripts and MCP clients

## Local preview

```bash
python -m http.server 8000
# open http://localhost:8000
```

The app reads its API URL from `const API_BASE` near the top of `<script>`. For local dev against `wrangler dev`, change it to `http://127.0.0.1:8787`.

## Deploy

The site ships directly from the `main` branch via GitHub Pages. No build required.

```bash
git add index.html
git commit -m "..."
git push origin main
# GitHub Pages picks up the change within ~1 minute.
```

## Project layout

```
.
├── index.html        # The whole UI (HTML + CSS + JS, single file)
├── README.md         # This file
└── .gitignore
```

## Configuration knobs (top of `<script>`)

| Constant | Default | Purpose |
|----------|---------|---------|
| `API_URL` | `https://protocol-scout-api.superhelong.workers.dev/analyze` | Legacy analyze endpoint |
| `API_BASE` | `https://protocol-scout-api.superhelong.workers.dev` | All other endpoints |
| `SHARE_URL_BASE` | `https://bobosynhq.github.io/protocol-scout/` | Public share link base |

## Privacy

The frontend does not embed Google Analytics, Mixpanel, Sentry, or any other tracking. Server logs are the only data we keep.

## Browser support

Tested in current Chrome / Firefox / Safari. Requires:

- ES2022 (async/await, optional chaining, top-level await in scripts)
- Web Crypto API (`crypto.subtle`, `crypto.getRandomValues`)
- MetaMask or another EIP-191 signing wallet

## License

Single-operator SaaS. All rights reserved.