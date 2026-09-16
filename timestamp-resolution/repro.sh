#!/bin/sh
# Repro: same real instant, two ISO-8601 spellings -> opposite verdicts.
# 2026-08-27T01:45 Kyiv (EEST, UTC+3) == 2026-08-26T22:45Z
ENDPOINT=https://llmhack-team-3.hackathon.intlab.ch/advise

ask() { # $1 = as_of literal
	DATA="{\"query\": \"What is the current situation and threat level?\", \"as_of\": \"$1\", \"location\": {\"text\": \"Brovary\"}}"
	curl -sS -X POST -H "Content-Type: application/json" -d "$DATA" "$ENDPOINT" \
	| jq -r '[.threat_level, (.siren_active|tostring), ((.citations//[])|join("+")), .as_of] | @tsv'
}

printf 'as_of\tthreat\tsiren\tcitations\techoed_as_of\n'
for t in '2026-08-27T01:45' '2026-08-26T22:45Z'; do
	printf '%-17s\t%s\n' "$t" "$(ask "$t")"
done
