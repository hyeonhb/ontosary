import { checkedSnapshot } from './snapshot-gate.js';
const [snapshot]=process.argv.slice(2);
if(!snapshot)throw Error('Usage: evaluate-snapshot <snapshot>; production evaluation remains blocked by R11');
// Check authority before opening source, cache or evaluator; no failure result is promoted to a trial result.
checkedSnapshot(snapshot);
