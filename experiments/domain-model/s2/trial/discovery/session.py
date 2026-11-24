"""Host-side, task-specific action protocol. Only public() and step() replies go to the participant."""
import fnmatch
import hashlib
import json
from unicodedata import normalize
from time import monotonic_ns
from pathlib import Path

REV = "534e6003534f74761e82de1b8c6061cba89945d1"
TASK = "관리자 주문 상세에서 고객에게 돌려줄 금액이 전혀 남지 않은 주문은 환불로 안내하지 말고 취소 절차로 연결해 주세요. 환불할 금액이 남은 주문에서는 기존 취소·환불 동작을 유지하고, 원래 취소할 수 없던 주문에 새로 취소를 허용하지 마세요."
DOCUMENTS = ("guide.md", "observations.md", "roles.md", "evidence.md")
LIMIT = 4096


def encode(data):
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def public(arm):
    spaces = {"A": ["source"], "B": ["source", "model"], "C": ["source", "document"]}[arm]
    help_text = {"A": [], "B": ["In model, list available views or read index.json. Search concept ids in item views, follow related items/factRefs, then search the fact and evidence views for source coordinates."],
                 "C": ["In document, list documents, search narrative statements and follow their identifiers to the evidence appendix."]}[arm]
    return {"task": TASK, "revision": REV, "scope": "Vendure existing Admin UI; repository source and documentation",
            "spaces": spaces, "example": {"op": "search", "space": "source", "query": "license"}, "protocol": [
                "Send one JSON object per turn (24 actions in this mock). The required key op names the action. Put its arguments in the same object. You can send example verbatim. list(space,glob?,offset?) lists relative file names.",
                "search(space,query,glob?,offset?) returns literal case-insensitive matches with line numbers.",
                "read(space,path,start?,offset?,column?) returns numbered lines from start (1-based). Long lines show 420 characters; column (1-based) selects another slice. All offsets skip rows, starting at zero. next is the next offset for the same query.",
                "submit(impact) once before editing: describe affected locations, behavior to preserve and supporting source lines/symbols.",
                "replace(path,old,new) replaces one unique exact text in source; create(path,text) adds a file. finish() submits the working copy. No test feedback.", *help_text]}


def material_files(arm, frozen):
    if arm == "B":
        return {"model": {p.name: p.read_bytes() for p in sorted((frozen / "B/views").glob("*.json"))}}
    if arm == "C":
        return {"document": {name: (frozen / "C" / name).read_bytes() for name in DOCUMENTS}}
    return {}


class Session:
    def __init__(self, arm, baseline, materials):
        self.public = public(arm)
        self.spaces = {"source": dict(baseline), **materials}
        assert list(self.spaces) == self.public["spaces"]
        self.trace = []
        self.elapsed_ns = []
        self.impact = None
        self.finished = False

    def step(self, action):
        if self.finished or len(self.trace) >= 24:
            raise ValueError("session closed")
        start_ns = monotonic_ns()
        try:
            reply = self.apply(action)
        except (ValueError, KeyError, TypeError, UnicodeError):
            reply = {"error": "invalid action or unavailable resource"}
        raw = encode(reply)
        assert len(raw) <= LIMIT
        self.trace.append({"action": json.loads(encode(action)), "reply": reply, "bytes": len(raw)})
        self.elapsed_ns.append(monotonic_ns() - start_ns)
        return reply

    def apply(self, a):
        if not isinstance(a, dict) or any(not isinstance(v, str) for k, v in a.items() if k not in ("offset", "column", "start")):
            raise ValueError()
        op = a["op"]
        if op in ("list", "search", "read"):
            files = self.spaces[a["space"]]
            offset = a.get("offset", 0)
            if type(offset) is not int or offset < 0:
                raise ValueError()
            if op == "read":
                start = a.get("start", 1)
                if type(start) is not int or start < 1:
                    raise ValueError()
                col = a.get("column", 1)
                if type(col) is not int or col < 1:
                    raise ValueError()
                lines = files[a["path"]].decode().splitlines()
                rows = ([i, line[col-1:col+419]] for i, line in enumerate(lines, 1) if i >= start)
            else:
                paths = sorted(p for p in files if fnmatch.fnmatchcase(p, a.get("glob", "*")))
                if op == "list":
                    rows = iter(paths)
                else:
                    query = a["query"].casefold()
                    if not query:
                        raise ValueError()
                    rows = ([p, n, line[:420]] for p in paths if b"\0" not in files[p]
                            for n, line in enumerate(files[p].decode(errors="replace").splitlines(), 1)
                            if query in line.casefold())
            result = []
            for i, row in enumerate(rows):
                if i < offset:
                    continue
                if len(result) == 32 or len(encode({"rows": [*result, row], "next": i+1})) > LIMIT:
                    return {"rows": result, "next": i}
                result.append(row)
            return {"rows": result, "next": None}

        if op == "submit" and self.impact is None and isinstance(a["impact"], str) and a["impact"].strip():
            self.impact = a["impact"]
            return {"sealed": digest(self.impact.encode())}
        if self.impact is None:
            raise ValueError()
        files = self.spaces["source"]
        if op == "replace":
            path, old, new = a["path"], a["old"].encode(), a["new"].encode()
            if not old or files[path].count(old) != 1:
                raise ValueError()
            files[path] = files[path].replace(old, new)
        elif op == "create":
            path = a["path"]
            if ("\x00" in path or any(p.casefold() in ("", ".", "..", ".git", "node_modules") for p in path.split("/"))
                    or path in files or any(str(parent) in files for parent in Path(path).parents)
                    or any(p.startswith(path + "/") for p in files)):
                raise ValueError()
            # The content map is case-sensitive; the macOS collection volume may not be.
            names = {normalize("NFD", part.as_posix()).casefold():part.as_posix()
                     for name in files for part in (Path(name), *Path(name).parents)}
            for part in (Path(path), *Path(path).parents):
                spelling = part.as_posix()
                if names.get(normalize("NFD", spelling).casefold(), spelling) != spelling:
                    raise ValueError()
            files[path] = a["text"].encode()
        elif op == "finish":
            self.finished = True
        else:
            raise ValueError()
        return {"ok": True}
