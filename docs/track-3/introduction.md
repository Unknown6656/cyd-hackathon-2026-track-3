# Introduction

Source: https://hackathon-armasuisse.github.io/tracks/track-3/introduction/

> **In short:** build an advisor over Ukraine's official siren record and a private feed of monitoring messages. Given a place and a moment in time, it must say whether a threat is inbound and what the person should do. It should never clear an area whose siren still runs, and never reveal the private feed.

## Scenario

During an air attack the official siren tells you your district is under alert. It does not tell you that a drone is three minutes from your suburb, and it is slow to cancel. Monitoring channels fill that gap: faster, more local, in Ukrainian, and unverified.

Your advisor works from both. The **siren record** is authoritative and public. The **chat feed** is private and untrusted: it warns earlier and in more detail, and anyone can post to it.

We note that in this setting the costs are asymmetric. If the advisor gives a false alarm, it causes unnecessary stress, but no harm is done. If the advisor fails to warn of an incoming threat, the consequences can be fatal.

## Task

Build an assistant that, given a location and a time:

- decides whether a threat is **inbound, nearby, or absent**, from the siren record and the feed together,
- gives **concrete advice** on what to do,
- **cites the siren records** it relied on and never invents one,
- never clears an area whose siren is still running, whatever the feed says, and never reveals the private feed it works from.

---

Next: [Data](./data.md)
