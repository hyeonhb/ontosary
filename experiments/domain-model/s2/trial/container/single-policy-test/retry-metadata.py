"""Read only this disposable guest's named policy metadata; do not change policy."""
import hashlib,json,pathlib,subprocess
root=pathlib.Path('/opt/ontosary-policy-retry');out=root/'metadata';out.mkdir()
rows=[]
for args in [['nerdctl','apparmor','inspect'],['apparmor_parser','--version']]:
 p=subprocess.run(args,capture_output=True,text=True,timeout=5);rows.append({'command':args,'exitCode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
kernel=subprocess.check_output(['uname','-r'],text=True).strip();config=pathlib.Path('/boot/config-'+kernel)
keys=['CONFIG_USER_NS','CONFIG_NAMESPACES','CONFIG_SECCOMP','CONFIG_SECCOMP_FILTER','CONFIG_SECURITY_APPARMOR']
selected=[line for line in config.read_text().splitlines() if any(line.startswith(k+'=') for k in keys)] if config.exists() else []
profiles=pathlib.Path('/sys/kernel/security/apparmor/profiles');named=[line for line in profiles.read_text().splitlines() if line.startswith('nerdctl-default ')] if profiles.exists() else []
result={'commands':rows,'kernel':kernel,'kernelConfiguration':selected,'namedLoadedProfile':named,'profileDumpMeaning':'Generated default template, not a dump of loaded compiled kernel policy. Named loaded profile and worker proc attachment are separate evidence.','runtimeDefaultPolicyChanged':False}
(out/'metadata.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'kernel':kernel,'namedLoadedProfile':named,'runtimeDefaultPolicyChanged':False}))
