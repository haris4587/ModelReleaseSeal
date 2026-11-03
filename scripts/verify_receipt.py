"""Verify receipt integrity OFFLINE; this does not authenticate on-chain execution."""
import argparse
import hashlib
import json
from pathlib import Path


def digest(value):
    raw=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)
    return hashlib.sha256(raw.encode()).hexdigest()


def verify(policy, receipt):
    p=dict(policy)
    policy_hash=p.pop('policy_hash')
    if digest(p)!=policy_hash or policy_hash!=receipt['policy_hash']:
        raise ValueError('Policy hash mismatch')
    if receipt['policy_id']!=policy['id'] or receipt['creator']!=policy['creator'] or receipt['version']!=policy['version']:
        raise ValueError('Policy/release binding mismatch')
    base={k:v for k,v in receipt.items() if k not in ['history','commitment']}
    if digest(base)!=receipt['commitment']:
        raise ValueError('Release commitment mismatch')
    if not 0<=len(receipt['history'])<=3:
        raise ValueError('History size')
    previous=receipt['commitment']
    for number,entry in enumerate(receipt['history'],1):
        if entry['attempt']!=number or entry['previous_hash']!=previous or entry['commitment']!=receipt['commitment']:
            raise ValueError('History link mismatch')
        if digest({k:v for k,v in entry.items() if k!='decision_hash'})!=entry['decision_hash']:
            raise ValueError('Decision hash mismatch')
        previous=entry['decision_hash']
    return {'integrity':'VALID','attempts':len(receipt['history']),'anchor':'UNVERIFIED_OFFLINE',
            'notice':'Verify deployed source, network, address, finalized successful transactions and complete state separately.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('policy',type=Path)
    parser.add_argument('receipt',type=Path)
    args=parser.parse_args()
    print(json.dumps(verify(json.loads(args.policy.read_text()),json.loads(args.receipt.read_text())),indent=2))

