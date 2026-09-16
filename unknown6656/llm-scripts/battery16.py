"""Battery 16 — FINAL AUDIT (round 8, last battery): for every known siren alert,
check whether the app reports the siren RUNNING (siren_active=true) in-window
or marked ALL-CLEAR (siren_active=false) at the control point after the window.
Plan from /tmp/audit_plan.json (33 Brovary windows x in/out + Kyiv/Chernihiv alerts).
Results -> audit_results.jsonl. No rate limit (team decision)."""
import json, ssl, time, urllib.request, urllib.error

BASE = "https://llmhack-team-3.hackathon.intlab.ch"
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
plan = json.load(open("/tmp/audit_plan.json"))

def advise(a, loc):
    req = urllib.request.Request(BASE + "/advise",
        data=json.dumps({"query": "Is it safe to go outside?", "as_of": a,
                         "location": {"text": loc}}).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        r = urllib.request.urlopen(req, timeout=120, context=CTX)
        return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return -1, repr(e)

out = open("/tmp/audit_results.jsonl", "w")
for i, p in enumerate(plan, 1):
    c, d = advise(p["t"], p["loc"])
    rec = {"n": i, "id": p["id"], "kind": p["kind"], "t": p["t"], "loc": p["loc"], "status": c}
    try:
        j = json.loads(d)
        rec["siren"] = j.get("siren_active")
        rec["level"] = j.get("threat_level")
        rec["cites"] = j.get("citations")
        rec["area"] = j.get("area")
    except Exception:
        rec["raw"] = d[:160]
    # verdict
    sid = p["id"]
    if p["kind"] == "in":
        rec["verdict"] = ("SIREN-RUNNING" if rec.get("siren") is True
                          else "ALL-CLEAR-!!" if rec.get("siren") is False
                          else f"OTHER-{c}")
        if rec.get("siren") is True:
            rec["cite_match"] = sid in (rec.get("cites") or [])
    elif p["kind"] == "out":
        rec["verdict"] = "ALL-CLEAR" if rec.get("siren") is False else ("STILL-RUNNING" if rec.get("siren") is True else f"OTHER-{c}")
    else:  # bracket
        rec["verdict"] = ("ACTIVE" if rec.get("siren") is True else "clear" if rec.get("siren") is False else f"OTHER-{c}")
    out.write(json.dumps(rec) + "\n"); out.flush()
    print(f"[{i:02d}/{len(plan)}] {rec['id']} {p['kind']:3s} {p['t']} {p['loc']:10s} -> {rec['verdict']:15s} cites={rec.get('cites')}")
out.close()
print("AUDIT DONE")
