# TraderJoe2025

**July 2025** | Archived personal project by NodeNestor

## What is this?

A real-time turbo warrant trading dashboard for Nordnet (Swedish broker). Uses Playwright to open browser tabs, intercept WebSocket and SSE streams, and display live turbo pricing data in a custom HTML dashboard.

Built to monitor long/short turbo positions simultaneously with relative performance tracking.

## Features

- Real-time WebSocket interception for turbo warrant bid/ask/price data
- SSE stream capture for underlying instrument prices
- Multi-tab browser automation (Playwright)
- Live HTML dashboard with relative performance, RSI, momentum, volatility indicators
- SQLite time-series storage and CSV export
- Spread monitoring, trend signals, and arbitrage opportunity detection

## Tech Stack

- **Python 3** with asyncio
- **Playwright** for browser automation and WebSocket/SSE interception
- **SQLite** for time-series data storage
- **NumPy** for analytics
- **Vanilla HTML/CSS/JS** for the dashboard UI

## Files

| File | Description |
|------|-------------|
| `TestSocket.py` | Early prototype — basic multi-tab WebSocket monitor |
| `ashbord.py` | First dashboard iteration with embedded HTML UI |
| `Dahsbrd.py` | Enhanced dashboard with analytics and strategy signals |
| `Dashbord3.py` | Extended version with more indicators |
| `dashbord4.py` | Final version — SQLite storage, CSV export, NumPy analytics |

## How it worked

1. Launch Playwright browser with multiple tabs pointing to Nordnet login
2. User logs in manually via BankID
3. Script intercepts WebSocket frames for turbo price/depth data
4. SSE streams captured for underlying instrument prices
5. Data fed into a custom dashboard page with live charts and analytics
6. All data persisted to SQLite and CSV for later analysis

## Status

**Archived.** This was a personal learning project. Not maintained.

## License

MIT
