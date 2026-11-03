# Architecture

## Immutable commitments

Policies lock scope, metric definitions and five semantic requirements before releases reference them. The policy hash covers ID, creator, version and canonical policy. Only its creator can submit or evaluate releases.

Release commitments bind ID, creator, version, policy ID/hash, artifact SHA-256 and both evidence manifests; history is excluded. Multiple releases reuse one policy without changing thresholds.

## Deterministic enforcement

Policies define 1–8 unique metrics, each with dataset SHA-256, unit, integer threshold, comparator (gte/lte), minimum samples and natural-language definition. Missing metrics or incomparable units/datasets yield UNKNOWN. Comparable measurements outside thresholds or below minimum sample count FAIL. Every numerical gate is hard. Boolean, floating-point and string measurements are rejected.

Five ordered semantic criteria are identity, benchmark_validity, coverage, safety and conflicts. Identity, benchmark validity and conflicts must be hard. Coverage and safety may be explicitly soft. PASS requires adequate supporting evidence and exact quotations from BOTH sources. FAIL requires a source quote; UNKNOWN may explain missing evidence with empty quotes.

## Native equivalence logic

1. Leader retrieves and hashes both snapshots, parses structured measurements, calculates numeric checks and independently infers semantic findings.
2. Validator independently repeats retrieval, hashing and inference, without the leader answer in its initial prompt.
3. Validator compares outcome, error reason, every numerical check and each ordered semantic classification.
4. Validator reauthenticates sources, validates the leader's exact quotes and deterministic aggregation, and performs a separate grounding review of the proposed explanations.
5. State changes occur only after protocol acceptance.

Different grounded prose and quotations are allowed; decision-critical fields must agree exactly. Malformed leader results, validator exceptions or disagreement return false. Failed protocol consensus produces no committed history entry. An INCONCLUSIVE assessment is an accepted result about insufficient evidence, not a disguised consensus failure.

Each independent assessment uses at most two downloads and one LLM call. A successful semantic validator uses two additional downloads and one grounding call. There are no internal retries, link-following loops or open-ended tools.

## Append-only receipts

Each release permits at most three completed attempts. An entry binds attempt number, release commitment, previous hash and complete report. The first previous hash is the release commitment. Its decision hash is SHA-256 of canonical entry JSON before adding decision_hash.

Canonicalization uses sorted JSON keys, literal Unicode, compact separators, no NaN and UTF-8 hashing. Text is not Unicode-normalized. Policy/release hashes similarly exclude their own hash fields. These hashes are not transaction signatures: successful finalized on-chain transactions and reads provide authenticity.

No entry is overwritten or designated the sole authoritative outcome. Inspect all attempts and related release IDs. A later PASS does not erase an earlier rejection. Per-release attempt bounds do not prevent creators making new releases or wallets.

