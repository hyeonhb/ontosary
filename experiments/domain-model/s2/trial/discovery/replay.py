"""Offline calibration. The scripted participant receives only the public prompt and action replies."""
import argparse
from collections import Counter
import gzip
import json
import os
from pathlib import Path
import subprocess
import sys

from session import Session, digest, encode, material_files, public

HERE = Path(__file__).resolve().parent
S2 = HERE.parent.parent
FROZEN = S2 / "results/2026-11-10-trial-preparation"
PILOT = S2 / "results/2026-11-18-fixed-input-pilot"
EXPECTED = S2 / "results/2026-11-22-refund-discovery"


def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def mock(prompt, step, control):
    def act(op, **kwargs):
        response = step({"op": op, **kwargs})
        assert "error" not in response, (op, response)
        return response

    def search(query, glob="*", space="source"):
        return act("search", space=space, query=query, glob=glob)["rows"]

    def read(space, path, start):
        return act("read", space=space, path=path, start=start)["rows"]

    # Fixed mock search choices are evaluator-only. All paths come back from the interface.
    hits = search("refund", "*admin-ui*.html")
    template, position, _ = next(hit for hit in hits if "(click)" in hit[2] and "cancel" in hit[2].lower())
    if len(prompt["spaces"]) > 1:
        space = prompt["spaces"][1]
        act("list", space=space)
        found = search("클라이언트 취소/환불 분기", "item-*.json" if space == "model" else "*.md", space)
        path, line, _ = found[0]
        read(space, path, max(1, line - 3))
        evidence = search("cancelOrRefund", "evidence-*.json" if space == "model" else "evidence.md", space)
        read(space, evidence[0][0], max(1, evidence[0][1] - 1))
    menu = read("source", template, position - 5)
    handler = next(t for _, t in menu if "(click)" in t).split('"')[1].split("(")[0]
    detail, branch, _ = search(handler + "(", "*admin-ui*.ts")[0]
    read("source", detail, branch)
    predicate = next(t for _, t in menu if "; else " in t).split('"')[1].split("(")[0]
    _, predicate_line, _ = next(row for row in search(predicate, detail) if ": boolean" in row[2])
    read("source", detail, predicate_line)
    targets = search(".fromComponent(", detail)
    # Locate both destinations, including the second method outside the first read window.
    refund_line = next(n for _, n, t in targets if "RefundOrderDialogComponent," in t)
    read("source", detail, refund_line - 2)
    amounts = search("refundableAmount", "*admin-ui*.ts")
    helper, balance_line, _ = next(row for row in amounts if "const refundableAmount" in row[2])
    helper_lines = read("source", helper, balance_line - 5)
    symbol = next(t.split("function ")[1].split("(")[0] for _, t in helper_lines if "export function " in t)
    usage = search(symbol + "(", "*admin-ui*.ts")
    dialog, dialog_line, _ = next(r for r in usage if "refund-order-dialog" in r[0])
    read("source", dialog, dialog_line - 3)
    impact = (f"{template}:{position-1}-{position+8} 메뉴는 Aggregate 제외 및 Cancelled 전이 가능일 때만 노출한다. "
              f"정산 결제 존재로 고르는 두 문구는 실제 잔액이 없으면 취소로 바꾼다. "
              f"{detail}:{branch}-{branch+7},{predicate_line}-{refund_line} 클릭은 cancel/refund 모달로 이어진다. "
              "PaymentAuthorized·active·정산 결제 없음의 직접 취소를 유지하고 그 밖에서는 잔액에 따라 분기한다. "
              f"{helper}:{balance_line-3}-{balance_line+6} 정산된 각 결제 amount에서 Failed를 제외한 refunds.total을 차감한다. "
              f"{dialog}:{dialog_line}도 이 값을 사용한다. 하나라도 양수이면 기존 문구와 경로를 보존하고 모두 소진이면 문구와 클릭을 함께 취소로 맞춘다.")
    act("submit", impact=impact)
    if control == "shared-predicate":
        act("replace", path=detail, old="return !!order.payments?.find(p => p.state === 'Settled');",
            new="""return !!order.payments?.some(p => p.state === 'Settled' &&
            p.amount > p.refunds.reduce((used, r) => used + (r.state === 'Failed' ? 0 : r.total), 0));""")
    elif control != "original":
        anchor = f"    {predicate}(order: OrderDetailFragment): boolean {{"
        act("replace", path=detail, old=anchor, new=(
            f"    hasRefundBalance(order: OrderDetailFragment): boolean {{\n"
            f"        return {symbol}(order.payments).some(p => p.refundableAmount > 0);\n    }}\n\n" + anchor))
        import_path = os.path.relpath(helper[:-3], str(Path(detail).parent))
        imports = read("source", detail, 1)
        first = imports[0][1]
        act("replace", path=detail, old=first, new=f"import {{ {symbol} }} from '{import_path}';\n" + first)
        act("replace", path=template, old=predicate + "(order); else", new="hasRefundBalance(order); else")
        if control == "reference":
            act("replace", path=detail, old=f"this.{predicate}(order)", new="this.hasRefundBalance(order)")
    act("finish")


def negative_checks(arm, source, materials):
    def session():
        return Session(arm, source, materials)
    s = session()
    checks = {}
    checks["shared-source-list"] = s.step({"op":"list","space":"source","glob":"README.md"})["rows"] == ["README.md"]
    for space in materials:
        checks["deny-extra-material"] = "error" in s.step({"op":"read","space":space,"path":"../TASK.md"})
    for space in sorted({"model", "document", "evaluator"} - set(s.public["spaces"])):
        checks["deny-" + space] = "error" in s.step({"op":"list", "space":space})
    for path in ("../evaluator", "/etc/passwd", ".git/config"):
        checks["deny-read-" + path] = "error" in s.step({"op":"read","space":"source","path":path})
    checks["deny-early-edit"] = "error" in s.step({"op":"replace","path":"README.md","old":"x","new":"y"})
    s.step({"op":"submit","impact":"first"})
    checks["deny-second-impact"] = "error" in s.step({"op":"submit","impact":"second"}) and s.impact == "first"
    checks["deny-escape-edit"] = "error" in s.step({"op":"create","path":"../out","text":"x"})
    checks["deny-case-alias"] = "error" in s.step({"op":"create","path":"Readme.md","text":"x"})
    checks["deny-malformed"] = "error" in s.step({"op":"search","space":"source","query":False})
    s.step({"op":"finish"})
    try:
        s.step({"op":"create","path":"x","text":"x"})
    except ValueError:
        checks["deny-after-finish"] = True
    assert checks.get("deny-after-finish") and all(checks.values())
    return checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("environment", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    files = {}
    for p in sorted(args.source.rglob("*")):
        assert not p.is_symlink(), p
        if p.is_file():
            files[p.relative_to(args.source).as_posix()] = p.read_bytes()
    with gzip.open(PILOT / "baseline.json.gz") as archive:
        pinned = json.load(archive)["typecheck"]["submittedManifest"]
    assert {p:digest(b) for p,b in files.items()} == pinned
    audit = subprocess.check_output([sys.executable,str(S2/"verification/2026-11-10-trial-preparation/audit-parity.py"), str(FROZEN)])
    result = {"sourceFiles":len(files), "materialParityLeaves":json.loads(audit)["totalUnits"],
              "materials":{}, "boundary":{}, "mocks":{}, "participantCalls":0}
    traces = {}
    timings = {}
    for arm, control in [("A","original"),("A","label-only"),("A","shared-predicate"),("A","reference"),("B","reference"),("C","reference")]:
        key = arm + "-" + control
        materials = material_files(arm,FROZEN)
        result["materials"][arm] = {space:{p:digest(b) for p,b in paths.items()} for space,paths in materials.items()}
        result["boundary"][arm] = negative_checks(arm,files,materials)
        s = Session(arm,files,materials)
        mock(public(arm), s.step, control)
        assert s.finished and s.impact and s.spaces["source"] is not files
        dest = out/key
        for p,b in s.spaces["source"].items():
            target = dest/p
            target.parent.mkdir(exist_ok=True,parents=True)
            with target.open("xb") as f:
                f.write(b)
        assert {p.relative_to(dest).as_posix():digest(p.read_bytes()) for p in dest.rglob("*") if p.is_file()} == {p:digest(b) for p,b in s.spaces["source"].items()}
        changes = {p:digest(b) for p,b in s.spaces["source"].items() if files.get(p)!=b}
        grade = out/(key+".json")
        subprocess.run([sys.executable,str(HERE.parent/"fixed-input/evaluate.py"),str(dest),
                        str(args.environment.resolve()),str(grade),"refund-discovery"],check=True)
        report = json.loads(grade.read_text())
        valid = control in ("reference","shared-predicate")
        passed = sum(row["passed"] for row in report["observations"])
        assert report["typecheck"] == "passed" and report["bound"] and passed == (11 if valid else 9), (key,report)
        assert report["status"] == ("passed" if valid else "failed")
        timings[key] = s.elapsed_ns
        if control == "reference":
            traces[arm] = {"public":s.public, "steps":s.trace}
        returned = Counter()
        counts = Counter()
        rows = Counter()
        for entry in s.trace:
            op = entry["action"]["op"]
            kind = entry["action"].get("space", "submission") + "." + op
            counts[kind] += 1
            returned[kind] += entry["bytes"]
            rows[kind] += len(entry["reply"].get("rows",[]))
        result["mocks"][key] = {"counts":counts,"returnedBytes":returned,"returnedRows":rows,
            "changes":changes, "impactSha256":digest(s.impact.encode()), "grade":report}
    refs = [result["mocks"][a+"-reference"] for a in "ABC"]
    assert all(r["grade"]["submissionId"]==refs[0]["grade"]["submissionId"] and r["impactSha256"]==refs[0]["impactSha256"] for r in refs)
    write(out/"tool-nanoseconds.json",timings)
    for name,data in [("results.json",result),("traces.json",traces)]:
        write(out/name,data)
        if args.verify:
            assert (out/name).read_bytes() == (EXPECTED/name).read_bytes(), name
    print("6 independent snapshots, 3 discovery transcripts, 0 participant calls:", out)


if __name__ == "__main__":
    main()
