"""Read-only live verification. No private key, wallet or transaction submission."""
import base64
import hashlib
import json
from pathlib import Path
import requests
from genlayer_py.abi import calldata
from genlayer_py.abi.transactions import serialize
from genlayer_py.contracts.utils import make_calldata_object
from verify_receipt import verify

ROOT=Path(__file__).resolve().parents[1]
STATE=json.loads((ROOT/'docs/live/deployment.json').read_text())


def rpc(method,params):
    response=requests.post(STATE['rpc'],json={'jsonrpc':'2.0','id':1,'method':method,'params':params},timeout=60)
    response.raise_for_status()
    data=response.json()
    if data.get('error'):
        raise RuntimeError(data['error'])
    return data['result']


def read(method,args):
    data=serialize([calldata.encode(make_calldata_object(method=method,args=args,kwargs=None)),b'\x00'])
    result=rpc('gen_call',[{'type':'read','to':STATE['address'],'from':STATE['demo_signer'],
                           'data':data,'transaction_hash_variant':'latest-final'}])
    return json.loads(calldata.decode(bytes.fromhex(result.removeprefix('0x'))))


def main():
    assert int(rpc('eth_chainId',[]),16)==STATE['chain_id']==61999
    source=base64.b64decode(rpc('gen_getContractCode',[STATE['address']]))
    assert source==(ROOT/'contracts/model_release_seal.py').read_bytes()
    assert hashlib.sha256(source).hexdigest()==STATE['source_sha256']
    for label,tx_hash in STATE['transactions'].items():
        tx=rpc('eth_getTransactionByHash',[tx_hash])
        assert tx['status']=='FINALIZED'
        assert tx['execution_mode']=='NORMAL' and tx['leader_only'] is False
        # Studio stores the signed transaction envelope here even in Normal mode.
        # Permit that envelope only; reject simulation overrides and mocked outputs.
        assert set(tx.get('sim_config') or {}).issubset({'signed_rollup_transaction'})
        assert tx['to_address'].lower()==STATE['address'].lower()
        expected_sender=STATE['browser_demo_signer'] if label in ['lock_policy_browser','submit_rejected','evaluate_rejected'] else STATE['demo_signer']
        assert tx['from_address'].lower()==expected_sender.lower()
        leaders=tx['consensus_data']['leader_receipt']
        assert leaders and leaders[0]['execution_result']=='SUCCESS'
        assert sum(v=='agree' for v in tx['consensus_data']['votes'].values())>=3
        if label=='deploy':
            assert base64.b64decode(tx['data']['contract_code'])==source
        else:
            call=json.loads(tx['data']['calldata']['readable'])
            expected_method=('submit_release' if label.startswith('submit_') else
                             'evaluate_release' if label.startswith('evaluate_') else 'lock_policy')
            assert call['method']==expected_method
        print(label,'FINALIZED / SUCCESS / NORMAL')

    for rid,pid,case in [('1','1','ready'),('2','2','rejected')]:
        policy=read('get_policy',[pid])
        receipt=read('get_receipt',[rid])
        recorded=json.loads((ROOT/f'docs/live/{case}-receipt.json').read_text())
        assert receipt==recorded,'State changed; review all new attempts before updating the evidence record'
        verify(policy,receipt)
        report=receipt['history'][-1]['report']
        assert report['outcome']==STATE['recorded_outcomes'][rid]
        # These actual runs proved fail-closed behavior, not a positive semantic review.
        assert report['reason']=='SEMANTIC_OUTPUT_INVALID' and report['semantic']==[]
        for role in ['card','evaluation']:
            doc=receipt[role]
            response=requests.get(doc['url'],timeout=45)
            response.raise_for_status()
            body=response.content
            assert len(body)==doc['bytes'] and hashlib.sha256(body).hexdigest()==doc['sha256']
        print('release',rid,report['outcome'],report['reason'])
    print('Live source, finality, consensus, evidence and receipt integrity verified.')
    print('Limitation: neither recorded run completed semantic findings; no RELEASE_READY claim is established.')


if __name__=='__main__':
    main()

