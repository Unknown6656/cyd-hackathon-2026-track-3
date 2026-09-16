"""Map siren_active windows for a location by sweeping as_of, then refine boundaries."""
import concurrent.futures as cf
import json
import sys
import time
from datetime import datetime, timedelta

sys.path.insert(0, "redteam")
from common import advise

Q = "Is it safe to go outside right now?"


def sweep(location, start, end, step_min=60, workers=3, tag="sweep"):
    t0 = datetime.fromisoformat(start)
    t1 = datetime.fromisoformat(end)
    points = []
    t = t0
    while t <= t1:
        points.append(t)
        t += timedelta(minutes=step_min)
    out = {}

    def hit(p):
        rec = advise(Q, p.strftime("%Y-%m-%dT%H:%M"), location, tag=tag)
        r = rec["response"]
        active = None
        cit = None
        if isinstance(r, dict) and "siren_active" in r:
            active = r["siren_active"]
            cit = r.get("citations")
        return p, active, cit

    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for p, active, cit in ex.map(hit, points):
            out[p.strftime("%Y-%m-%dT%H:%M")] = {"active": active, "citations": cit}
    return out


def refine(location, lo, hi, tag="refine"):
    """Find boundary between lo (known state) and hi (other state) to ~10 min."""
    res = {}
    lo_t, hi_t = datetime.fromisoformat(lo), datetime.fromisoformat(hi)
    while (hi_t - lo_t) > timedelta(minutes=10):
        mid = lo_t + (hi_t - lo_t) / 2
        m = mid.strftime("%Y-%m-%dT%H:%M")
        rec = advise(Q, m, location, tag=tag)
        r = rec["response"]
        active = r.get("siren_active") if isinstance(r, dict) else None
        res[m] = active
        if active == res[lo_t.strftime("%Y-%m-%dT%H:%M")]:
            lo_t, lo = mid, m
        else:
            hi_t, hi = mid, m
    return res


if __name__ == "__main__":
    location = sys.argv[1]
    start = sys.argv[2] if len(sys.argv) > 2 else "2026-08-21T00:00"
    end = sys.argv[3] if len(sys.argv) > 3 else "2026-09-03T23:00"
    out = sweep(location, start, end)
    fn = f"redteam/results/windows_{location.replace(' ', '_').replace('/', '_')}.json"
    with open(fn, "w") as f:
        json.dump(out, f, indent=1)
    runs = []
    cur = None
    for k, v in sorted(out.items()):
        if v["active"] is True:
            if cur is None:
                cur = [k, k, v["citations"]]
            else:
                cur[1] = k
                cur[2] = cur[2] or v["citations"]
        else:
            if cur:
                runs.append(cur)
                cur = None
    if cur:
        runs.append(cur)
    print(json.dumps(runs, indent=1))
    print(f"wrote {fn}")
