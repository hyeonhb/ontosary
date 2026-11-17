"""Pure result gate: missing positive controls never establish isolation."""
def check(result,state,mode):
 reasons=[]
 def require(value,reason):
  if not value:reasons.append(reason)
 require(state.get('terminationConfirmed') and state.get('collectionStatus')=='collected','termination-or-collection')
 require(state.get('container')=='not-applicable','container-contract')
 require(result.get('uid')==22001 and result.get('gid')==22001,'worker-identity')
 require('CapEff:\t0000000000000000' in result.get('status','') and 'NoNewPrivs:\t1' in result.get('status',''),'worker-privilege')
 for k in ['credentialTransfers','logins','refreshes','providerRequests','modelCalls','trialRuns']:require(result.get(k)==0,'forbidden-call:'+k)
 require(result.get('nativePayloadStarted') is True,'native-sandbox-payload-not-started')
 p=result.get('payload') or {}
 require(p.get('started') is True and p.get('completed') is True,'payload-incomplete')
 for k in ['sourceRead','sourceWrite','materialRead','scratchWrite','homeWrite']:require(p.get('positive',{}).get(k) is True,'positive:'+k)
 for k in ['fakeDirect','fakeSymlink','controlDirect','otherRun','parentProcRoot','parentProcEnvironment','parentProcFd','inheritedFd','fakeEnvironment','materialWrite','outsideWrite','ipv4','unix']:
  require(p.get('denied',{}).get(k,{}).get('accessible') is False,'denial:'+k)
 for k in ['sourceRead','sourceWrite','materialRead','fakeFileExists','fakeEnvironmentPresent','controlCanaryReadable','fdOpen','procRootReadable','procEnvironmentPresent','procFdReadable']:require(result.get('parent',{}).get(k) is True,'parent:'+k)
 for k in ['ipv4','unix']:require(result.get('networkPositive',{}).get(k) is True,'network-positive:'+k)
 if 'ipv6' in result.get('networkPositive',{}):require(result['networkPositive']['ipv6'] and p.get('denied',{}).get('ipv6',{}).get('accessible') is False,'ipv6-boundary')
 else:require(result.get('networkNotApplicable',{}).get('ipv6',{}).get('status')=='not-applicable','ipv6-unaccounted')
 for k in ['sudo','serviceControl']:require(result.get('management',{}).get(k,{}).get('exitCode',0)!=0,'management:'+k)
 for k in ['cgroupMove','runtimeSocket','managerState','managerSSH','supervisorSignal']:require(result.get('management',{}).get(k,{}).get('accessible') is False,'management:'+k)
 require(result.get('configUnchanged') is True and result.get('materialsUnchanged') is True,'input-mutated')
 if mode.startswith('normal'):require(result.get('calls',[])[-1].get('exitCode')==0 if result.get('calls') else False,'sandbox-command-exit')
 require(not result.get('error'),'worker-error')
 return {'passed':not reasons,'reasons':reasons,'fixtureOnly':True,'validSubmission':False}
