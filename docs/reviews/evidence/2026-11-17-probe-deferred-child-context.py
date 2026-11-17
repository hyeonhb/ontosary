"""Host-only deferred child-context probe; no runtime or saved evidence changes."""
import json,pathlib,sys
sys.path.insert(0,str(pathlib.Path.cwd()/'experiments/domain-model/s2/trial/container/execution-lifecycle'))
import trace_reanalysis as t

def exec_line(pid,cmd):return f'[pid {pid}] execve("/proc/self/fd/3", ["bwrap", "{cmd}"], 0) = 0'
def denial(pid):return f'[pid {pid}] mount(NULL, "/", NULL, MS_REC|MS_SILENT|MS_SLAVE, NULL) = -1 EPERM (Operation not permitted)'
start=[exec_line(41,'/usr/bin/true'),f'[pid 41] {t.START} <unfinished ...>']
resume='[pid 41] <... clone resumed>) = 42'
child_exec='[pid 42] execve("/usr/bin/other", ["other"], 0) = 0'
rest=[exec_line(43,'/usr/local/bin/node'),f'[pid 43] {t.START}) = 44',denial(44)]
cases={
 'resume_before_child_exec':start+[resume,child_exec,denial(42)]+rest,
 'resume_after_child_exec':start+[child_exec,denial(42),resume]+rest,
 'supported_denial_before_resume':start+[denial(42),resume]+rest,
}
rows=[]
for name,lines in cases.items():
 result=t.parse_trace('\n'.join(lines)+'\n')
 rows.append({'name':name,'trace':'\n'.join(lines)+'\n','status':result['status'],'issues':result['issues'],'nextDenied':result['nextDenied']})
assert rows[0]['status']=='inconclusive'
assert rows[1]['status']=='first-clone-passed-next-blocked' and not rows[1]['issues']
assert rows[2]['status']=='first-clone-passed-next-blocked'
print(json.dumps({'runtimeExecutions':0,'cases':rows},indent=2))
