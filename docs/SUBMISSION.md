# Intelligent Contracts submission

**Name:** ModelReleaseSeal

**Short description:** Evidence-bound AI model release assessments combining deterministic benchmark enforcement with independently validated semantic review on GenLayer.

**Category:** Intelligent Contracts — standalone reusable primitive.

## Purpose

AI release decisions often depend on model cards and favorable headline scores. ModelReleaseSeal locks scope and release requirements before evidence submission, binds an exact model artifact and commit-pinned reports, and checks whether documented tests and limitations actually support the proposed release.

## Consensus role

The leader and validators independently retrieve, authenticate and assess evidence across identity, benchmark validity, coverage, safety and conflicts. Validators require matching classifications and numerical results, authenticate exact quotations and separately ground proposed interpretations against complete sources. Format-only checks cannot pass. Native GenLayer nondeterministic execution gates all assessment writes.

## Reusability

Policies are reusable across model versions. Inputs are immutable. Canonical receipts bind policy hashes, release commitments and append-only three-attempt histories. Creator permissions isolate records. Outcomes are RELEASE_READY, CONDITIONAL, REJECTED and INCONCLUSIVE; conditions arise only from explicitly soft requirements.

## Review links

- contracts/model_release_seal.py — source
- docs/abi.json — ABI
- docs/TESTING.md — checks and verification boundaries
- docs/REVIEWER_GUIDE.md — reproducible walkthrough
- docs/demo-arguments.json — exact fixture inputs
- docs/EVIDENCE.md — input schemas and hashes
- SECURITY.md — enforced controls and remaining risks
- docs/DEPLOYMENT.md — honest deployment status

Bundled evidence is synthetic. The primitive assesses documentary readiness, not universal safety, and does not execute models or rerun benchmarks. Local SDK checks and mocked direct tests are included. Live Studionet contract: 0x29C140CAA44978645BFAa830594222DCE703dba8. Seven Normal-mode transactions finalized successfully. Recorded assessments returned INCONCLUSIVE and REJECTED because semantic output validation failed; these runs demonstrate fail-closed behavior, not a completed positive semantic review. See docs/LIVE_TEST.md for transaction links, receipts and remaining limitations.

