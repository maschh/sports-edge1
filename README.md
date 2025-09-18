# Sports Edge (Free, Auto-Refreshing via GitHub Pages)

This repo runs **daily sports predictions** (MLB, NBA, NFL, CFB) using **free data sources** and publishes
a clean **HTML report** to GitHub Pages automatically.

Live page (after you enable Pages): `https://<your-username>.github.io/sports-edge/`

## What it does
- Pulls free data: MLB StatsAPI, balldontlie (NBA), nflverse & sportsdataverse (NFL/CFB), Google Trends, Meteostat weather.
- Builds features: Elo, rolling form, public interest (Trends), optional injuries (CSV), weather.
- Trains: LightGBM for win probabilities + totals regression.
- Outputs: `predictions.html` with American odds, spreads, totals, and model leans.
- Automation: GitHub Action runs daily and commits the updated HTML.

## Quick Start
1) Push this folder to your repo (e.g., `maschh/sports-edge`).  
2) In **Settings → Pages**, set Source to `main` branch, folder `/ (root)`.
3) Actions run daily at 09:00 UTC, or trigger manually (Actions → Daily Predictions → Run workflow).

