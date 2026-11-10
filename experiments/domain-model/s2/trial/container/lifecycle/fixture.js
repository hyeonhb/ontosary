// Finite, known fixtures only; no Codex/provider/evaluator calls.
const fs=require('fs'),cp=require('child_process'),net=require('net');
const mode=process.argv[1], role=process.argv[2]||'main';
const put=(n,v)=>{const tmp='/source/.'+n+'.'+process.pid;fs.writeFileSync(tmp,typeof v==='string'||Buffer.isBuffer(v)?v:JSON.stringify(v));fs.renameSync(tmp,'/source/'+n);};
const code=process.env.FIXTURE_CODE;
if(role==='writer') {
 const fd=fs.openSync('/source/writer.log','a');fs.writeSync(fd,'first\n');
 put('writer-'+process.pid+'.json',{pid:process.pid,ppid:process.ppid,role,time:Date.now()});
 const timer=setInterval(()=>fs.writeSync(fd,'tick\n'),100);
 setTimeout(()=>{fs.writeSync(fd,'LATE\n');put('late-'+process.pid+'.txt','late');},7000);
 setTimeout(()=>{clearInterval(timer);fs.closeSync(fd);process.exit(0);},12000);
} else if(role==='middle') {
 const c=cp.spawn(process.execPath,['-e',code,mode,'writer'],{detached:true,stdio:mode==='timeout'?'inherit':'ignore',env:process.env});c.unref();process.exit(0);
} else {
 (async()=>{
 put('started.json',{pid:process.pid,mode,time:Date.now()});
 put('original.txt','modified\0bytes');fs.unlinkSync('/source/delete.txt');put('added.bin',Buffer.from([0,1,2,255]));fs.writeFileSync('/auxiliary/note.txt','auxiliary');
 const checks=[];const attempt=(name,f)=>{try{checks.push({name,success:true,value:f()});}catch(e){checks.push({name,success:false,code:e.code});}};
 attempt('self-read',()=>fs.readFileSync('/source/original.txt','utf8'));
 for(const p of ['/opt/ontosary-fixture/control/package.json','/run/containerd/containerd.sock','/opt/ontosary-fixture/previous/source/package.json','/opt/ontosary-fixture/previous/result/fixture.json'])attempt(p,()=>fs.readFileSync(p,'utf8'));
 attempt('move-cgroup',()=>fs.writeFileSync('/sys/fs/cgroup/cgroup.procs',String(process.pid)));
 attempt('delegate-cgroup',()=>fs.writeFileSync('/sys/fs/cgroup/cgroup.subtree_control','+pids'));
 await new Promise(resolve=>{const socket=net.createConnection('/run/containerd/containerd.sock');socket.on('connect',()=>{checks.push({name:'runtime-api',success:true});socket.destroy();resolve();});socket.on('error',e=>{checks.push({name:'runtime-api',success:false,code:e.code});resolve();});});
 put('access.json',{checks,cgroup:fs.readFileSync('/proc/self/cgroup','utf8'),mountinfo:fs.readFileSync('/proc/self/mountinfo','utf8'),status:fs.readFileSync('/proc/self/status','utf8')});
 if(mode==='consume') {
   attempt('snapshot-read',()=>JSON.parse(fs.readFileSync('/snapshot/fixture.json','utf8')).fixtureOnly);
   attempt('snapshot-write',()=>fs.writeFileSync('/snapshot/source/original.txt','tamper'));
   put('consume.json',checks);put('ready.json',{pid:process.pid,time:Date.now()});return;
 }
 if(mode==='symlink')fs.symlinkSync('/opt/ontosary-fixture/control/package.json','/source/bad');
 if(mode==='hardlink')fs.linkSync('/source/original.txt','/source/bad');
 if(mode==='fifo'){const r=cp.spawnSync('mkfifo',['/source/bad']);if(r.status!==0)throw Error('mkfifo unavailable');}
 if(mode==='socket'){const server=net.createServer();await new Promise(r=>server.listen('/source/bad',r));server.unref();}
 if(mode==='files')for(let i=0;i<129;i++)put('file-'+i,'x');
 if(mode==='bytes')fs.writeFileSync('/source/large',Buffer.alloc(16*1024*1024+1));
 if(mode==='depth'){const p='/source/'+Array(17).fill('nested').join('/');fs.mkdirSync(p,{recursive:true});fs.writeFileSync(p+'/bad','x');}
 if(mode==='logs'){put('ready.json',{pid:process.pid,time:Date.now()});process.stdout.write(Buffer.alloc(1024*1024+32,65));await new Promise(r=>setTimeout(r,12000));return;}
 if(['normal','timeout','wrapper','supervisor','kill-error','query-error','control','race'].includes(mode)) {
   const child=cp.spawn(process.execPath,['-e',code,mode,'middle'],{detached:true,stdio:mode==='timeout'?'inherit':'ignore',env:process.env});child.unref();
   while(!fs.readdirSync('/source').some(n=>n.startsWith('writer-')))await new Promise(r=>setTimeout(r,10));
   put('ready.json',{pid:process.pid,time:Date.now(),writerStarted:true});
   if(mode==='race')for(let i=0;i<7;i++){const c=cp.spawn(process.execPath,['-e',code,mode,'writer'],{detached:true,stdio:'ignore',env:process.env});c.unref();}
   if(mode==='normal'||mode==='race')return;
   if(mode==='control'){await new Promise(r=>setTimeout(r,8000));return;}
   await new Promise(r=>setTimeout(r,12000));return;
 }
 put('ready.json',{pid:process.pid,time:Date.now()});
 if(mode==='nonzero')process.exitCode=7;
 })().then(()=>process.exit(process.exitCode||0)).catch(e=>{console.error(e);process.exit(20);});
}
