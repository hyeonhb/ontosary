"""Build-input lookup, independently verified output binding. No reproducibility claim."""
import hashlib,json,os,pathlib,tarfile,time,uuid
from artifacts import canonical,digest_file,verify_image_archive,Rejected
BASE='docker.io/library/node@sha256:4a4884e8a44826194dff92ba316264f392056cbe243dcc9fd3551e71cea02b90'
BUNDLE='fe0ef0e9840ee8932640e6058f84b7fa98050f9726e44af44883a5b804ae830e'
def build_inputs(dockerfile,base=BASE,tools=None):
 return {'schema':'s2-image-input-v1','context':{'Dockerfile':{'sha256':hashlib.sha256(dockerfile).hexdigest(),'bytes':len(dockerfile)}},'buildArgs':{'BASE_IMAGE':base},'platform':'linux/arm64','tools':tools or {'nerdctl':'2.4.2','containerd':'2.4.2-b7a25261e029d68978bbf290df0a62fc819b3c51','runc':'1.5.2','fullBundleSha256':BUNDLE}}
def key(inputs):return hashlib.sha256(canonical(inputs)).hexdigest()
class ImageCache:
 def __init__(self,store):self.store=store
 def _path(self,inputs):return self.store.root/('.image-key-'+key(inputs)+'.json')
 def _lookup(self,inputs,end):
  path=self._path(inputs)
  self.store.usage()
  if not path.exists():return None
  if path.is_symlink() or path.stat().st_size>65536:raise Rejected('image-binding-file')
  record=json.loads(path.read_text())
  if record.get('schema')!='s2-image-binding-v1' or record.get('inputs')!=inputs or record.get('key')!=key(inputs):raise Rejected('image-input-binding')
  artifact=self.store._lookup(record['request'],end)
  if artifact is None or artifact['actual']!=record['output']:raise Rejected('image-artifact-binding')
  verified=verify_image_archive(artifact['path'],record['image'],end)
  return {'binding':record,'artifact':artifact,'archiveVerification':verified,'cacheHit':True}
 def lookup(self,inputs,end):
  with self.store.lock(end):return self._lookup(inputs,end)
 def bind(self,inputs,request,image,provenance,end):
  with self.store.lock(end):
   found=self._lookup(inputs,end)
   if found:
    if found['binding']['request']!=request or found['binding']['image']!=image:raise Rejected('image-key-conflict')
    return found
   artifact=self.store._lookup(request,end)
   if artifact is None:raise Rejected('unregistered-image-output')
   verify_image_archive(artifact['path'],image,end)
   record={'schema':'s2-image-binding-v1','key':key(inputs),'inputs':inputs,'request':request,'output':artifact['actual'],'image':image,'provenance':provenance}
   data=canonical(record)+b'\n'
   if len(data)>65536 or self.store.usage()+len(data)>self.store.limit:raise Rejected('store-capacity')
   temp=self.store.root/('.binding-'+uuid.uuid4().hex)
   try:
    with temp.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
    os.chmod(temp,0o400);os.link(temp,self._path(inputs));temp.unlink()
   finally:
    if temp.exists():temp.unlink()
   return self._lookup(inputs,end)
 def legacy_link(self,inputs,host,end):
  """Bind only historical bytes whose recipe, build command and bundle are evidenced."""
  host=pathlib.Path(host)
  from scope import verify_index
  verify_index(host.parent)
  saved=json.loads((host/'image-artifact.json').read_text());req=saved['first']['request']
  transfer=json.loads((host/'input-transfer.json').read_text())
  if digest_file(host/'inputs.tar.gz',end)['sha256']!=transfer['archiveSha256']:raise Rejected('legacy-transfer')
  with tarfile.open(host/'inputs.tar.gz') as tar:
   members={m.name:m for m in tar if m.isfile()}
   if set(members)!=set(transfer['members']):raise Rejected('legacy-input-members')
   if [n for n in members if n.startswith('build/')]!=['build/Dockerfile']:raise Rejected('legacy-extra-build-context')
   docker=tar.extractfile(members['build/Dockerfile']).read()
  if build_inputs(docker)!=inputs:return None
  recipe=hashlib.sha256(docker).hexdigest()
  if recipe!=transfer['members']['build/Dockerfile'] or recipe!=req['buildInputHashes']['recipe'] or req['buildInputHashes']['baseImage']!=BASE.split('@')[1]:raise Rejected('legacy-recipe')
  acquisitions=json.loads((host/'artifact-acquisitions.json').read_text())
  bundle=next(r for r in acquisitions if r['request']['name']=='nerdctl-full-2.4.2-linux-arm64')
  if bundle['actual']['sha256']!=BUNDLE:raise Rejected('legacy-tool-bundle')
  with tarfile.open(host/'guest-evidence.tar.gz') as tar:events=[json.loads(x) for x in tar.extractfile('preparation/events.jsonl')]
  builds=[x for x in events if x.get('kind')=='command' and 'build' in x['command']]
  if len(builds)!=1 or builds[0]['exitCode']!=0 or builds[0]['command'][-6:]!=['build','--build-arg','BASE_IMAGE='+BASE,'-t','ontosary-s2-execution:trace','/opt/ontosary-execution/build']:raise Rejected('legacy-build-command')
  versions=events[0]['stdout']
  if not all(x in versions for x in ['nerdctl version 2.4.2','b7a25261e029d68978bbf290df0a62fc819b3c51','runc version 1.5.2']):raise Rejected('legacy-tool-version')
  proof={'kind':'validated-legacy-link','oldManifestUnmodified':True,'externalPackageQueriesFullyPinned':False,'evidence':{n:digest_file(host/n,end)['sha256'] for n in ['image-artifact.json','input-transfer.json','inputs.tar.gz','guest-evidence.tar.gz','artifact-acquisitions.json']}}
  return self.bind(inputs,req,req['image'],proof,end)
