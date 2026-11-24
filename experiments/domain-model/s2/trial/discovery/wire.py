"""Capture initial and follow-up participant inputs at a local rejection endpoint. No live provider."""
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading

from session import digest, encode, public

system = "Use only the public prompt and action history. Return one JSON action."
s2 = Path(__file__).resolve().parents[2]
prior = json.loads((s2/"results/2026-11-20-sol-comparison/preflight/quantity.json").read_bytes())
traces = json.loads(Path(sys.argv[1]).read_bytes())
output = Path(sys.argv[2])
model = prior["model"]
observed = []


class Capture(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        observed.append(data)
        self.send_response(400)
        self.end_headers()
        self.wfile.write(b'{"error":{"message":"Local capture complete"}}')


with tempfile.TemporaryDirectory() as scratch, HTTPServer(("127.0.0.1", 0), Capture) as server:
    folder = Path(scratch)
    run = folder/"empty"
    run.mkdir()
    catalog = folder/"catalog.json"
    local_cache = json.loads((Path.home()/".codex/models_cache.json").read_bytes())
    entry = next(m for m in local_cache["models"] if m["slug"]==model)
    catalog.write_text(json.dumps({"models":[{**entry, **prior["catalogOverrides"]}]}))
    instructions = folder/"system.txt"
    instructions.write_text(system)
    settings = [*prior["settings"], 'model_catalog_json='+json.dumps(str(catalog)),
                'model_instructions_file='+json.dumps(str(instructions)), 'model_provider="localcapture"',
                'model_providers.localcapture.name="Offline capture"', 'model_providers.localcapture.wire_api="responses"',
                f'model_providers.localcapture.base_url="http://127.0.0.1:{server.server_port}/v1"']
    (folder/"state").mkdir()
    env = {"PATH":os.environ["PATH"],"HOME":scratch,"CODEX_HOME":str(folder/"state"),"LANG":"C"}
    cli = ["codex","exec","--ignore-user-config","--ignore-rules","--ephemeral","--json","--skip-git-repo-check",
           "-C",str(run),"-s","read-only","-m",model,*[x for v in settings for x in ("-c",v)],"-"]
    threading.Thread(target=server.serve_forever, daemon=True).start()
    captured = {}
    for arm,t in traces.items():
        captured[arm] = []
        assert t["public"] == public(arm)
        assert t["steps"][0]["action"] == t["public"]["example"] and t["steps"][0]["reply"]["rows"]
        for n in (0, 1, 3):
            # Only public action/reply pairs are returned, never timings, grader, gold or other arms.
            history = [{"action":r["action"],"reply":r["reply"]} for r in t["steps"][:n]]
            packet = encode({"public":t["public"],"history":history}).decode()
            observed.clear()
            proc = subprocess.run(cli, input=packet,text=True,env=env,cwd=run,capture_output=True,timeout=45)
            assert len(observed)==1, (arm,n,len(observed),proc.stderr[-1200:])
            data = observed[0]
            assert data["model"]==model and data["reasoning"]["effort"]=="medium"
            assert data.get("instructions") in (None,"",system), "Unexpected top-level instructions"
            items = data["input"]
            assert not any(i.get("tools") for i in [data,*items])
            assert [(i["role"],i["type"],[c["text"] for c in i["content"]]) for i in items] == [
                ("developer","message",[system]),("user","message",[packet])]
            received = json.loads(items[1]["content"][0]["text"])
            frame = {"historySteps":n,"packetSha256":digest(packet.encode()),"tools":[],
                     "example":received["public"]["example"]}
            if n == 1:
                first, = received["history"]
                assert first["action"] == frame["example"] and first["reply"] == t["steps"][0]["reply"]
                frame["firstReplyRows"] = len(first["reply"]["rows"])
                frame["firstReplySha256"] = digest(encode(first["reply"]))
            captured[arm].append(frame)
    server.shutdown()
    with output.open("x") as f:
        json.dump({"cli":subprocess.check_output(["codex","--version"],text=True).strip(),"model":model,"effort":"medium",
                   "provider":"loopback HTTP 400", "roles":["developer","user"],"captured":captured},f,indent=2)
        f.write("\n")
