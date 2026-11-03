# Validation evidence

Validation date: 2026-11-03. Python 3.12.14; official GenVM SDK v0.2.16; genvm-linter 0.11.0; genlayer-test 0.29.2; pytest 9.2.0.

| Check | Result |
| --- | --- |
| SDK direct automated suite | 51 passed |
| Numerical/semantic gate priority | Exhaustive 2,187 combinations within the suite |
| GenVM AST lint | Passed |
| Exact SDK semantic validation | Passed |
| ABI extraction and comparison | Passed; 6 public methods, 3 write and 3 view |
| Nondeterministic callback serialization | Passed with official direct runner pickling checks |
| Public-network deployment/finality | Not performed; no configured signing account/live node |

The suite covers all four outcomes; integer threshold boundaries; sample minimums; wrong units/dataset/model identity; missing and duplicate measurements; duplicate JSON keys; unknown fields; type/bounds attacks; commit-only URL allowlisting; creator authorization; immutable policy records; three-attempt history and hashes; corrupted/HTTP-failing evidence; invalid model output; independently disagreeing validators; forged quotes, status, numeric values, outcomes and explanations; different grounded prose; source reauthentication; offline tampering detection; closure pickling; and no history write after rejected consensus.

Direct tests run the actual contract against real SDK storage/serialization, with mocked web and LLM responses. Captured validator callbacks are explicitly executed separately and with changed evidence/answers. A host-side rejection test checks that a rejected callback cannot write history. These tests do not simulate the distributed protocol, economic security, appeals, finality, transport limits or actual AI judgment.

The injection fixture includes malicious instructions as evidence. Mock responses verify data flow and deterministic checks; they do not prove any live LLM resists arbitrary prompt injection. The conflict fixture tests independent decision matching under an explicit UNKNOWN classification; real validators may determine explicit hard noncompliance instead.

## Reproduce

~~~sh
pip install -r requirements-test.txt
python -m pytest -q
genvm-lint check contracts/model_release_seal.py
genvm-lint schema contracts/model_release_seal.py --output /tmp/model-release-abi.json
diff -u docs/abi.json /tmp/model-release-abi.json
~~~

A session fixture initializes the pinned SDK and invalidates Python's directory import caches after first-time extraction. No tests are skipped or replaced by a handwritten fake SDK. CI runs the same checks. Live network evidence must be recorded separately according to DEPLOYMENT.md.

