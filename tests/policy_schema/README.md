# AGE-7 policy conformance corpus

This directory is an executable policy-language specification. `reference.py` is a test-only Python oracle; the Go service does not import it. It is not the production AGE-11 loader, evaluator, API, or snapshot persistence implementation.

## Run

Use Python 3.9 or newer in a development virtual environment:

```sh
python3 -m venv /tmp/agentwall-policy-venv
/tmp/agentwall-policy-venv/bin/python -m pip install -r tests/policy_schema/requirements.txt
make policy-test PYTHON=/tmp/agentwall-policy-venv/bin/python
```

Dependencies are development-only. No Go runtime dependency is introduced. The focused suite checks the structural schema, source-level and semantic preparation restrictions, exact size/depth/count boundaries, and declared evaluation results. CI runs the suite separately from Go tests.

## Shared format

`fixtures/semantics.json` is UTF-8 JSON with `fixtureVersion: 1` and `cases`. Each case contains:

| Field | Meaning |
|---|---|
| `id` | Unique stable test identifier |
| `files` | Candidate set: objects with `path` and verbatim YAML `source`; each path names an `agentwall-policy.yaml` |
| `request` | Decoded authorization request for successfully loaded cases |
| `serverTimeMs` | Optional injected test clock instant, signed int64 epoch milliseconds; default 0 in this harness |
| `expected.load` | `ok` or `policy_validation` |
| `expected.error` | Expected request/evaluation error category; absent on successful decisions |
| `expected.decision` | `allow` or `deny`, only if load and evaluation succeed |
| `expected.truth` | Optional direct condition assertion: `true`, `false`, or `unknown` |

A load failure has no evaluation expectation. An evaluation case has exactly one of error or decision. `truth` is used only for single-applicable-rule operator and logical cases; it is not an API result. The clock is injected separately from caller assertions. Error categories match the [Go contract](../../docs/policy-go-model-v1alpha1.md). There is no error-message-text dependency.

The 333 stored cases cover all operators over missing, null, same-type, cross-type, and container values, full binary three-valued logic, negation, scope, deny precedence and reordering, server-time boundaries, and malformed source. Expected values are stored in the corpus, not computed by the oracle. Representative values cover the type classes; no finite suite exhausts every string or int64.

`fixtures/activation.json` declares sequential `activate`, `acquire`, and `evaluate` steps. Activation has candidate files and a revision; acquisition saves a named snapshot handle; evaluation optionally uses a saved handle. Expected errors or revision/decision pairs verify unavailable startup, all-or-nothing rejection, preserving last-known-good state, and retained old snapshots. This is not evidence of production concurrency or crash recovery.

`test_contract.py` also constructs exact boundary pairs for policy document bytes, policy/rule/node counts, metadata and condition depth, descriptions and UTF-8 strings/keys, membership size, int64 precision, and request size/depth/member/string/list limits. Generated boundary inputs remain local to the test runner to avoid committing repeated hundreds-of-kilobyte padding. AGE-11 should reproduce these boundaries in Go in addition to consuming the stored corpus.

## Adoption by production implementations

AGE-11 should feed verbatim `source` values into its strict loader and compare load outcomes, then retain compiled policies for evaluator cases. The production evaluator should consume requests and fixed clocks from successfully loaded cases and compare decision/error results. Use its typed errors, not this Python implementation, as the source of observed results.

Passing this reference suite establishes internal contract consistency. Production Go tasks must pass the same corpus and add implementation-specific coverage for immutability, cancellation, race safety, activation, persistence, and recovery. Their completion cannot be inferred from this oracle passing.
