# Deployment status

Implementation, automated SDK direct tests, GenVM lint/semantic validation and ABI extraction are included. **No public deployment address, funded signing account, live transaction or multi-validator finality result is claimed.** This workspace provided no configured GenLayer signing account or live node. Public-network deployment remains unverified.

The source pins official GenVM v0.2.16 and its py-genlayer runner hash. Deploy only on a compatible network; do not silently change the dependency hash.

## Studio deployment

1. Open https://studio.genlayer.com/ and load contracts/model_release_seal.py.
2. Deploy with no arguments using the chosen account.
3. Save the transaction hash, chain ID and contract address.
4. Use docs/demo-arguments.json and docs/REVIEWER_GUIDE.md to lock, submit and evaluate.
5. Select Normal / Full Consensus, simulation off, and wait for successful finality.

The official CLI also provides deploy, write, call, receipt and code commands. Consult the installed CLI's help for evolving network/account/fee flags. Never commit a key or .env.

## Live verification record

Before claiming live deployment, record:

- Network, chain ID, RPC and address.
- Repository source SHA-256 and independently retrieved deployed source checksum.
- Deployment, policy, release and assessment transaction hashes.
- Successful finalized receipts, actual consensus execution mode and relevant traces.
- Exported policy and complete release history with exact evidence bytes and recalculated hashes.

Do not substitute mock hashes or example addresses. Offline integrity is not chain authenticity.

## Official references consulted on 2026-11-03

- https://docs.genlayer.com/developers/intelligent-contracts/features/calling-llms
- https://docs.genlayer.com/developers/intelligent-contracts/features/non-determinism
- https://docs.genlayer.com/developers/intelligent-contracts/types/collections
- https://docs.genlayer.com/api-references/genlayer-linter
- https://docs.genlayer.com/api-references/genlayer-test/direct
- https://docs.genlayer.com/api-references/genlayer-cli

