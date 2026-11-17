"""Bounded offline replay and topological interleavings for the R18 contract."""
import hashlib,json,pathlib,sys
sys.path.insert(0,str(pathlib.Path.cwd()/'experiments/domain-model/s2/trial/container/execution-lifecycle'))
import trace_reanalysis as t
old=json.loads(pathlib.Path('docs/reviews/evidence/2026-11-17-s2-trace-reanalysis-independent.json').read_text())['probe']['cases']
replay=[]
for case in old:
 r=t.parse_trace(case['trace']);expected='first-clone-passed-next-blocked' if case['name']=='supported_denial_before_resume' else 'inconclusive';assert r['status']==expected
 replay.append({'case':case['name'],'previous':case['status'],'current':r['status'],'issues':r['issues'],'admittedChildPids':[d['pid'] for d in r['nextDenied']]})
def orders(nodes,edges,done=()):
 if len(done)==len(nodes):yield done;return
 for name in nodes:
  if name not in done and all(a in done for a,b in edges if b==name):yield from orders(nodes,edges,done+(name,))
checks=[]
for with_exec in [False,True]:
 nodes={};edges=[]
 for role,pid,child,arg in [('a',41,42,'/usr/bin/true'),('b',43,44,'/usr/local/bin/node')]:
  e,s,r,d=[role+x for x in ['exec','start','return','denial']]
  nodes.update({e:f'[pid {pid}] execve("/proc/self/fd/3", ["bwrap", "{arg}"], 0) = 0',s:f'[pid {pid}] {t.START} <unfinished ...>',r:f'[pid {pid}] <... clone resumed>) = {child}',d:f'[pid {child}] mount(NULL, "/", NULL, MS_SLAVE, NULL) = -1 EPERM (Operation not permitted)'})
  edges += [(e,s),(s,r),(s,d)]
  if with_exec and role=='a':
   x='aChildExec';nodes[x]='[pid 42] execve("/other", ["other"], 0) = 0';edges += [(s,x),(x,d)]
 count=0;sha=hashlib.sha256();expected='inconclusive' if with_exec else 'first-clone-passed-next-blocked'
 for order in orders(nodes,edges):
  count+=1;assert count<=10000
  trace='\n'.join(nodes[n] for n in order)+'\n';sha.update(trace.encode());r=t.parse_trace(trace)
  assert r['status']==expected,(order,r)
  if with_exec:assert [d['pid'] for d in r['nextDenied']]==[44]
 checks.append({'childExec':with_exec,'ordersChecked':count,'expectedStatus':expected,'traceSetSha256':sha.hexdigest()})
print(json.dumps({'runtimeExecutions':0,'originalProbeReplay':replay,'interleavings':checks},indent=2))
