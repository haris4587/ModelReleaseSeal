# Reviewer walkthrough

1. Run README tests and GenVM checks. Inspect contracts/model_release_seal.py and docs/abi.json.
2. Deploy the exact contract in GenLayer Studio with no constructor arguments on a network supporting its pinned runtime.
3. Use docs/demo-arguments.json: pass lock_policy.policy_json as ONE string argument. Wait for successful finality and recover the returned policy ID.
4. Call submit_release with that ID, model_sha256 and evidence_json. Recover the release ID after successful finality.
5. Call evaluate_release(release_id) in **Normal / Full Consensus**, simulation off. Wait for successful finalized execution, not just transaction acceptance.
6. Read get_policy and get_receipt. Verify hashes, source identities, numerical checks, all five semantic findings and full history.
7. Record chain ID, address, source checksum and successful finalized deployment/lock/submission/evaluation transactions.

The ready fixture is expected to yield RELEASE_READY if independent validators find the evidence adequate. Expected outcomes are not hardcoded; live model disagreement can block consensus or yield a different supported classification.

Generate additional cases against the fixture commit in demo-arguments.json:

~~~sh
python scripts/build_manifest.py FULL_FIXTURE_COMMIT --case conditional
python scripts/build_manifest.py FULL_FIXTURE_COMMIT --case rejected
python scripts/build_manifest.py FULL_FIXTURE_COMMIT --case inconclusive
python scripts/build_manifest.py FULL_FIXTURE_COMMIT --case conflict
python scripts/build_manifest.py FULL_FIXTURE_COMMIT --case injection
~~~

Reuse the same locked policy but submit a NEW release for each package.

| Case | Evidence | Expected interpretation |
| --- | --- | --- |
| ready | All scoped requirements documented | RELEASE_READY |
| conditional | Explicitly unperformed optional multilingual test | CONDITIONAL |
| rejected | F1 8500 below 9000 | REJECTED |
| inconclusive | Missing safety records | INCONCLUSIVE |
| conflict | Excluded adverse run with no reconciliation | INCONCLUSIVE or REJECTED for explicit hard noncompliance; never READY |
| injection | Ready evidence plus malicious output instructions | Ignore commands; assess documented evidence |

All fixtures are synthetic. A hash mismatch must prevent READY. A branch URL must reject at submission. Another wallet must not submit/evaluate under your policy. A fourth completed evaluation must revert. Mocked automated cases are not live benchmark or network execution evidence.

