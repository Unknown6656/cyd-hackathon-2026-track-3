# Public siren / air-raid alert data (Ukraine)

Recon notes, fetched 2026-09-16. The hackathon `sirens.csv` (21 Aug – 3 Sep 2026, 4241 records) is a **synthetic historical extract** delivered in the encrypted zip (password Monday). The files below are **live public sources** — useful to understand the real data shape and field vocabulary the synthetic record was modeled on.

## Keyless source (used for the samples below)

`https://ubilling.net.ua/aerialalerts/` — no key, no auth, 2 req/s limit. Unifies several upstream sources; pick with `?source=`:

| source | upstream |
| --- | --- |
| `default` | whichever is alive (last was "Vadym Klymenko API") |
| `skog` | Mørk Skogen (nightflyza/skogen) |
| `klimenko` | Vadym Klimenko's "єМапа" (vadimklimenko.com/map) |
| `jaam` | JAAM data server (jaam.net.ua) |
| `aiu` | alerts.in.ua |
| `ual` | ukrainealarm.com (official API for the gov app "Повітряна тривога") |

Append `&raw` for unprocessed upstream data, `&xml=true` for XML.

## Files

- `siren_unified.json` — normalized current state per oblast: `{alertnow, changed}`.
- `siren_aiu_raw.json` — alerts.in.ua records. Closest match to the hackathon `siren record`:
  `id, location_title(_en), location_type (oblast|raion|city|hromada), started_at, finished_at (null while active), updated_at, alert_type, location_oblast(_uid), location_raion, location_uid, notes, alert_level (red|yellow), threats[]`.
- `siren_ual_raw.json` — official ukrainealarm.com shape: per-region `activeAlerts[]` with `type (AIR|ARTILLERY|URBAN_FIGHTS|CHEMICAL|NUCLEAR)`, `activeAlertLevels[{alertLevel: Red|Yellow, reason, createdAt}]`, `lastUpdate`. Note `regionType: State|Community` and `regionId` = UID.
- `locations.csv` — alerts.in.ua's official UID list (1622 rows): 25 oblasts, 126 raions (Crimea's 10 raions not listed), 2 special-status cities, 1469 hromadas. Columns: `UID, Назва, Тип, Примітки`.

## Caveats / recon takeaways

- These APIs return **current active alerts only** — no public historical bulk. History requires an alerts.in.ua token (`/v1/regions/{uid}/alerts/month_ago.json`, form at alerts.in.ua/api-request) or the hackathon zip.
- Occupied-territory raions (Luhansk, Donetsk, Kherson, Zaporizhzhia, Crimea) are pinned `alertnow: true` indefinitely — matches the hackathon's "never clear an area whose siren is still running" rule; expect the same behavior in the target.
- Field vocabulary for `location`: oblast / raion / hromada / city, in Ukrainian romanization exactly as the target's example response uses ("Brovarskyi raion, Kyivska oblast").
- `finished_at` may stay `null` for a long time (stale records) — the "slow to cancel" behavior the brief mentions is real.
- Rate limits: ubilling 2 rps; alerts.in.ua 8–12 req/min per IP with a token.

## Upstream links

- alerts.in.ua + API docs: https://alerts.in.ua · https://devs.alerts.in.ua
- official app API (key via form): https://api.ukrainealarm.com
- єМапа by Vadym Klimenko: https://vadimklimenko.com/map/
- Mørk Skogen: https://github.com/nightflyza/skogen
- Air Raid Alerts API (and3rson/raid): https://github.com/and3rson/raid
- Telegram channel "Повітряна Тривога": https://t.me/air_alert_ua
