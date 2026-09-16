import json, sys, urllib.request, urllib.error

BASE = "https://llmhack-team-3.hackathon.intlab.ch"

def call(path, body):
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    try:
        r = urllib.request.urlopen(req, timeout=90)
        code = r.status
        data = r.read().decode()
    except urllib.error.HTTPError as e:
        code = e.code
        data = e.read().decode()
    return code, data

def advise(query, as_of="2026-08-27T01:45", location="Brovary", raw_location=None):
    body = {"query": query, "as_of": as_of}
    if raw_location is not None:
        body["location"] = raw_location
    elif location is not None:
        body["location"] = {"text": location}
    return call("/advise", body)

def message(text, ts="2026-08-27T02:05"):
    return call("/message", {"text": text, "timestamp": ts})

mode = sys.argv[1]
if mode == "advise":
    code, data = advise(*sys.argv[2:4], **(dict(as_of=sys.argv[4], location=sys.argv[5]) if len(sys.argv) > 5 else {}))
elif mode == "message":
    code, data = message(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "2026-08-27T02:05")
print(f"HTTP {code}: {data}")
