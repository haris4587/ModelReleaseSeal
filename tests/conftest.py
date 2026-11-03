import copy
import importlib
import json
import re
import sys
from pathlib import Path

import pytest
from gltest.direct import VMContext, deploy_contract

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope='session', autouse=True)
def prepare_sdk():
    # Invalidate cached directory lookups after first-time SDK extraction.
    from gltest.direct.sdk_loader import setup_sdk_paths
    setup_sdk_paths(ROOT / 'contracts/model_release_seal.py', 'v0.2.16')
    importlib.invalidate_caches()


@pytest.fixture
def env():
    vm = VMContext()
    vm.sender = bytes.fromhex('11' * 20)
    with vm.activate():
        contract = deploy_contract(ROOT / 'contracts/model_release_seal.py', vm, sdk_version='v0.2.16')
        module = sys.modules['_contract_model_release_seal']
        yield vm, contract, module


@pytest.fixture
def policy():
    return json.loads((ROOT / 'fixtures/policy.json').read_text())


def package(module, case='ready'):
    card = (ROOT / f'fixtures/{case}-card.txt').read_text()
    evaluation = (ROOT / f'fixtures/{case}-evaluation.txt').read_text()
    model = (ROOT / 'fixtures/model-sha256.txt').read_text().strip()
    docs = {}
    for key, body in [('card', card), ('evaluation', evaluation)]:
        docs[key] = {
            'url': f'https://raw.githubusercontent.com/haris4587/ModelReleaseSeal/{"a"*40}/fixtures/{case}-{key}.txt',
            'sha256': module.hashlib.sha256(body.encode()).hexdigest(), 'bytes': len(body.encode())
        }
    return model, docs, card, evaluation


def report(module, card, evaluation, statuses=None):
    # Mocked semantic reports exercise the real SDK closures, not real AI judgment.
    lines = card.splitlines()[1:6]
    statuses = statuses or ['PASS'] * 5
    return {'checks': [
        {'id': category, 'status': status, 'card_quote': line, 'evaluation_quote': line,
         'explanation': 'The documented evidence explicitly supports this locked requirement.'}
        for category, line, status in zip(module.CATEGORIES, lines, statuses)
    ]}


def setup_release(env, policy, case='ready', statuses=None, grounding='true'):
    vm, contract, module = env
    model, docs, card, evaluation = package(module, case)
    pid = contract.lock_policy(json.dumps(policy))
    rid = contract.submit_release(pid, model, json.dumps(docs))
    install_mocks(vm, docs, card, evaluation, report(module, card, evaluation, statuses), grounding)
    return rid, docs, card, evaluation


def install_mocks(vm, docs, card, evaluation, semantic, grounding='true'):
    vm.clear_mocks()
    vm.mock_web(re.escape(docs['card']['url']), {'status': 200, 'body': card})
    vm.mock_web(re.escape(docs['evaluation']['url']), {'status': 200, 'body': evaluation})
    vm.mock_llm('^Audit an AI model release', json.dumps(semantic))
    vm.mock_llm('^Independently verify', grounding)

