"""Retired 2026-11-12 mutable runner; immutable execution copies remain in verification/."""
if __name__=='__main__':
 raise SystemExit('This round-specific entrypoint is retired. Use execution-lifecycle/round.py for prepare/fixtures/pair/cleanup; engine.py owns every stop/remove/collect branch. Historical snapshots remain replayable as evidence, not authorized runtime retries.')
