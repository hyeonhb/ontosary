"""Close this bounded stop after offline verification; do not reset the first clock."""
import datetime,json,pathlib,re,subprocess,time
from snapshot import snapshot
work=pathlib.Path('work/s2-single-policy-test');base=pathlib.Path('experiments/domain-model/s2/trial/container/single-policy-test');budget=json.loads((work/'budget.json').read_text())
snapshot(work,['python3',str(base/'close.py')])
# Preliminary cost enables real link checking before final accounting.
(work/'cost.json').write_text(json.dumps({'status':'preliminary-finalization-in-progress'})+'\n')
def run(name,args):
 with (work/name).open('w') as f:subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=30)
run('package-before-close.log',['python3',str(base/'package.py')])
run('saved-verification.log',['python3',str(base/'verify-saved.py')])
run('links-final.log',['python3',str(base/'verify-repository.py')])
now=datetime.datetime.now(datetime.timezone.utc);mono=time.monotonic();seconds=mono-budget['monotonic'];cumulative=budget['previousCumulativeSeconds']+seconds
assert seconds+5<45*60
cost={'status':'closed','startedUtc':budget['utc'],'measurementEndedUtc':now.isoformat(),'startedMonotonic':budget['monotonic'],'endedMonotonic':mono,'measuredSeconds':seconds,'previousCumulativeSeconds':budget['previousCumulativeSeconds'],'measuredCumulativeSeconds':cumulative,'finalSerializationAllowanceSeconds':5,'conservativeRoundUpperBoundSeconds':seconds+5,'conservativeCumulativeUpperBoundSeconds':cumulative+5,'newPaidCost':0,'gitDeliveryIncluded':False,'runtimeRetries':0,'preStartMechanicalCorrections':0,'verificationCorrection':'first local-link check preceded cost creation; final check passed after cost creation','completion':'bounded-stop-completed','outcome':'inconclusive'}
(work/'cost.json').write_text(json.dumps(cost,indent=2)+'\n')
p=pathlib.Path('docs/reviews/2026-11-12-s2-single-policy-test.md');s=p.read_text().replace('ROUND_SECONDS',f'{seconds:.3f}').replace('CUMULATIVE_SECONDS',f'{cumulative:.3f}');s=re.sub(r'회차 비용: \*\*[0-9.]+초\*\*, 이전 누적11408.175213083973초, 새 누적 \*\*[0-9.]+초\*\*',f'회차 비용: **{seconds:.3f}초**, 이전 누적11408.175213083973초, 새 누적 **{cumulative:.3f}초**',s);s=s.replace('종료 증거 직렬화/최종 index 생성의 작은 후처리 시간은 cost의 측정 구간과 함께 구분한다.','최종 cost/index 직렬화에는 별도 최대5초를 포함한 보수적 상한을 기록하며 그 안에 종료했는지 검사한다.');p.write_text(s)
run('package-final.log',['python3',str(base/'package.py')])
# Avoid another mutable log in the delivered index after its creation.
subprocess.run(['python3',str(base/'verify-saved.py')],check=True,timeout=3)
subprocess.run(['python3',str(base/'verify-repository.py')],check=True,timeout=3)
tail=time.monotonic()-mono;assert tail<=5
print(json.dumps({'measuredSeconds':seconds,'finalSerializationSeconds':tail,'roundSecondsIncludingSerialization':seconds+tail,'upperBoundSeconds':seconds+5,'finishedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat()}))
