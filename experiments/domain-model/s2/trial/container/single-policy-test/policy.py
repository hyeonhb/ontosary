"""Strict offline OCI fixture comparison; no runtime identity normalization."""
import copy
RULE={'names':['clone'],'action':'SCMP_ACT_ALLOW','args':[{'index':0,'op':'SCMP_CMP_EQ','value':2013397009}]}
def verify(candidate,baseline):
 expected=copy.deepcopy(baseline['Spec']);expected['linux']['seccomp']['syscalls'].append(copy.deepcopy(RULE))
 assert candidate['Spec']==expected,'policy-or-security-mismatch'
 return {'exactAddedRule':RULE,'otherSecurityUnchanged':True,'scope':'offline-identical-identity-fixture-only'}
