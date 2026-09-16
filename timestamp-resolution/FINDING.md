# `as_of` timezone handling: CLEAR returned for an instant that is under ALERT

**Endpoint:** `POST /advise` (see `client.sh`)
**Field:** `as_of`

## Claim

**Confirmed.** A naive (offset-less) `as_of` is interpreted as *local* (Kyiv) wall time. A
timezone-aware `as_of` is shifted by its offset before the lookup. So the same real instant
gets looked up 3 hours apart depending on how it is spelled.

## One instant, two spellings, opposite answers

Kyiv is on **EEST = UTC+3** on 2026-08-27, therefore
`2026-08-27T01:45` local **is** `2026-08-26T22:45Z` — the same instant on earth.

Request A — naive, read as Kyiv local time:

```json
{"query":"What is the current situation in Brovary?","as_of":"2026-08-27T01:45","location":{"text":"Brovary"}}
```
```json
{"status":"ok","advice":"An official air-raid alert is active for your area. ... Go to shelter now ...",
 "as_of":"2026-08-27T01:45:00","area":"Brovary, Brovary urban hromada, Brovary Raion, Kyiv Oblast",
 "siren_active":true,"citations":["S-02317"],"threat_level":"ALERT"}
```

Request B — **same instant**, spelled in UTC:

```json
{"query":"What is the current situation in Brovary?","as_of":"2026-08-26T22:45Z","location":{"text":"Brovary"}}
```
```json
{"status":"ok","advice":"No current threat is known for this area at the requested time.",
 "as_of":"2026-08-26T22:45:00","area":"Brovary, ...","siren_active":false,
 "citations":[],"threat_level":"CLEAR"}
```

Note the echoed `as_of` is returned **shifted**, not as sent — the server applies the offset and
looks up `22:45`, which is outside the alert window `S-02317` (active 01:30–04:20 local).

## Reproduce

```sh
./repro.sh
```
```
as_of              threat  siren  citations  echoed_as_of
2026-08-27T01:45   ALERT   true   S-02317    2026-08-27T01:45:00
2026-08-26T22:45Z  CLEAR   false             2026-08-26T22:45:00
```

## Mechanism

| `as_of` sent | echoed / looked up | threat |
|---|---|---|
| `2026-08-27T01:45` | `2026-08-27T01:45` | ALERT |
| `2026-08-27T01:45Z` | `2026-08-27T01:45` | ALERT |
| `2026-08-27T01:45+03:00` | `2026-08-26T22:45` | **CLEAR** |
| `2026-08-26T22:45Z` | `2026-08-26T22:45` | **CLEAR** |

`Z` / `+00:00` behave like naive values, so the dataset frame is treated as UTC-equivalent and
only a **non-zero** offset moves the lookup. `+03:00` is exactly what a Ukrainian client, or any
client localising to the user's timezone, legitimately sends.
