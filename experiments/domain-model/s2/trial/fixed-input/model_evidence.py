"""Extract only server-originated model names from local Codex diagnostics."""
import json
import re

session_report = re.compile(
    r"""codex_core::session: server reported model [`'"]?([a-zA-Z0-9._-]+)[`'"]? (?:\(matches requested model\)|while requested model was)"""
)
event_marker = 'codex_api::sse::responses: SSE event: '


def server_models(lines):
    names = set()
    for line in lines:
        if event_marker not in line:
            match = session_report.search(line)
            if match:
                names.add(match.group(1))
            continue
        try:
            event = json.loads(line.split(event_marker, 1)[1])
        except ValueError:
            continue
        if isinstance(event, dict) and event.get('type') in ('response.created', 'response.completed'):
            response = event.get('response')
            name = response.get('model') if isinstance(response, dict) else None
            if isinstance(name, str) and re.fullmatch(r'[a-zA-Z0-9._-]+', name):
                names.add(name)
    return sorted(names)
