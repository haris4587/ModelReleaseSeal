# Security model

Report vulnerabilities privately to the repository owner through an available private channel. Do not publish secrets.

## Enforced controls

- Creator-only submission/evaluation, immutable policies/artifact IDs/evidence.
- Contract-allocated IDs and independent records prevent identifier squatting.
- Exact commit-pinned raw GitHub host/path allowlist, with no arbitrary SSRF destination.
- Exact size, SHA-256 and UTF-8 verification before reasoning.
- Strict bounded schemas, duplicate-key rejection, integer arithmetic and mandatory integrity gates.
- Independent validator retrieval and inference, matching all decision fields.
- Exact excerpts plus contextual source-grounding of the leader report.
- Prompts explicitly treat policy text, evidence and proposed reports as untrusted data.
- No writes within nondeterministic execution; bounded attempts and hash-linked history.

## Limitations

AI can misunderstand evidence, follow an injection despite instructions, or share correlated errors. Mocked adversarial fixtures verify checks and data flow, not universal prompt-injection resistance. Consensus liveness is not guaranteed.

Evidence authors can fabricate experiments, sample counts and provenance. SHA-256 proves bytes, not experimental truth or authorship. The contract never downloads model weights or executes benchmarks.

The allowlist constrains requested URLs; GenVM's HTTP module controls redirects, timeouts and buffering. Body-size checks occur AFTER retrieval and are not a streaming cap. Large responses can consume resources. GitHub/network failures can cause inconclusive results or failed consensus.

Creators can choose weak policies and create additional release IDs. Per-release bounds are not Sybil-resistant. Review scope, all known releases and complete histories; absence of undisclosed negative evidence cannot be proved.

There is no token custody, automated deployment authorization or safety certification. Results are scoped documentary readiness assessments. No external security audit is claimed. Live deployment/finality and fail-closed outcomes are recorded in docs/LIVE_TEST.md; successful positive semantic assessment remains unverified.

