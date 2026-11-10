import { hash, stable } from './analysis-session.js';
// No new interpretation is generated here: quoted claims/limitations come from the frozen B views.
type Data = Record<string, any>;
export interface Unit { id:string; view:string; pointer:string; value:unknown; kind:string; C:{file:string;startLine:number;endLine:number;sha256:string}; transformation:string; sourceEvidence:string[]; automatic:string; developerReview:string; }
export function leaves(value:unknown,pointer=''): {pointer:string;value:unknown}[] {
    if(value&&typeof value==='object'&&Object.keys(value).length) return Object.entries(value).flatMap(([k,v])=>leaves(v,pointer+'/'+k.replaceAll('~','~0').replaceAll('/','~1')));
    return [{pointer,value}];
}
const literal=(v:unknown)=>JSON.stringify(v).replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('|','&#124;');
export function proseViews(views:Map<string,unknown>) {
    const files=new Map<string,string>(), units:Unit[]=[], docs=new Map<string,string[]>();
    const starts:Record<string,string>={
        'C/guide.md':'# 개념과 클라이언트 흐름\n\n[코드 관찰](observations.md) · [역할 후보](roles.md) · [원문과 식별 정보](evidence.md)\n',
        'C/observations.md':'# 코드 관찰과 범위\n\n[개념과 흐름](guide.md) · [원문과 식별 정보](evidence.md)\n',
        'C/roles.md':'# 공통 역할 후보\n\n[개념과 흐름](guide.md) · [원문과 식별 정보](evidence.md)\n',
        'C/evidence.md':'# 원문과 재현 메타데이터\n\n[개념과 흐름](guide.md) · [코드 관찰](observations.md)\n\n아래 원문·식별자·좌표·조회 상태는 변경 전 자료의 재현 정보를 보존한다.\n',
    };
    for(const [file,start] of Object.entries(starts))docs.set(file,start.split('\n'));
    for(const [view,raw] of views) {
        const d=raw as Data, all=leaves(raw), used=new Set<string>();
        const evidence=all.filter(x=>x.pointer.endsWith('/sha256')).map(x=>String(x.value));
        function emit(file:string,text:string,paths:string[],kind='statement') {
            const lines=docs.get(file)!, startLine=lines.length+1;lines.push(...text.split('\n'));if(kind!=='metadata')lines.push('');
            const covered=all.filter(x=>!used.has(x.pointer)&&paths.some(p=>x.pointer===p||x.pointer.startsWith(p+'/')));
            for(const x of covered) {
                used.add(x.pointer);
                units.push({id:view+'#'+x.pointer,view:'B/views/'+view+'.json',pointer:x.pointer,value:x.value,kind,C:{file,startLine,endLine:startLine+text.split('\n').length-1,sha256:hash(text)},transformation:kind==='metadata'?'verbatim metadata':'template with verbatim source values',sourceEvidence:[...new Set(evidence)],automatic:'coverage-and-text-integrity-only',developerReview:'pending'});
            }
        }
        const title=(file:string,text:string)=>{docs.get(file)!.push('','## '+view+' — '+text,'');};
        if(view==='status') {
            title('C/guide.md','자료의 상태와 한계');
            emit('C/guide.md',`이 자료의 내용 무결성은 ${literal(d.integrity)}, 변경 전 근거 검사는 ${literal(d.baselineEvidence)}다. 업무 의미 검토는 ${literal(d.semanticReview)}이며, 자료의 기준은 ${literal(d.sourceVersion)}이다. 현재 작업 소스에 대한 평가는 ${literal(d.currentWorkspaceAssessment)}다. 적용 범위: ${d.coverage}.`,['/integrity','/baselineEvidence','/semanticReview','/sourceVersion','/currentWorkspaceAssessment','/coverage'],'status');
        } else if(view==='index') {
            title('C/guide.md','찾아가기');
            (raw as Data[]).forEach((x,i)=>emit('C/guide.md',`- ${x.label}: 항목 식별자 ${literal(x.id)}. 아래 항목 절에서 해석·근거·관련 관계를 함께 읽는다.`,['/'+i],'navigation'));
        } else if(view.startsWith('item-')) {
            const item=d.item.value,s=item.source;
            title('C/guide.md',s.label);
            emit('C/guide.md',`${s.label}: ${s.interpretation}\n\n이 항목은 ${literal(s.kind)}이며 상태는 ${literal(s.status)}, 작성 주체는 ${literal(s.author)}다. 의도한 정책 기록: ${literal(s.intendedPolicy)}. 미확인 질문: ${(s.unverified as unknown[]).map(literal).join('; ')||'없음'}.`,['/item/value/source/label','/item/value/source/interpretation','/item/value/source/kind','/item/value/source/status','/item/value/source/author','/item/value/source/intendedPolicy','/item/value/source/unverified']);
            emit('C/guide.md',`연결된 코드 사실: ${literal(item.factRefs)}. 발견 후보 참조: ${literal(item.candidateRefs)}. 원문 연결은 아래 부록의 동일 식별자로 찾는다.`,['/item/value/factRefs','/item/value/candidateRefs'],'reference');
            d.neighbors.value.forEach((e:Data,i:number)=>emit('C/guide.md',`관계 ${literal(e.kind)}는 ${literal(e.from)}에서 ${literal(e.to)}로 향한다. 이 항목에서 본 방향은 ${literal(e.direction)}이며 기록 근거는 ${literal(e.provenance)}다.`,['/neighbors/value/'+i],'relation'));
        } else if(view.startsWith('fact-')) {
            const s=d.value.source;
            title('C/observations.md',s.id);
            emit('C/observations.md',`${s.claim}\n\n관찰 종류는 ${literal(s.kind)}, 주체는 ${literal(s.author)}, 방법은 ${literal(s.method)}다. 지원 수준: ${s.support}. 범위와 한계: ${s.scope}.`,['/value/source/claim','/value/source/kind','/value/source/author','/value/source/method','/value/source/support','/value/source/scope']);
            if('object' in s)emit('C/observations.md',`멤버 ${literal(s.object)}에 대해 역할 ${literal(s.attribute)}의 관찰값은 ${literal(s.value)}다. 추가 사유 기록: ${literal(s.reasons)}.`,['/value/source/object','/value/source/attribute','/value/source/value','/value/source/reasons']);
        } else if(view.startsWith('candidate-')) {
            const c=d.candidate.value;
            title('C/roles.md',c.id);
            const members=(c.extent as string[]).map(id=>{const o=d.objects.find((o:Data)=>o.id===id);if(!o)throw Error('Candidate member absent');return o.class+'.'+o.name+'()';});
            emit('C/roles.md',`이 후보에 묶인 멤버는 ${members.join(', ')}다. 공통 역할 집합은 ${literal(c.intent)}이며 상태는 ${literal(c.source.status)}다. 멤버 집합과 근거 사실의 식별자, 선언과 원문 좌표는 부록의 ${view} 절에 보존되어 있다.`,['/candidate/value/extent','/candidate/value/intent','/candidate/value/source/status'],'candidate');
        } else if(view.startsWith('evidence-')) {
            const e=d.value;
            title('C/evidence.md',e.id);
            emit('C/evidence.md',`원문 ${literal(e.file)}, ${e.line}행 ${e.column}열, UTF-16 구간 [${e.offset}, ${e.end})의 ${literal(e.sourceVersion)} 인용:\n\n~~~text\n${e.text}\n~~~`,['/value/text','/value/file','/value/line','/value/column','/value/offset','/value/end','/value/sourceVersion'],'source-quote');
        } else throw Error('Unreviewed C view kind: '+view);
        // Only reproduction metadata remains; semantic clauses above are never hidden in this table.
        const remaining=all.filter(x=>!used.has(x.pointer));
        if(remaining.length) {title('C/evidence.md',view+' 식별·참조·조회·원문 좌표');
        docs.get('C/evidence.md')!.push('| 기록 경로 | 보존 값 |','| --- | --- |');}
        for(const x of remaining)emit('C/evidence.md',`| ${x.pointer} | ${literal(x.value)} |`,[x.pointer],'metadata');
    }
    for(const [file,lines] of docs)files.set(file,lines.join('\n').replace(/\n+$/, '')+'\n');
    return {files,units};
}
/** Detect drift, omissions/additions/duplicates; does NOT prove translation semantics. */
export function auditProse(views:Map<string,unknown>, documents:Map<string,string>, inventory:Unit[]) {
    const expected=proseViews(views), errors:string[]=[];
    const ids=inventory.map(x=>x.id);
    if(new Set(ids).size!==ids.length)errors.push('duplicate units');
    if(stable(ids.slice().sort())!==stable(expected.units.map(x=>x.id).sort()))errors.push('missing/additional units');
    if(stable(inventory)!==stable(expected.units))errors.push('mapping/value drift');
    if(stable([...documents].sort())!==stable([...expected.files].sort()))errors.push('C text/structure drift: developer and human re-review required');
    return {pass:errors.length===0,errors,units:expected.units.length,views:views.size,meaningProven:false,humanParityReview:'pending'};
}
