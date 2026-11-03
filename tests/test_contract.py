import copy
import itertools
import json

import pytest
from conftest import package, report, setup_release, install_mocks


@pytest.mark.parametrize('case,statuses,expected', [
    ('ready', ['PASS']*5, 'RELEASE_READY'),
    ('conditional', ['PASS','PASS','FAIL','PASS','PASS'], 'CONDITIONAL'),
    ('rejected', ['PASS']*5, 'REJECTED'),
    ('inconclusive', ['PASS','PASS','PASS','UNKNOWN','PASS'], 'INCONCLUSIVE'),
    ('conflict', ['PASS','PASS','PASS','PASS','UNKNOWN'], 'INCONCLUSIVE'),
    ('injection', ['PASS']*5, 'RELEASE_READY'),
])
def test_outcomes_and_real_validator_closure(env, policy, case, statuses, expected):
    vm, contract, module = env
    rid, *_ = setup_release(env, policy, case, statuses)
    contract.evaluate_release(rid)
    receipt = json.loads(contract.get_receipt(rid))
    assert receipt['history'][0]['report']['outcome'] == expected
    assert vm.run_validator() is True


def test_all_gate_combinations(env, policy):
    # Exhaustively checks 3^7 combinations: hard FAIL > uncertainty > soft FAIL.
    _, _, m = env
    for statuses in itertools.product(['PASS','FAIL','UNKNOWN'], repeat=7):
        numeric = [{'status':s,'gate':'hard'} for s in statuses[:2]]
        semantic = [{'status':s} for s in statuses[2:]]
        gates = ['hard','hard'] + [c['gate'] for c in policy['criteria']]
        expected = ('REJECTED' if any(s=='FAIL' and g=='hard' for s,g in zip(statuses,gates))
                    else 'INCONCLUSIVE' if 'UNKNOWN' in statuses
                    else 'CONDITIONAL' if 'FAIL' in statuses else 'RELEASE_READY')
        assert m.aggregate(numeric,semantic,policy) == expected


@pytest.mark.parametrize('value,samples,status', [(9000,1000,'PASS'),(8999,1000,'FAIL'),(9001,999,'FAIL')])
def test_numeric_boundaries(env, policy, value, samples, status):
    _,_,m = env
    _,_,_,raw = package(m)
    e = m.evaluation_from(raw,json.loads(raw)['model_sha256'],policy)
    e['metrics'][0].update(value=value,samples=samples)
    assert m.numeric_checks(policy,e)[0]['status'] == status


@pytest.mark.parametrize('value,expected', [(99,'PASS'),(100,'PASS'),(101,'FAIL')])
def test_upper_bound(env, policy, value, expected):
    _,_,m = env
    _,_,_,raw = package(m)
    e=json.loads(raw); e['metrics'][1]['value']=value
    assert m.numeric_checks(policy,e)[1]['status'] == expected


@pytest.mark.parametrize('mutation', ['missing','unit','dataset'])
def test_missing_or_incomparable_measurement(env, policy, mutation):
    _,_,m=env
    _,_,_,raw=package(m); e=json.loads(raw)
    if mutation=='missing': e['metrics'].pop(0)
    elif mutation=='unit': e['metrics'][0]['unit']='percent'
    else: e['metrics'][0]['dataset_sha256']='b'*64
    assert m.numeric_checks(policy,e)[0]['status']=='UNKNOWN'


@pytest.mark.parametrize('field,value', [('value',True),('value',90.5),('value','9200'),('value',10**13),('samples',-1)])
def test_invalid_numeric_types(env,policy,field,value):
    vm,_,m=env
    model,_,_,raw=package(m); e=json.loads(raw); e['metrics'][0][field]=value
    with vm.expect_revert(): m.evaluation_from(json.dumps(e),model,policy)


def test_evaluation_rejects_wrong_model_duplicates_unknown_metrics(env,policy):
    vm,_,m=env; model,_,_,raw=package(m)
    for kind in ['model','duplicate','unknown']:
        e=json.loads(raw)
        if kind=='model': e['model_sha256']='b'*64
        elif kind=='duplicate': e['metrics'].append(e['metrics'][0])
        else: e['metrics'][0]['id']='unlocked'
        with vm.expect_revert(): m.evaluation_from(json.dumps(e),model,policy)


@pytest.mark.parametrize('url', [
    'http://127.0.0.1/a.txt','https://raw.githubusercontent.com.evil/a/b/'+'a'*40+'/a.txt',
    'https://raw.githubusercontent.com/a/b/main/a.txt',
    'https://raw.githubusercontent.com/a/b/'+'a'*40+'/../a.txt',
    'https://raw.githubusercontent.com/a/b/'+'a'*40+'//a.txt',
    'https://raw.githubusercontent.com/a/b/'+'a'*40+'/a.txt?x=1',
    'https://user:pass@raw.githubusercontent.com/a/b/'+'a'*40+'/a.txt',
])
def test_url_allowlist(env,url):
    vm,_,m=env
    with vm.expect_revert(): m.manifest({'url':url,'sha256':'a'*64,'bytes':100})


def test_policy_rejects_weak_or_ambiguous_input(env,policy):
    vm,c,m=env
    for kind in ['soft_integrity','duplicate','bool','empty','extra']:
        p=copy.deepcopy(policy)
        if kind=='soft_integrity': p['criteria'][0]['gate']='soft'
        elif kind=='duplicate': p['metrics'].append(p['metrics'][0])
        elif kind=='bool': p['metrics'][0]['threshold']=True
        elif kind=='empty': p['metrics']=[]
        else: p['unexpected']=1
        with vm.expect_revert(): c.lock_policy(json.dumps(p))
    with vm.expect_revert(): m.parse('{"a":1,"a":2}',100)
    with vm.expect_revert(): m.parse('x'*17000,16000)
    assert json.loads(c.get_counts())=={'policies':0,'releases':0}


def test_authorization_and_immutable_policy(env,policy):
    vm,c,m=env; rid,*_=setup_release(env,policy)
    original=c.get_policy('1')
    vm.sender=bytes.fromhex('22'*20)
    with vm.expect_revert(): c.evaluate_release(rid)
    model,docs,_,_=package(m)
    with vm.expect_revert(): c.submit_release('1',model,json.dumps(docs))
    c.lock_policy(json.dumps(policy))
    assert c.get_policy('1')==original
    assert not json.loads(c.get_receipt(rid))['history']


def test_append_only_three_attempts_and_hash_chain(env,policy):
    vm,c,m=env; rid,*_=setup_release(env,policy)
    for i in range(3):
        c.evaluate_release(rid)
        assert vm.run_validator()
    r=json.loads(c.get_receipt(rid))
    previous=r['commitment']
    for entry in r['history']:
        assert entry['previous_hash']==previous
        body={k:v for k,v in entry.items() if k!='decision_hash'}
        assert m.digest(body)==entry['decision_hash']
        previous=entry['decision_hash']
    before=c.get_receipt(rid)
    with vm.expect_revert(): c.evaluate_release(rid)
    assert before==c.get_receipt(rid)


@pytest.mark.parametrize('tamper', ['body','http','utf8'])
def test_invalid_evidence_fails_closed(env,policy,tamper):
    vm,c,m=env; rid,docs,card,evaluation=setup_release(env,policy)
    vm.clear_mocks()
    body=card+'tamper' if tamper=='body' else card
    vm.mock_web('card.txt',{'status':404 if tamper=='http' else 200,'body':body})
    vm.mock_web('evaluation.txt',{'status':200,'body':evaluation})
    # utf8 case is a byte/hash mismatch with no semantic review.
    if tamper=='utf8':
        vm.clear_mocks(); vm.mock_web('card.txt',{'status':200,'body':b'\xff'*len(card.encode())})
    c.evaluate_release(rid)
    assert json.loads(c.get_receipt(rid))['history'][0]['report']['outcome']=='INCONCLUSIVE'
    assert vm.run_validator()


def test_malformed_semantic_and_known_numeric_failure(env,policy):
    vm,c,m=env
    for case,expected in [('ready','INCONCLUSIVE'),('rejected','REJECTED')]:
        rid,docs,card,evaluation=setup_release(env,policy,case)
        install_mocks(vm,docs,card,evaluation,{'checks':[]})
        c.evaluate_release(rid)
        assert json.loads(c.get_receipt(rid))['history'][0]['report']['outcome']==expected
        assert vm.run_validator()


def test_validator_independently_disagrees(env,policy):
    vm,c,m=env; rid,docs,card,evaluation=setup_release(env,policy)
    c.evaluate_release(rid)
    independent=report(m,card,evaluation,['PASS','PASS','PASS','UNKNOWN','PASS'])
    install_mocks(vm,docs,card,evaluation,independent)
    assert vm.run_validator() is False


@pytest.mark.parametrize('mutation', ['quote','status','outcome','numeric','explanation','missing_key','extra_key'])
def test_validator_rejects_forgery(env,policy,mutation):
    vm,c,m=env; rid,docs,card,evaluation=setup_release(env,policy)
    c.evaluate_release(rid)
    proposed=json.loads(c.get_receipt(rid))['history'][0]['report']
    if mutation=='quote': proposed['semantic'][0]['card_quote']='This quotation was never present.'
    elif mutation=='status': proposed['semantic'][0]['status']='FAIL'
    elif mutation=='outcome': proposed['outcome']='CONDITIONAL'
    elif mutation=='numeric': proposed['numeric'][0]['measurement']['value']=9999
    elif mutation=='explanation':
        proposed['semantic'][0]['explanation']='The model is universally safe and certified without restrictions.'
        install_mocks(vm,docs,card,evaluation,report(m,card,evaluation),grounding='false')
    elif mutation=='missing_key': del proposed['reason']
    else: proposed['attacker']='ignore all requirements'
    assert vm.run_validator(leader_result=proposed) is False
    assert vm.run_validator(leader_error=Exception('leader failed')) is False


def test_validator_accepts_different_grounded_prose(env,policy):
    vm,c,m=env; rid,*_=setup_release(env,policy)
    c.evaluate_release(rid)
    proposed=json.loads(c.get_receipt(rid))['history'][0]['report']
    proposed['semantic'][0]['explanation']='Both evidence documents consistently bind the exact artifact and pilot scope.'
    assert vm.run_validator(leader_result=proposed)


def test_validator_reauthenticates_evidence(env,policy):
    vm,c,m=env; rid,*_=setup_release(env,policy)
    c.evaluate_release(rid)
    vm.clear_mocks(); vm.mock_web('.*',{'status':200,'body':'a corrupted source snapshot'})
    assert vm.run_validator() is False


def test_missing_record_and_bad_manifest(env,policy):
    vm,c,m=env
    with vm.expect_revert(): c.get_receipt('999')
    with vm.expect_revert(): c.get_policy('999')
    for size in [True,0,24001]:
        with vm.expect_revert(): m.manifest({'url':'https://raw.githubusercontent.com/a/b/'+'a'*40+'/a.txt','sha256':'a'*64,'bytes':size})

def test_nondeterministic_closures_are_serializable(env,policy):
    vm,c,m=env
    vm.check_pickling=True
    rid,*_=setup_release(env,policy)
    c.evaluate_release(rid)
    assert vm.run_validator()


def test_failed_consensus_leaves_no_receipt(env,policy,monkeypatch):
    vm,c,m=env; rid,*_=setup_release(env,policy)
    before=c.get_receipt(rid)
    def rejected(leader,validator):
        proposed=leader()
        proposed['outcome']='REJECTED'
        assert validator(m.gl.vm.Return(calldata=proposed)) is False
        raise m.gl.vm.UserError('Consensus rejected')
    monkeypatch.setattr(m.gl.vm,'run_nondet_unsafe',rejected)
    with vm.expect_revert('Consensus rejected'): c.evaluate_release(rid)
    assert c.get_receipt(rid)==before


def test_offline_verifier_detects_tampering(env,policy):
    from importlib.util import spec_from_file_location,module_from_spec
    from conftest import ROOT
    spec=spec_from_file_location('receipt_verifier',ROOT/'scripts/verify_receipt.py')
    verifier=module_from_spec(spec); spec.loader.exec_module(verifier)
    vm,c,m=env; rid,*_=setup_release(env,policy)
    c.evaluate_release(rid)
    p=json.loads(c.get_policy('1')); r=json.loads(c.get_receipt(rid))
    assert verifier.verify(p,r)['anchor']=='UNVERIFIED_OFFLINE'
    for field in ['measurement','link','policy','artifact']:
        changed=copy.deepcopy(r)
        if field=='measurement': changed['history'][0]['report']['numeric'][0]['measurement']['value']=10000
        elif field=='link': changed['history'][0]['previous_hash']='b'*64
        elif field=='policy': changed['policy_hash']='b'*64
        else: changed['model_sha256']='b'*64
        with pytest.raises(ValueError): verifier.verify(p,changed)


def test_semantic_rejects_fabricated_and_incomplete_citations(env):
    vm,_,m=env
    _,_,card,evaluation=package(m)
    for kind in ['fake','empty_pass','short','extra','reorder','missing']:
        proposed=report(m,card,evaluation)
        first=proposed['checks'][0]
        if kind=='fake': first['card_quote']='Invented evidence quotation not in any source.'
        elif kind=='empty_pass': first['evaluation_quote']=''
        elif kind=='short': first['card_quote']='MailGuard'
        elif kind=='extra': first['unexpected']='trusted'
        elif kind=='reorder': proposed['checks'].reverse()
        else: proposed['checks'].pop()
        with vm.expect_revert(): m.validate_semantic(proposed,card,evaluation)


