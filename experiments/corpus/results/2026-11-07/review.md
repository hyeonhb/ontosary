# Corpus review worksheet — 2026-11-07

Agent-authored code facts; all human decisions are pending. A correct extraction is not a supported predicate or approved business concept.

| Label | Source | Claim | Automated observation | Human decision |
| --- | --- | --- | --- | --- |
| p-queue-01 | [source/lower-bound.ts:3](https://github.com/sindresorhus/p-queue/blob/7f272ab5ff2254c0dc2537b7977e88ede1cd55e8/source/lower-bound.ts#L3) | lowerBound is a separate function declaration. | correct | pending |
| p-queue-02 | [source/lower-bound.ts:3](https://github.com/sindresorhus/p-queue/blob/7f272ab5ff2254c0dc2537b7977e88ede1cd55e8/source/lower-bound.ts#L3) | lowerBound has an array parameter named array. | correct | pending |
| p-queue-03 | [source/lower-bound.ts:3](https://github.com/sindresorhus/p-queue/blob/7f272ab5ff2254c0dc2537b7977e88ede1cd55e8/source/lower-bound.ts#L3) | lowerBound tests count > 0 in its while loop. | correct | pending |
| p-queue-04 | [source/lower-bound.ts:3](https://github.com/sindresorhus/p-queue/blob/7f272ab5ff2254c0dc2537b7977e88ede1cd55e8/source/lower-bound.ts#L3) | The invocation comparator resolves to this function parameter, not a same-name global. | correct | pending |
| p-queue-05 | [source/queue.ts:3](https://github.com/sindresorhus/p-queue/blob/7f272ab5ff2254c0dc2537b7977e88ede1cd55e8/source/queue.ts#L3) | Queue is a generic type alias. | correct | pending |
| p-queue-06 | [source/queue.ts:3](https://github.com/sindresorhus/p-queue/blob/7f272ab5ff2254c0dc2537b7977e88ede1cd55e8/source/queue.ts#L3) | Queue exposes size as a number field. | correct | pending |
| p-queue-07 | [source/priority-queue.ts:58](https://github.com/sindresorhus/p-queue/blob/7f272ab5ff2254c0dc2537b7977e88ede1cd55e8/source/priority-queue.ts#L58) | enqueue is a method on PriorityQueue. | correct | pending |
| p-queue-08 | [source/priority-queue.ts:58](https://github.com/sindresorhus/p-queue/blob/7f272ab5ff2254c0dc2537b7977e88ede1cd55e8/source/priority-queue.ts#L58) | enqueue references the imported lowerBound declaration. | correct | pending |
| p-queue-09 | [source/priority-queue.ts:120](https://github.com/sindresorhus/p-queue/blob/7f272ab5ff2254c0dc2537b7977e88ede1cd55e8/source/priority-queue.ts#L120) | dequeue tests whether head equals queue length. | correct | pending |
| p-queue-10 | [source/priority-queue.ts:137](https://github.com/sindresorhus/p-queue/blob/7f272ab5ff2254c0dc2537b7977e88ede1cd55e8/source/priority-queue.ts#L137) | size returns array length minus consumed head. | correct | pending |
| p-queue-11 | [source/priority-queue.ts:11](https://github.com/sindresorhus/p-queue/blob/7f272ab5ff2254c0dc2537b7977e88ede1cd55e8/source/priority-queue.ts#L11) | PriorityQueue is a distinct class declaration (class modeling coverage probe). | unsupported | pending |
| p-queue-12 | [source/priority-queue.ts:11](https://github.com/sindresorhus/p-queue/blob/7f272ab5ff2254c0dc2537b7977e88ede1cd55e8/source/priority-queue.ts#L11) | PriorityQueue declares numeric private state #head (field modeling coverage probe). | unsupported | pending |
| date-fns-01 | [src/isWeekend/index.ts:27](https://github.com/date-fns/date-fns/blob/313b902b9a72c64501074db9bc2b9897d2db5140/src/isWeekend/index.ts#L27) | isWeekend has its own function declaration. | correct | pending |
| date-fns-02 | [src/isSaturday/index.ts:27](https://github.com/date-fns/date-fns/blob/313b902b9a72c64501074db9bc2b9897d2db5140/src/isSaturday/index.ts#L27) | isSaturday has its own function declaration. | correct | pending |
| date-fns-03 | [src/isSaturday/index.ts:7](https://github.com/date-fns/date-fns/blob/313b902b9a72c64501074db9bc2b9897d2db5140/src/isSaturday/index.ts#L7) | IsSaturdayOptions and IsSundayOptions are distinct declarations despite both extending ContextOptions<Date>. | correct | pending |
| date-fns-04 | [src/isWeekend/index.ts:27](https://github.com/date-fns/date-fns/blob/313b902b9a72c64501074db9bc2b9897d2db5140/src/isWeekend/index.ts#L27) | isWeekend returns day === 0 \|\| day === 6. | correct | pending |
| date-fns-05 | [src/isSaturday/index.ts:27](https://github.com/date-fns/date-fns/blob/313b902b9a72c64501074db9bc2b9897d2db5140/src/isSaturday/index.ts#L27) | isSaturday compares converted getDay() to 6. | correct | pending |
| date-fns-06 | [src/isSunday/index.ts:27](https://github.com/date-fns/date-fns/blob/313b902b9a72c64501074db9bc2b9897d2db5140/src/isSunday/index.ts#L27) | isSunday compares converted getDay() to 0. | correct | pending |
| date-fns-07 | [src/isWeekend/index.ts:27](https://github.com/date-fns/date-fns/blob/313b902b9a72c64501074db9bc2b9897d2db5140/src/isWeekend/index.ts#L27) | isWeekend refers to the local imported toDate declaration. | correct | pending |
| date-fns-08 | [src/isSaturday/index.ts:27](https://github.com/date-fns/date-fns/blob/313b902b9a72c64501074db9bc2b9897d2db5140/src/isSaturday/index.ts#L27) | isSaturday refers to the same toDate declaration as isWeekend. | correct | pending |
| date-fns-09 | [src/isWeekend/index.ts:27](https://github.com/date-fns/date-fns/blob/313b902b9a72c64501074db9bc2b9897d2db5140/src/isWeekend/index.ts#L27) | options.in resolves to the inherited ContextOptions.in declaration. | correct | pending |
| date-fns-10 | [src/types.ts:10](https://github.com/date-fns/date-fns/blob/313b902b9a72c64501074db9bc2b9897d2db5140/src/types.ts#L10) | DateArg retains the date, number, string union alias. | correct | pending |
| date-fns-11 | [src/constructFrom/index.ts:44](https://github.com/date-fns/date-fns/blob/313b902b9a72c64501074db9bc2b9897d2db5140/src/constructFrom/index.ts#L44) | constructFrom branches on typeof date === function. | correct | pending |
| date-fns-12 | [src/toDate/index.ts:42](https://github.com/date-fns/date-fns/blob/313b902b9a72c64501074db9bc2b9897d2db5140/src/toDate/index.ts#L42) | toDate has its own generic function declaration. | correct | pending |

Review the unchanged source first, then linked evidence in labels.json. Correct an agent label separately from an extraction defect; keep original observations.

## User tasks (not yet performed)

1. Locate weekday/queue rules with source search or LSP, recording actual elapsed time and wrong turns.
2. Review the single type/property groups and FCA candidates on the same facts. Record useful/noise/uncertain and evidence checked. Counts are not quality scores.
3. Explain the two preselected weekday differences from source. Both comparisons are Unsupported; do not infer a proof or policy violation.

Decode *-concepts.json.gz and *-simple-groups.json.gz using the README command. All candidates remain unreviewed; do not interpret RunFunction, Date or Array sharing as business identity.

Human reviewer: pending. Human elapsed time: not measured. Approved knowledge: none.
