"""Verify the intentionally narrow tracked change scope and local documentation links."""
import pathlib,re,subprocess,json,urllib.parse
names=['docs/PROGRESS.md','docs/ARCHITECTURE.md','docs/ROADMAP.md','docs/reviews/REVIEW_CONTEXT.md','docs/DECISIONS.md','docs/reviews/2026-11-12-s2-single-policy-test.md']
changed=subprocess.check_output(['git','diff','--name-only','HEAD'],text=True).splitlines()
assert all(p in names or p.startswith('experiments/domain-model/s2/trial/container/single-policy-test/') or p.startswith('experiments/domain-model/s2/verification/2026-11-12-single-policy-test/') for p in changed),changed
links=0
for name in names:
 p=pathlib.Path(name)
 for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  if target.startswith(('http:','https:','#','mailto:')):continue
  target=urllib.parse.unquote(target.split('#')[0]);assert (p.parent/target).exists(),(name,target);links+=1
print(json.dumps({'changedTrackedPaths':changed,'localLinksChecked':links,'scopePassed':True}))
