"""Read only an allowlisted non-secret config value and filesystem metadata; never auth contents."""
import json,os,pathlib,stat,tomllib
root=pathlib.Path(os.environ.get('CODEX_HOME',str(pathlib.Path.home()/'.codex')))
config=root/'config.toml';record={'scope':'host metadata only; not copied into guest','codeHomeOverridePresent':'CODEX_HOME' in os.environ,'configPresent':config.is_file(),'authenticationContentsRead':False,'keychainQueried':False,'accountIdentifiersRead':False}
if config.is_file():
 try:
  with config.open('rb') as f:value=tomllib.load(f).get('cli_auth_credentials_store')
  record['cli_auth_credentials_store']=value if value in ['file','keyring','auto','ephemeral'] else 'unset-or-unknown'
 except Exception:record['cli_auth_credentials_store']='unknown-parse-failed'
auth=root/'auth.json'
try:
 s=auth.lstat();record['authFile']={'exists':True,'mode':oct(stat.S_IMODE(s.st_mode)),'regular':stat.S_ISREG(s.st_mode),'symlink':stat.S_ISLNK(s.st_mode)}
except FileNotFoundError:record['authFile']={'exists':False}
record['effectiveStorage']='unknown; key presence/file metadata cannot prove the current active credential backend'
print(json.dumps(record,indent=2))
