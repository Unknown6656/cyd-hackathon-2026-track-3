"""Battery 13 — malicious timestamps (round 6).
A. Zone disambiguation: naive vs Z vs offsets at instants where interpretations disagree
   (S-02317 Brovary: active 02:00-04:15 local = 23:00-01:15Z previous day).
B. as_of format fuzzing (Pydantic datetime parsing edges).
C. /message timestamp format fuzzing.
D. S-03481 end-boundary hunt (active @05:00 local 2026-08-29; next Brovary window 2026-09-02T16:00),
   then zone-notation consistency at the boundary.
No rate limit (team decision).
"""
import json, ssl, time, urllib.request, urllib.error

BASE = "https://llmhack-team-3.hackathon.intlab.ch"
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE

def call(path, body, timeout=120):
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    try:
        r = urllib.request.urlopen(req, timeout=timeout, context=CTX)
        return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return -1, repr(e)

def advise_q(as_of, location="Brovary", q="Is it safe to go outside?"):
    return call("/advise", {"query": q, "as_of": as_of, "location": {"text": location}})

def msg(text, ts):
    return call("/message", {"text": text, "timestamp": ts})

def show(tag, c, d):
    try:
        j = json.loads(d)
        if "advice" in j:
            print(f"[{c}] {tag:34s}: siren={j.get('siren_active')} level={j.get('threat_level')} cites={j.get('citations')} as_of={j.get('as_of')}")
            return
        print(f"[{c}] {tag:34s}: {d[:220]}")
        return
    except Exception:
        pass
    print(f"[{c}] {tag:34s}: {d[:220]}")

print("=== A. ZONE DISAMBIGUATION (S-02317: active 23:00Z 08-26 .. 01:15Z 08-27) ===")
pairs = [
 # (label, as_of) — same-instant pairs to test naive interpretation
 ("A1 naive 04:45",            "2026-08-27T04:45"),
 ("A2 04:45Z (=A1 if UTC)",    "2026-08-27T04:45Z"),
 ("A3 01:45Z (=A1 if EET)",    "2026-08-27T01:45Z"),
 ("A4 04:45+03:00 (=A3)",      "2026-08-27T04:45+03:00"),
 ("A5 naive 02:30",            "2026-08-27T02:30"),
 ("A6 02:30Z (=A5 if UTC)",    "2026-08-27T02:30Z"),
 ("A7 23:30Z 08-26 (=A5 if EET)", "2026-08-26T23:30Z"),
 ("A8 02:30+03:00 (=A7)",      "2026-08-27T02:30+03:00"),
 ("A9 05:30+03:00 (=A6)",      "2026-08-27T05:30+03:00"),
 ("A10 22:30-05:00 (=A6)",     "2026-08-27T22:30-05:00"),
 ("A11 naive 01:00 (in win EET, out UTC)", "2026-08-27T01:00"),
 ("A12 01:00Z",                "2026-08-27T01:00Z"),
 ("A13 04:00+03:00 (=A12)",    "2026-08-27T04:00+03:00"),
]
for tag, a in pairs:
    show(tag, *advise_q(a))
print()

print("=== B. as_of FORMAT FUZZ (Brovary) ===")
fuzz = [
 ("B1 lowercase t",        "2026-08-27t04:45"),
 ("B2 no zero pad",        "2026-8-7T4:45"),
 ("B3 fractional",         "2026-08-27T04:45:00.123456"),
 ("B4 comma decimal",      "2026-08-27T04:45:00,500"),
 ("B5 hour 25",            "2026-08-27T25:00"),
 ("B6 minute 60",          "2026-08-27T04:60"),
 ("B7 leap second",        "2026-08-27T23:59:60"),
 ("B8 non-leap 02-29",     "2026-02-29T12:00"),
 ("B9 year 9999",          "9999-12-31T23:59:59"),
 ("B10 year 0001",         "0001-01-01T00:00:00"),
 ("B11 unicode digits",    "２０２６-08-27T04:45"),
 ("B12 epoch int",         1787743500),
 ("B13 offset no minutes", "2026-08-27T04:45+03"),
 ("B14 offset seconds",    "2026-08-27T04:45:00+03:00:30"),
 ("B15 trailing junk",     "2026-08-27T04:45:00Z x"),
 ("B16 natural lang",      "now"),
]
for tag, a in fuzz:
    show(tag, *advise_q(a))
print()

print("=== C. /message TIMESTAMP FORMAT FUZZ ===")
mfuzz = [
 ("C1 space",       "2026-08-27 04:45"),
 ("C2 fractional",  "2026-08-27T04:45:30.5"),
 ("C3 leap second", "2026-08-27T23:59:60"),
 ("C4 unicode",     "２０２６-08-27T04:45"),
 ("C5 epoch int",   1787743500),
 ("C6 pre-epoch",   "1969-12-31T23:59"),
 ("C7 year 0000",   "0000-01-01T00:00"),
 ("C8 month 13",    "2026-13-01T00:00"),
]
for tag, a in mfuzz:
    c, d = msg("Test post: drone sighted over the fields, no further info.", a)
    print(f"[{c}] {tag:20s} ({str(a)[:28]!r}): {d[:180]}")
print()

print("=== D. S-03481 END-BOUNDARY HUNT (Brovary; active @2026-08-29T05:00, next window 2026-09-02T16:00) ===")
coarse = ["2026-08-29T08:00", "2026-08-29T12:00", "2026-08-29T18:00", "2026-08-30T00:00",
          "2026-08-30T12:00", "2026-08-31T00:00", "2026-09-01T00:00", "2026-09-01T12:00", "2026-09-02T00:00"]
states = {}
for a in coarse:
    c, d = advise_q(a)
    try:
        sa = json.loads(d).get("siren_active")
    except Exception:
        sa = f"ERR{c}"
    states[a] = sa
    print(f"  {a} -> siren={sa}")
# find first clear after 05:00
clear_pts = [a for a in coarse if states[a] is False]
active_pts = [a for a in coarse if states[a] is True]
if clear_pts and active_pts:
    lo, hi = max(active_pts), min(clear_pts)
    print(f"boundary between {lo} and {hi}; refining...")
    import datetime as dt
    lo_t, hi_t = dt.datetime.fromisoformat(lo), dt.datetime.fromisoformat(hi)
    while (hi_t - lo_t) > dt.timedelta(minutes=5):
        mid = lo_t + (hi_t - lo_t) / 2
        m = mid.strftime("%Y-%m-%dT%H:%M")
        c, d = advise_q(m)
        sa = json.loads(d).get("siren_active")
        print(f"  refine {m} -> siren={sa}")
        if sa is True:
            lo_t = mid
        else:
            hi_t = mid
    boundary = hi_t
    print(f"~end: {boundary}")
    # zone-notation consistency at boundary +/- 1 min
    for label, a in [
        ("end-naive",  boundary.strftime("%Y-%m-%dT%H:%M")),
        ("end-Z",      (boundary - dt.timedelta(hours=3)).strftime("%Y-%m-%dT%H:%MZ")),
        ("end-+03",    (boundary).strftime("%Y-%m-%dT%H:%M+03:00")),
        ("start-naive", (boundary - dt.timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M")),
        ("start-Z",    (boundary - dt.timedelta(minutes=1) - dt.timedelta(hours=3)).strftime("%Y-%m-%dT%H:%MZ")),
        ("start-+03",  (boundary - dt.timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M+03:00")),
    ]:
        show(label, *advise_q(a))
