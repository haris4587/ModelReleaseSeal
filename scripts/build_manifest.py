"""Build byte-exact evidence manifests and Studio arguments."""
import argparse
import hashlib
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def build(commit, case):
    if not re.fullmatch('[0-9a-f]{40}', commit):
        raise ValueError('Full 40-character commit SHA required')
    if case not in ['ready','conditional','rejected','inconclusive','conflict','injection']:
        raise ValueError('Unknown fixture')
    docs = {}
    for role in ['card','evaluation']:
        path=f'fixtures/{case}-{role}.txt'
        body=(ROOT/path).read_bytes()
        docs[role]={'url':f'https://raw.githubusercontent.com/haris4587/ModelReleaseSeal/{commit}/{path}',
                    'sha256':hashlib.sha256(body).hexdigest(),'bytes':len(body)}
    return {'fixture_notice':'Synthetic educational evidence; no real model was tested.',
            'fixture_commit':commit,
            'lock_policy':{'policy_json':json.dumps(json.loads((ROOT/'fixtures/policy.json').read_text()),sort_keys=True,separators=(',',':'))},
            'submit_release':{'policy_id':'REPLACE_WITH_RETURNED_POLICY_ID',
                              'model_sha256':(ROOT/'fixtures/model-sha256.txt').read_text().strip(),
                              'evidence_json':json.dumps(docs,sort_keys=True,separators=(',',':'))},
            'evaluate_release':{'release_id':'REPLACE_WITH_RETURNED_RELEASE_ID'}}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('commit')
    parser.add_argument('--case',default='ready')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    output=json.dumps(build(args.commit,args.case),indent=2,ensure_ascii=False)+'\n'
    if args.output:
        args.output.write_text(output)
    else:
        print(output,end='')

