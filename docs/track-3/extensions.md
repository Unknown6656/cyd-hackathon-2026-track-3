# Extensions

Source: https://hackathon-armasuisse.github.io/tracks/track-3/extensions/

> **Optional.** Once your core advisor works, these are directions to take it further. They are pointers, not requirements: pick any, all, or none.

Your baseline is the advisor from [Building your Application](./building-your-application.md).

## 1. Add a user interface

A person under an alert wants a colour and a sentence, not JSON. A map with the last hour of reports plotted, and a single line telling them what to do, demos far better than a transcript.

> [Open WebUI](https://openwebui.com) speaks the OpenAI chat format, so a thin adapter in front of `/advise` gets you a chat UI quickly.

## 2. Confidence and source weighting

Add a confidence to each answer, and let it depend on where the evidence came from: a siren record, a corroborated report, or a single unverified post do not deserve equal weight.

## 3. Your own extension

Free choice. Two possibilities:

- **data augmentation**: search for more useful data online, that can be added to the corpus for retrieval.
- **Chat instead of a single answer**: let the user ask follow-ups, and keep the context of the conversation. Let the LLM ask for clarifications, or for the user to confirm a location.
