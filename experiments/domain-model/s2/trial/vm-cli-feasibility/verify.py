"""Verify the stopped, zero-runtime record. Never infer VM feasibility from it."""
import argparse
import datetime
import hashlib
import json
import pathlib
import sys
import tempfile
import time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(HERE.parent / 'container/lifecycle'))
from collector import open_directory, read_regular


def require(value, message):
    if not value:
        raise ValueError(message)


def regular(path, end):
    fd = open_directory(path.parent)
    try:
        before = path.lstat()
        require(before.st_size <= 2 * 1024**2, 'file byte limit')
        with tempfile.TemporaryDirectory() as tmp:
            copy = pathlib.Path(tmp) / 'verified'
            meta = read_regular(fd, path.name, before, end, copy)
            data = copy.read_bytes()
        require(hashlib.sha256(data).hexdigest() == meta['sha256'], 'changed input')
        return data, meta
    finally:
        import os
        os.close(fd)


def validate_record(result, stop, first, closure):
    require(result['status'] == 'inconclusive', 'only stopped inconclusive evidence is supported')
    require(result['reason'] == '15-minute-minimum-implementation-and-cleanup-gate-missed', 'stop reason')
    require(stop['reason'] == result['reason'] and stop['status'] == result['status'], 'stop/result mismatch')
    start = datetime.datetime.fromisoformat(first['utc'])
    gate = datetime.datetime.fromisoformat(stop['gateUtc'])
    detected = datetime.datetime.fromisoformat(stop['detectedUtc'])
    require((gate - start).total_seconds() == 900, 'gate reset')
    require(stop['gateMonotonic'] == first['monotonic'] + 900, 'monotonic gate reset')
    require(detected > gate and abs((detected - start).total_seconds() - stop['detectedElapsedSeconds']) < .01, 'gate observation')
    require(stop['firstCommand'] == first, 'first command mismatch')
    require(stop['gatePassed'] is False and stop['actualExperimentsStopped'] is True, 'stop not enforced')
    require(stop['executionCodeHashes'] is None and result['executionCodeHashes'] is None, 'unexecuted code claimed as executed')
    require(result['fixtureOnly'] is True, 'fixture classification')
    for name in ['validSubmission', 'trialAuthorized', 'readyForTrial', 'runtimeVerified']:
        require(result[name] is False, 'unauthorized promotion: ' + name)
    require(result['results'] is None and result['actualUnits'] == [], 'unobserved runtime results')
    require(result['requiredUnits'] == ['normal-1', 'timeout', 'wrapper-death', 'normal-2'], 'unit denominator')
    require(result['observedUnits'] == 0, 'unit observations')
    counters = ['vmAttempts', 'fixtureAttempts', 'cliDiscoveryCalls', 'sandboxCalls', 'downloads', 'builds',
                'imageSaves', 'vendureInstalls', 'credentialTransfers', 'logins', 'refreshes', 'providerRequests', 'modelCalls', 'trialRuns']
    for key in counters:
        require(type(result['counts'][key]) is int and result['counts'][key] == 0, 'nonzero or invalid counter: ' + key)
    for key in ['vmAttempts', 'fixtureAttempts', 'cliDiscoveryCalls', 'sandboxCalls']:
        require(type(stop[key]) is int and stop[key] == result['counts'][key], 'stop counter mismatch: ' + key)
    require(result['cleanupStatus'] == closure['cleanupStatus'] == 'not-created', 'cleanup status')
    require(result['recoveryStatus'] == 'not-applicable-no-guest', 'recovery status')
    require(closure['ownershipRecords'] == [] and closure['executionRegistrations'] == [] and closure['ownedProcesses'] == [], 'owned state remains')
    require(len(closure['prospectiveRoots']) == 2 and all(v is False for v in closure['prospectiveRoots'].values()), 'prospective roots')
    require(closure['vmDeletionVerified'] is False, 'no VM deletion occurred')


def verify(directory, root=ROOT):
    directory = pathlib.Path(directory).resolve()
    end = time.monotonic() + 20
    raw, _ = regular(directory / 'index.json', end)
    index = json.loads(raw)
    require(index['schema'] == 'ontosary-vm-stopped-record-v1', 'index schema')
    files = index['files']
    require(0 < len(files) <= 128, 'file count limit')
    require(all(pathlib.PurePosixPath(n).name == n and n not in ['.', '..', 'index.json'] for n in files), 'index path')
    require({p.name for p in directory.iterdir()} == set(files) | {'index.json'}, 'unindexed evidence')
    data = {}
    total = 0
    for name, expected in files.items():
        body, actual = regular(directory / name, end)
        require(actual == expected, 'evidence hash/size: ' + name)
        total += actual['bytes']
        require(total <= 16 * 1024**2, 'aggregate byte limit')
        if name.endswith('.json'):
            data[name] = json.loads(body)
    for required in ['result.json', 'stop.json', 'first-command.json', 'closure.json', 'public-cache.json', 'immutability.json', 'validation.json']:
        require(required in data, 'missing required evidence: ' + required)
    validate_record(data['result.json'], data['stop.json'], data['first-command.json'], data['closure.json'])
    cache = data['public-cache.json']
    require(len(cache['records']) == 4 and cache['downloads'] == cache['builds'] == 0, 'cache observations')
    # Store.usage() includes registered metadata as well as the four archive bodies.
    require(sum(r['actual']['bytes'] for r in cache['records']) <= cache['bytes'] <= 10 * 1024**3, 'cache bytes')
    for row in cache['records']:
        require(row['cacheHit'] is True and row['actual']['sha256'] == row['request']['sha256'], 'cache provenance')
    hashes = index['sourceHashes']
    expected_sources = {str(p.relative_to(root)) for p in HERE.iterdir() if p.suffix in ['.py', '.mjs']}
    require(set(hashes) == expected_sources, 'source inventory')
    old = data['immutability.json']
    require(old['changed'] == [] and old['missing'] == [], 'historical evidence changed')
    require(old['checkedCount'] == len(old['hashes']), 'historical file count')
    for name, expected in {**old['hashes'], **hashes}.items():
        path = pathlib.PurePosixPath(name)
        require(not path.is_absolute() and '..' not in path.parts, 'source path')
        require(time.monotonic() < end, 'verification deadline')
        require(hashlib.sha256((root / name).read_bytes()).hexdigest() == expected, 'source/history hash: ' + name)
    require(data['validation.json']['pnpmCheck']['exitCode'] == 0 and data['validation.json']['localTests']['exitCode'] == 0, 'local validation failed')
    return {'verificationStatus': 'consistent-inconclusive-record', 'runtimeVerified': False,
            'status': 'inconclusive', 'observedUnits': 0, 'requiredUnits': 4,
            'filesChecked': len(files), 'historicalFilesChecked': old['checkedCount']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=pathlib.Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.directory), indent=2))
