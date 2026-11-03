# ModelReleaseSeal

**Evidence-bound AI model release reviews on GenLayer.**

Live contract on Studionet (61999): [0x29C140CAA44978645BFAa830594222DCE703dba8](https://explorer-studio.genlayer.com/address/0x29C140CAA44978645BFAa830594222DCE703dba8). Seven transactions finalized with successful execution. [Live evidence and limitations](docs/LIVE_TEST.md): the two assessments exercised fail-closed behavior (INCONCLUSIVE and REJECTED); neither completed semantic findings.

A standalone Intelligent Contract for deciding whether an exact AI model artifact satisfies a locked release policy. Commit numerical thresholds and semantic requirements first, submit immutable evaluation snapshots, and obtain quotation-grounded assessments through native GenLayer leader/validator execution.

This repository includes the contract primitive, automated tests, synthetic evidence, ABI and reviewer instructions. It has no frontend and belongs in **Intelligent Contracts**.

## Decision rules

| Outcome | Rule |
| --- | --- |
| REJECTED | Any verified numerical failure or hard semantic failure |
| INCONCLUSIVE | No hard failure but any required finding is unknown, or evidence cannot be authenticated |
| CONDITIONAL | All hard requirements pass, no unknowns, at least one explicitly soft requirement fails |
| RELEASE_READY | Every numerical and semantic requirement passes |

Hard failure takes priority over uncertainty. Invalid evidence produces INCONCLUSIVE before claimed measurements are used. Invalid AI output cannot erase a verified numeric failure. CONDITIONAL records unmet soft requirements; it does not authorize deployment.

## Why GenLayer matters

Deterministic code checks artifact and dataset hashes, units, sample counts and integer thresholds. Independent AI reasoning assesses whether benchmark methodology supports those numbers, the promised deployment scope was tested, and limitations or adverse results have been concealed.

The leader retrieves and authenticates both documents, then assesses five locked criteria: identity, benchmark validity, coverage, safety and conflicts. Each validator independently repeats retrieval and reasoning BEFORE inspecting the leader's decision. It requires agreement on every classification and numerical check, validates exact source excerpts and separately grounds the proposed explanations in the full evidence.

The contract uses native gl.vm.run_nondet_unsafe. A well-formed JSON response alone cannot pass consensus. SDK direct tests mock web/LLM I/O and exercise the actual validator closure; they are not live consensus evidence.

## API

| Method | Purpose |
| --- | --- |
| lock_policy(policy_json) | Permanently lock a caller-owned policy; returns ID |
| submit_release(policy_id, model_sha256, evidence_json) | Bind an artifact and two manifests to an existing caller-owned policy; returns ID |
| evaluate_release(release_id) | Append a consensus-backed assessment; creator only, maximum three completed attempts |
| get_policy(policy_id) | Return canonical policy JSON and hash |
| get_receipt(release_id) | Return immutable release inputs and complete hash-linked history |
| get_counts() | Return policy/release counts |

Policies are reusable across model versions. Each evidence package creates a separate release ID; prior inputs and history cannot be edited. IDs are contract allocated, preventing identifier squatting. There is no administrator, token custody, automatic upgrade or global record quota.

## Run

Python 3.12+ is required by the pinned official SDK.

~~~sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-test.txt
python -m pytest -q
genvm-lint check contracts/model_release_seal.py
genvm-lint schema contracts/model_release_seal.py --output docs/abi.json
~~~

The first test run downloads official GenVM v0.2.16 artifacts. See [test evidence](docs/TESTING.md), [reviewer walkthrough](docs/REVIEWER_GUIDE.md) and [deployment status](docs/DEPLOYMENT.md).

## Trust boundaries

Evidence must use HTTPS raw GitHub .txt URLs with full 40-character commits and match exact SHA-256 and UTF-8 byte lengths. Evaluation snapshots contain strict JSON and fixed-point integer measurements. No arbitrary URLs, document renderers, untrusted link traversal or executable models are accepted.

Hashes bind bytes, not truth or authorship. This primitive does not execute model weights, rerun benchmarks, prove training-data provenance, guarantee safety, certify legal compliance or force deployment tooling to obey verdicts. Policy requirements and evidence remain self-attested unless independently authenticated outside the contract. A policy lock proves transaction ordering, not that it predates the developer's testing.

Read [evidence format](docs/EVIDENCE.md), [security](SECURITY.md), [architecture](docs/ARCHITECTURE.md) and [submission text](docs/SUBMISSION.md). All bundled model data is explicitly synthetic.

