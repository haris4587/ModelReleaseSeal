# Evidence format

Use fixtures/policy.json as the complete policy example. Top-level keys are exactly name, scope, metrics and criteria. Duplicate JSON keys and unknown fields are rejected. Policy JSON is bounded at 16,000 UTF-8 bytes; manifest packages at 2,000.

| Criterion ID | Meaning | Allowed gates |
| --- | --- | --- |
| identity | Exact artifact/version and use scope | hard |
| benchmark_validity | Dataset, definitions, held-out methodology, supported numbers | hard |
| coverage | Required evaluation scenarios | hard or soft |
| safety | Required tests, limitations and mitigations | hard or soft |
| conflicts | Negative runs and contradictions disclosed/resolved | hard |

Criteria must use that order. Metrics have id, unit, op, threshold, min_samples, dataset_sha256 and definition. Fixed-point basis_points means fraction times 10,000; 9200 is 92%. Latency can use integer milliseconds with a locked definition. No automatic unit conversion.

## Manifest package

The evidence_json string contains exactly card and evaluation. Each has exactly url, sha256 and bytes. URL form:

~~~text
https://raw.githubusercontent.com/OWNER/REPO/FULL_40_HEX_COMMIT/path/document.txt
~~~

Both documents must be 30–24,000 bytes and strict UTF-8. Hashes are lowercase 64-hex. No branches, query strings, fragments, credentials, ports, encoded paths or traversal. model_sha256 identifies the artifact separately from document hashes.

Generate exact fixture arguments against a real commit containing those bytes:

~~~sh
python scripts/build_manifest.py FULL_40_HEX_COMMIT --case ready --output docs/demo-arguments.json
~~~

## Model card

Plain text binding artifact hash/version, intended/excluded uses, datasets, methodology, test coverage, negative results, limitations and mitigations.

## Evaluation snapshot

The .txt file contains strict JSON with exactly model_sha256, metrics and narrative. See fixtures/ready-evaluation.txt. Each measurement has exactly id, value, unit, samples and dataset_sha256. IDs must be locked and unique. Values are signed integers within ±10^12; samples are 0–10^9. Maximum 8 measurements. Narrative length is 30–18,000 characters within the document byte bound.

Missing metric IDs yield UNKNOWN. Unknown/duplicate metrics, duplicate keys, invalid model identity or malformed schema invalidate the package. Include every relevant run and all adverse results. If original material is PDF/private, externally prepare a complete public plaintext snapshot and disclose its provenance. The contract authenticates the snapshot, not the original publisher.

## Offline audit

Export exact get_policy and get_receipt JSON strings:

~~~sh
python scripts/verify_receipt.py policy-record.json release-receipt.json
~~~

This checks hash integrity, policy binding and history links; it explicitly labels the receipt UNVERIFIED_OFFLINE. An internally consistent fabricated receipt can pass. Authenticate deployed code, network/address, successful finalized transactions and full contract state separately.

