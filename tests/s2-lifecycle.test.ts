import { it, expect } from 'vitest';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { checkedSnapshot } from '../experiments/domain-model/s2/trial/snapshot-gate.js';
import { snapshot } from '../experiments/domain-model/s2/trial/runtime.js';
import { refuseTrial } from '../experiments/domain-model/s2/trial/telemetry.js';

it('a stopped container fixture cannot authorize production collection, evaluation or live dispatch', () => {
    const root = fs.mkdtempSync(path.join(os.tmpdir(), 's2-container-fixture-'));
    try {
        const receipt = {
            schema: 's2-lifecycle-fixture-v1', fixtureOnly: true, validSubmission: false,
            classification: 'normal-fixture',
            termination: { state: 'stopped-confirmed', confirmed: true, admissionClosed: true },
        };
        fs.writeFileSync(path.join(root, 'fixture.json'), JSON.stringify(receipt));
        expect(() => snapshot(receipt)).toThrow('production collection blocked');
        expect(() => checkedSnapshot(root)).toThrow('production evaluation blocked');
        expect(() => refuseTrial()).toThrow('not authorized');
    } finally {
        fs.rmSync(root, { recursive: true, force: true });
    }
});
