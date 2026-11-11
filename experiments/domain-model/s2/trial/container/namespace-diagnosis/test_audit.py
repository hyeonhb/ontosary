"""Reject corrupted real archive metadata and altered security policy."""
import copy,json,pathlib,unittest
from audit import verify_inputs,verify_policy
ROOT=pathlib.Path('work/s2-namespace-diagnosis')
class EvidenceTests(unittest.TestCase):
 def test_actual_inputs(self):verify_inputs(ROOT/'inputs.tar.gz',json.loads((ROOT/'inputs.json').read_text()))
 def test_wrong_archive_hash(self):
  m=json.loads((ROOT/'inputs.json').read_text());m['archiveSha256']='0'*64
  with self.assertRaisesRegex(AssertionError,'archive-hash'):verify_inputs(ROOT/'inputs.tar.gz',m)
 def test_wrong_policy_member_hash(self):
  m=json.loads((ROOT/'inputs.json').read_text());m['members']['policy.toml']='0'*64
  with self.assertRaisesRegex(AssertionError,'member-hash'):verify_inputs(ROOT/'inputs.tar.gz',m)
 def test_added_namespace_allow_is_rejected(self):
  old=json.loads((ROOT/'prior-native.json').read_text());changed=copy.deepcopy(old);changed['Spec']['linux']['seccomp']['syscalls'].append({'names':['clone'],'action':'SCMP_ACT_ALLOW'})
  with self.assertRaisesRegex(AssertionError,'policy-mismatch'):verify_policy(changed,old)
 def test_disabled_nnp_is_rejected(self):
  old=json.loads((ROOT/'prior-native.json').read_text());changed=copy.deepcopy(old);changed['Spec']['process']['noNewPrivileges']=False
  with self.assertRaisesRegex(AssertionError,'policy-mismatch'):verify_policy(changed,old)
if __name__=='__main__':unittest.main(verbosity=2)
