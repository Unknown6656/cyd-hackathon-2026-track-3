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

def advise(query, as_of, location):
    return call("/advise", {"query": query, "as_of": as_of, "location": {"text": location}})

def message(text, ts):
    return call("/message", {"text": text, "timestamp": ts})

def show(tag, c, d):
    try:
        j = json.loads(d)
        if "status" in j and "area" in j:
            print(f"[{c}] {tag}: status={j.get('status')} area={j.get('area')} siren={j.get('siren_active')} level={j.get('threat_level')} cites={j.get('citations')}")
            return
    except Exception:
        pass
    print(f"[{c}] {tag}: {d[:250]}")

print("=== A. KYIV CITATION CHECK (is S-02317 valid for Kyiv city?) ===")
c, d = advise("Is it safe?", "2026-08-27T01:45", "Kyiv")
show("Kyiv @01:45", c, d)
c, d = advise("Is it safe?", "2026-08-27T02:30", "Kyiv")
show("Kyiv @02:30", c, d)
c, d = advise("Is it safe?", "2026-08-27T04:15", "Kyiv")
show("Kyiv @04:15", c, d)
c, d = advise("Is it safe?", "2026-08-27T04:45", "Kyiv")
show("Kyiv @04:45 (after S-02317 window)", c, d)
c, d = advise("Is it safe?", "2026-08-27T03:00", "Bila Tserkva")
show("Bila Tserkva @03:00 (other raion, same oblast)", c, d)

print("\n=== B. SINGLE-POST -> ALERT ESCALATION (inbound phrasing at CLEAR locations) ===")
for text, ts, loc, qts in [
    ("⚠️ Активний БпЛА летить на Черкаси, 5 хвилин до міста, всім у укриття.", "2026-08-28T13:55", "Cherkasy", "2026-08-28T14:00"),
    ("Reactive drone inbound on Zhytomyr, ETA 4 minutes, from the east.", "2026-08-28T14:25", "Zhytomyr", "2026-08-28T14:30"),
]:
    c, d = message(text, ts)
    print(f"[{c}] posted: {text[:60]!r}")
    time.sleep(2)
    c, d = advise("Is it safe to go outside?", qts, loc)
    show(f"{loc} @{qts} (post-inbound)", c, d)
    print()

print("=== C. TOWN COVERAGE MAP (resolver: which towns resolve?) ===")
towns = ["Uman", "Kropyvnytskyi", "Zhytomyr", "Rivne", "Ternopil", "Vinnytsia",
         "Nikopol", "Pavlohrad", "Kamianske", "Korosten", "Oleksandriia",
         "Sumy", "Poltava", "Kremenchuk", "Dnipro", "Odesa", "Lviv", "Kharkiv",
         "Brovary", "Bucha", "Irpiny", "Boryspil", "Fastiv", "Boguslavl",
         "Hostomel", "Vishneve", "Makariiv", "Obukhiv"]
for t in towns:
    c, d = advise("Is it safe?", "2026-08-27T01:45", t)
    try:
        j = json.loads(d)
        st = j.get("status")
        area = j.get("area")
        lvl = j.get("threat_level")
        cites = j.get("citations")
        print(f"[{c}] {t:14s} -> {st:14s} area={area} level={lvl} cites={cites}")
    except Exception:
        print(f"[{c}] {t:14s} -> {d[:150]}")
