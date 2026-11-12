"""Audit the bounded preboot stop and explicit immutable historical/current scopes."""
import hashlib,json,pathlib
from scope import verify,classify
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit(work):
 budget=json.loads((work/'budget.json').read_text());events=budget['events']
 preparation=[e for e in events if e['command'][-1].endswith('/host-prepare.py')]
 assert len(preparation)==1 and preparation[0]['exitCode']==124 and preparation[0]['timeoutSeconds']==450
 assert not (work/'inputs.tar.gz').exists() and not (work/'guest-evidence.tar.gz').exists()
 cleanup=json.loads((work/'host-cleanup.json').read_text())
 assert cleanup['rootAbsent'] and cleanup['vmBefore']=='Stopped' and not cleanup['vmList'].strip() and not cleanup['ownedProcessesRemaining'] and cleanup['containersCreated']==0
 assert all(not c['existsAfter'] for c in cleanup['cache'] if not c['existedBefore'])
 assert any(c.get('incomplete') and c['partialBytes']==784252928 and c['removed'] for c in cleanup['cache'])
 previous=pathlib.Path('experiments/domain-model/s2/verification/2026-11-11-namespace-diagnosis/snapshots');prior=json.loads((work/'prior-snapshot-scope.json').read_text())
 classify(previous,prior['analysis'],prior['closing']);past=verify(previous,prior['analysis']);assert past==json.loads((work/'prior-scope-audit.json').read_text()) and past['snapshotsVerified']==11
 unchanged=json.loads((work/'start-input-hashes.json').read_text())
 for name,digest in unchanged.items():assert sha(pathlib.Path(name))==digest,name
 current=verify(work/'snapshots',json.loads((work/'analysis-scope.json').read_text()))
 return {'completion':'bounded-stop-completed','outcome':'inconclusive','blockedReasons':['preboot-image-download-command-timeout'],'environmentDeadlineMinutes':20,'commandTimeoutSeconds':450,'commandTimeoutWasEarlierThanEnvironmentDeadline':True,'vmAttempts':1,'guestBoots':0,'containers':0,'candidateApplications':0,'candidateStarts':0,'actualOCIPolicyComparisons':0,'tracedCLIInvocations':0,'credentialTransfers':0,'logins':0,'refreshes':0,'providerRequests':0,'modelCalls':0,'trialRuns':0,'preStartMechanicalCorrections':0,'runtimeRetries':0,'originalInputsUnchanged':len(unchanged),'historicalAnalysis':past,'historicalClosing':prior['closing'],'snapshots':current,'fixtureOnly':True,'validSubmission':False,'trialAuthorized':False,'readyForTrial':False,'results':None,'R11':'unresolved','R12':'prior verified scope unchanged','cleanup':'passed','note':'No original/candidate runtime observation. Draft unit helpers in earlier snapshots were never dispatched and are omitted from final tool tree.'}
if __name__=='__main__':
 work=pathlib.Path('work/s2-single-policy-test');result=audit(work);(work/'audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
