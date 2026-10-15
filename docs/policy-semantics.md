# Policy semantic decisions for v0.1

Status: AGE-7 specification and executable reference contract complete; production Go adoption pending

Date: 2026-10-15  
Issue: AGE-7 — Specify policy schema and matching semantics

## Purpose and scope

This document records the agreed AgentWall v0.1 policy semantics: how conditions evaluate, how rules combine, and how policy sets load safely. It is a design contract, not a claim of implemented behavior or a complete YAML schema. AGE-11, the YAML validation and normalized policy loader, depends on completing the remaining AGE-7 contracts.

These decisions apply to `agentwall.dev/v1alpha1` policies and align with the policy-and-audit boundary in [requirements](requirements.md), [ADR 002](ADRs/002-policy-engine.md), and [ADR 003](ADRs/003-policy-audit-first.md). The [versioned schema contract](policy-schema-v1alpha1.md) and [structural JSON Schema](schemas/agentpolicy-v1alpha1.schema.json) assemble the agreed document format. YAML snippets illustrate that format; detailed Go type declarations and full acceptance fixtures remain deliverables. Unresolved details are listed at the end and must not be treated as approved guarantees.

## 1. Three condition results: true, false, and unknown

A condition can return:

| Result | Meaning |
|---|---|
| `true` | Available information establishes that the condition matches. |
| `false` | Available information establishes that it does not match. |
| `unknown` | Required information is missing, so the match cannot be determined. |

For example, evaluating `user.department eq "engineering"`:

| Input | Result |
|---|---|
| `department: engineering` | `true` |
| `department: sales` | `false` |
| Department attribute absent | `unknown` |

Missing attributes return `unknown` for negative comparisons as well. In particular, missing `department` cannot satisfy `department neq "contractors"`.

`unknown` is an internal condition result. It is distinct from both a final access decision and an evaluation error. In Go, condition evaluation returns a three-valued truth enum (`true`, `false`, `unknown`) plus a separate error. A non-nil error invalidates the accompanying truth result. Final access decisions use a separate allow/deny type and are returned only after successful evaluation; neither unknown nor an error is a final access decision. A non-nil error at the decision boundary likewise invalidates any accompanying decision value.

## 2. Logical composition

`all`, `any`, and `not` use three-valued logic:

| A | B | `all(A, B)` | `any(A, B)` |
|---|---|---|---|
| `true` | `true` | `true` | `true` |
| `true` | `false` | `false` | `true` |
| `true` | `unknown` | `unknown` | `true` |
| `false` | `false` | `false` | `false` |
| `false` | `unknown` | `false` | `unknown` |
| `unknown` | `unknown` | `unknown` | `unknown` |

Negation behaves as follows:

| Input | `not` result |
|---|---|
| `true` | `false` |
| `false` | `true` |
| `unknown` | `unknown` |

For groups with multiple children:

- `all` is false if any child is false; otherwise unknown if any child is unknown; otherwise true.
- `any` is true if any child is true; otherwise unknown if any child is unknown; otherwise false.

This prevents negation from turning missing information into permission.

## 3. Explicit null is different from missing

Explicit null is a known value for equality:

| Expression | Result |
|---|---|
| `null eq null` | `true` |
| `null neq null` | `false` |
| `null eq "engineering"` | `false` |
| `null neq "contractors"` | `true` |
| Missing attribute `eq null` | `unknown` |
| `startsWith` applied to null | Type error |
| Numeric range applied to null | Type error |

The practical consequence is that `department neq "contractors"` accepts an explicit null department.

To require a populated department that is not contractors, the policy checks both:

```text
all(
  department neq null,
  department neq "contractors"
)
```

Null equality is an intentional exception to ordinary cross-type rejection.

## 4. Strict typing

AgentWall performs **no implicit type coercion**.

| Comparison | Behavior |
|---|---|
| Integer `5` equals integer `5` | `true` |
| String `"5"` equals integer `5` | Type mismatch |
| String `"true"` equals boolean `true` | Type mismatch |
| `startsWith` applied to an integer | Type mismatch |

The operator-specific literal types are:

| Operator | Required `value` type |
|---|---|
| `eq`, `neq` | String, signed int64, boolean, or null |
| `in`, `notIn` | Nonempty list of one non-null scalar type (string, int64, or boolean), optionally including null; duplicates and null-only lists are rejected |
| `startsWith` | Nonempty string |
| `gt`, `gte`, `lt`, `lte` | Signed int64 |
| `range` | Mapping of the supported bounds to signed int64 values, subject to section 8 |

Object and list equality are outside v0.1; `eq` and `neq` do not compare containers. Request containers used as comparison inputs produce a type error, including when the literal is null. The null equality exception applies to scalar comparisons.

Invalid types identifiable from the policy fail at load time. Type mismatches discovered in request context produce evaluation errors—not false or unknown.

## 5. Membership operators

`in` uses equality semantics. `notIn` is its logical negation.

| Expression | Result |
|---|---|
| `"engineering" in ["engineering", "sales"]` | `true` |
| `null in ["engineering", "sales"]` | `false` |
| `null in [null, "engineering"]` | `true` |
| Missing attribute `in ["engineering", "sales"]` | `unknown` |
| Missing attribute `notIn ["contractors"]` | `unknown` |

Membership lists contain one non-null type, optionally including null:

- `["engineering", "sales"]`: valid.
- `["engineering", null]`: valid.
- `["engineering", 5]`: rejected at load time as a type error.
- Duplicate values are rejected at load time as a type error.

A non-null request value whose type differs from the list's non-null type produces an evaluation type error. Null-only membership lists, such as `[null]`, are rejected at load time as a type error. Lists containing one non-null type and an optional null remain valid, such as `["engineering", null]`.

## 6. Empty groups and lists

The loader rejects:

- `all: []`
- `any: []`
- Empty `in` or `notIn` lists.

`not` requires exactly one child condition, represented directly as a condition mapping, not a list. A logical or constant node is a mapping with exactly one key: `all`, `any`, `not`, or `always`. `all` and `any` each contain a nonempty list of child condition mappings; `always` contains only literal `true`. Extra keys and mixed condition forms are rejected.

These restrictions prevent an accidentally empty group or list from becoming an always-true condition.

## 7. String matching

String comparisons are:

- Case-sensitive.
- Exact.
- Free of automatic whitespace trimming or normalization.

Examples:

| Expression | Result |
|---|---|
| `"Engineering" eq "engineering"` | `false` |
| `"engineering " eq "engineering"` | `false` |
| `"Engineering" startsWith "eng"` | `false` |

Any normalization occurs before evaluation under an explicit attribute contract. Empty `startsWith` prefixes are rejected at load time.

## 8. Numeric representation and ranges

v0.1 supports **signed 64-bit integers only**.

- No floating-point values.
- No implicit conversion of numeric strings.
- Parsing preserves precision without passing through `float64`.
- Values outside the int64 range are rejected.
- Units and scales are explicit in the attribute contract.

Examples include `duration_ms: 1500`, `cost_microusd: 250000`, or a risk score represented as `750` on a scale of 0–1000.

Standalone `gt`, `gte`, `lt`, and `lte` operators coexist with `range`. They accept int64 literals and int64 input without coercion; missing input returns unknown and null or non-integer input produces a type error.

Ranges use explicit bounds:

```yaml
field: request.token_count
operator: range
value:
  gte: 1
  lt: 4096
```

This matches integers from 1 through 4095.

| Bound | Meaning |
|---|---|
| `gt` | Greater than |
| `gte` | Greater than or equal |
| `lt` | Less than |
| `lte` | Less than or equal |

Rules:

- At least one bound is required.
- One-sided ranges are valid.
- A lower bound uses either `gt` or `gte`.
- An upper bound uses either `lt` or `lte`.
- Conflicting bounds and ranges containing no valid integer are rejected at load time.
- Missing input returns unknown.
- Null or non-integer input produces a type error.

## 9. Attribute paths

Attribute references use case-sensitive, dot-separated paths through nested objects:

```yaml
field: user.department
```

This resolves through:

```json
{
  "user": {
    "department": "engineering"
  }
}
```

Each path segment follows:

```text
[A-Za-z_][A-Za-z0-9_]*
```

v0.1 does not support array indexing, path wildcards, or escaped dots in field names.

| Situation | Behavior |
|---|---|
| A path segment is missing | `unknown` |
| An intermediate value is null or a scalar | Type error |
| The final value is null | Explicit-null semantics |

For example, `{"user": null}` cannot be traversed as `user.department`.

Conditions compare an attribute against literal values; attribute-to-attribute comparisons are outside v0.1.

## 10. Resource patterns

Resource identifiers use `/`-separated segments.

| Pattern | Meaning |
|---|---|
| `tools/github/read` | Exact resource match |
| `tools/github/*` | Exactly one additional nonempty segment |
| `tools/github/**` | One or more additional segments |

Examples:

| Pattern | Resource | Matches? |
|---|---|---|
| `tools/github/*` | `tools/github/read` | Yes |
| `tools/github/*` | `tools/github/repos/delete` | No |
| `tools/github/**` | `tools/github/repos/delete` | Yes |
| `tools/github/**` | `tools/github` | No |

Additional restrictions:

- Wildcards occupy whole segments.
- `**` appears only at the end.
- Partial-segment patterns such as `read*` are rejected.
- Matching covers the entire identifier and remains case-sensitive.
- Regex is unsupported.
- Empty resource identifiers, empty segments, and `.` or `..` segments are rejected. Resource identifiers and patterns have no leading or trailing slash. The leading-slash and root exceptions for `path` and `apiPath` are defined in section 11.
- AgentWall does not normalize paths or decode percent escapes.

## 11. Rule scope and applicability

Scope determines whether a rule participates in evaluation. Supported scope targets include file paths (including filenames and directories), resource names, and API paths. Scope is mandatory for every rule. All supported scope targets use the whole-segment `*` and trailing `**` wildcard rules in section 10. Multiple scope fields combine using the three-valued `all` (AND) semantics in section 2; a false combined scope excludes the rule, while an unknown combined scope produces an evaluation error. The supported YAML scope fields are:

| Field | Target |
|---|---|
| `path` | File or directory path |
| `resource` | Resource name |
| `apiPath` | API path |

Every scope must contain at least one of these fields. An empty or missing scope is rejected at load time. Multiple fields must all match for the rule to apply. Scope patterns and corresponding request values follow these slash rules:

| Scope field | Slash rules |
|---|---|
| `resource` | No leading or trailing slash. |
| `apiPath` | Leading slash required; `/` is a valid root path. |
| `path` | Relative and absolute paths are supported; `/` is a valid absolute root path. |

Trailing slashes are rejected except for `/`. Repeated slashes and `.` or `..` segments are rejected. The single leading slash on an absolute path is a root marker, not an empty segment. Relative and absolute file paths are distinct and are matched as written. Matching performs no normalization or percent decoding. Whole-segment `*` and trailing `**` retain their section 10 meanings; in particular, `**` requires one or more additional segments.

Each scope field matches the same-named top-level request attribute: `scope.path` matches `path`, `scope.resource` matches `resource`, and `scope.apiPath` matches `apiPath`. Only fields present in the rule's scope participate in its scope match. A missing corresponding request attribute produces unknown for that component; the combined scope follows the three-valued AND semantics above. All supplied top-level `path`, `resource`, and `apiPath` request attributes are validated as strings with the corresponding path syntax during request validation, even if no loaded rule references them or a rule would otherwise not match. Concrete request targets must not contain `*` anywhere; wildcard syntax is reserved for policy scope patterns. This excludes literal filenames containing asterisks in v0.1. Invalid supplied target values are rejected before evaluation. Missing targets are permitted by this validation step and produce unknown only when referenced by a scope; caller assertion contracts may impose additional required fields.

| Scope result | Behavior |
|---|---|
| `true` | Evaluate the rule’s condition |
| `false` | Exclude the rule |
| `unknown` | Return an evaluation error |

An indeterminate scope must not silently exclude a potentially relevant deny rule. Required scope attributes should ordinarily be caught by request validation first.

Unrelated rules whose scopes definitively do not match do not block access.

## 12. Combining rules: deny overrides and default deny

Once validation succeeds and scopes are determined:

| Evaluation outcome | Final decision |
|---|---|
| Any applicable deny condition is true | Deny |
| Any applicable deny condition is unknown | Deny |
| At least one applicable allow condition is true, and all applicable deny conditions are false | Allow |
| No applicable allow condition is true | Deny |

An unknown allow condition cannot grant access. An unknown condition on an applicable deny rule blocks access because permission cannot be established.

**Neither rule order nor pattern specificity changes precedence.**

For example:

| Rules | Request | Decision |
|---|---|---|
| Deny `tools/github/**`; allow `tools/github/read` | `tools/github/read` | Deny |
| Allow `tools/github/**`; deny `tools/github/delete` | `tools/github/delete` | Deny |

An exception to a broad deny must be expressed by changing its scope or conditions.

Evaluation and infrastructure failures remain error responses rather than ordinary policy denials. Calling gateways must fail closed on errors, timeouts, or unavailability.

## 13. Type validation and short-circuiting

Type validation happens **across all applicable rules before condition evaluation or a final decision**. A type error must be returned even if another applicable rule establishes a deny. Neither rule order nor an already established outcome may hide validation errors.

For example:

```text
any(
  user.role eq "admin",
  request.token_count < 1000
)
```

If the role is `"admin"` but `token_count` is `"many"`, evaluation produces a type error. The successful first branch does not hide the malformed second branch.

Consequences:

- Reordering conditions does not change whether type errors are reported.
- Short-circuit evaluation is permitted after validation succeeds.
- Missing values remain unknown, not type errors.
- Conditions in definitively excluded rules do not require validation.

## 14. Explicit conditions and effects

A comparison node is a mapping with exactly three required fields: `field`, `operator`, and `value`. Unknown comparison fields are rejected. `field` is an attribute-path string following section 9; `operator` is a supported operator string. Omitting `value` is invalid, whereas `value: null` is an explicit null literal supported by `eq` and `neq`. List-valued operands are used only for `in` and `notIn`; mapping-valued operands are used only for `range` bounds. Other comparison operands are literals of the operator's supported scalar type.

Each rule is a mapping with exactly four required fields: `id`, `effect`, `scope`, and `condition`. Unknown rule fields are rejected. Rule IDs must match `^[A-Za-z0-9-]{1,50}$`, are case-sensitive, and must be unique within their policy.

Every rule requires an explicit condition. An unconditional rule uses:

```yaml
condition:
  always: true
```

“Unconditional” applies **within the rule’s scope**.

- Missing or null conditions are rejected.
- `always` accepts only literal `true`.
- Each condition node has exactly one form: comparison, `all`, `any`, `not`, or `always`.
- Rule effects are explicitly `allow` or `deny`; there is no default effect.
- Policies with no rules are rejected.

## 15. Server time

Time conditions use a trusted `server.time` attribute.

- AgentWall captures UTC time once per evaluation.
- Every rule in that evaluation sees the same instant.
- Clients cannot supply or override it.
- The value uses Unix epoch milliseconds as an int64.
- Tests inject a clock for reproducibility.

v0.1 supports absolute time windows. Recurring schedules and local-time rules remain outside scope.

A validity window uses `gte` for its start and `lt` for expiry, so it expires exactly at the end boundary.

## 16. Size and complexity limits

The agreed initial limits are:

| Limit | Maximum |
|---|---:|
| YAML document size | 256 KiB |
| Complete authorization JSON request body | 256 KiB (262,144 bytes) |
| Total object members per authorization request | 1,000 |
| Elements per request list | 100 |
| UTF-8 bytes per decoded request string value or object key | 2,048 |
| Policies per loaded set / immutable snapshot | 100 |
| Rules per policy | 100 |
| Condition nesting depth | 10 |
| Metadata nesting depth | 10 |
| Request-object nesting depth | 10 |
| Condition nodes per policy, including logical groups | 1,000 |
| Values per membership list | 100 |
| UTF-8 bytes per string literal or resource pattern | 2,048 |

The root condition has depth 1. Policies exceeding condition or metadata limits are rejected at load time. Requests exceeding the request-object depth limit are rejected during request validation. The complete authorization JSON request body is limited to 262,144 bytes, enforced before evaluation; larger bodies are rejected. The body-size limit measures serialized UTF-8 JSON bytes, not decoded string lengths. A request may contain at most 1,000 object members in total: count each key/value entry in the root object and every nested object, including objects inside lists. Requests exceeding this limit are rejected during request validation before evaluation. Each request string value and object key is limited to 2,048 UTF-8 bytes after JSON decoding, including scope target strings. Oversized decoded strings or keys are rejected during request validation before evaluation. Each request list may contain at most 100 elements. Check every list independently, including nested lists; an object or list element counts as one element of its containing list. The body-size, depth, and total object-member limits also apply. Lists exceeding 100 elements are rejected during request validation before evaluation. For metadata, the `metadata` mapping is depth 1; for requests, the top-level request object is depth 1. Each nested object or list adds 1 to the containing container’s depth. Scalar values add no depth. The maximum container depth is 10, including empty objects and lists. For example, `metadata: {ownership: {teams: [engineering]}}` has metadata depth 3.

A loaded set contains at most 100 policies. Each evaluation uses one snapshot and therefore evaluates no more than 100 policies. Combined with the per-policy limits, a snapshot contains at most 10,000 rules and 100,000 condition nodes. These are starting limits to validate with benchmarks, not a latency guarantee. Request limits apply together; satisfying one does not exempt a request from the others.

## 17. Strict loading and immutable representation

The loader rejects:

- Unknown fields outside the extensible `metadata` mapping.
- Duplicate YAML keys.
- Unsupported operators.
- YAML aliases.
- All explicitly written YAML tags, including standard tags such as `!!str` and `!!int`, as well as custom tags. Ordinary implicit YAML typing remains supported subject to schema validation.
- Invalid types and structures.
- Duplicate policy identities within a loaded set.
- Duplicate rule IDs within a policy.

The policy root is a mapping with exactly four required fields: `apiVersion`, `kind`, `metadata`, and `rules`. Rules are directly under `rules`, not under a `spec` wrapper. Unknown top-level fields are rejected. `apiVersion` must be `agentwall.dev/v1alpha1`, `kind` must be `AgentPolicy`, `metadata` must be a mapping, and `rules` must be a nonempty list of rules.

The standard policy filename is `agentwall-policy.yaml`. Each file contains exactly one YAML policy document; multiple documents are rejected. An empty loaded policy set is rejected.

`metadata` is required and must be a mapping. `metadata.name` is mandatory and is the policy identifier. Duplicate `metadata.name` values within a loaded set are rejected. The name must match `^[A-Za-z0-9-]{1,50}$`: 1–50 ASCII letters, digits, or hyphens. It is case-sensitive. Leading and trailing hyphens are permitted. Whitespace and all other characters are rejected. Rules require unique IDs within their policy.

An optional `metadata.description` is a string of at most 500 Unicode code points (Go runes), counted without normalization. The 2,048 UTF-8 byte string limit also applies.

All metadata object keys, including nested keys, must be nonempty strings of at most 2,048 UTF-8 bytes. Keys are case-sensitive and are not normalized. Numeric and composite YAML keys are rejected; duplicate keys remain rejected.

Users may add additional fields under `metadata` for descriptive information, such as `agent-name` or team ownership. These fields do not affect identity, scope, matching, or access decisions. The allowance for additional metadata is an explicit exception to unknown-field rejection; fields elsewhere remain strictly validated. Metadata remains subject to document-size limits and the YAML restrictions above. Additional metadata values may be strings, signed int64 numbers, booleans, null, lists, or nested objects. Booleans and null are also allowed inside lists and nested objects. Metadata nesting is limited to depth 10 using the container-counting convention in section 16. The 500-character limit applies specifically to `metadata.description`.

For an illustrative policy structure, see the [policy sample](policy-envelop-sample/policy-v1alpha1-sample.yaml). Its structure is specified in the [versioned schema contract](policy-schema-v1alpha1.md).

Attribute lookup returns a separate presence flag and tagged value, with lookup errors returned separately. Value kinds are null, string, int64, boolean, object, and list. Missing is represented by `present=false` (the returned value is ignored); explicit null is `present=true` with kind null. A nil Go value alone must not represent both states. Traversal through a null or scalar intermediate remains a type error under section 9.

YAML authoring structs and compiled runtime types are separate Go representations. Loading parses authoring data, validates it, and compiles it into runtime policies and condition nodes. Only validated constructors may create runtime policies and nodes. Runtime fields are unexported; constructors defensively copy maps, slices, and nested mutable values so authoring data or caller-owned inputs cannot mutate an active snapshot. Accessors must not expose writable references to runtime state. Immutability is enforced by the representation rather than relying on caller convention.

Loader and evaluator errors expose stable machine-readable categories: policy validation, request validation, runtime type mismatch, indeterminate scope, unavailable snapshot, and cancellation/deadline. Errors include relevant policy, rule, and field locations when available, without raw request values. HTTP status mapping belongs to the API contract. Errors remain separate from truth values and access decisions.

Validated policies compile into typed Go models and immutable condition trees. Policies cannot execute arbitrary code, scripts, embedded expressions, or network calls.

## 18. Versioning

A single version pins both syntax and semantics:

```yaml
apiVersion: agentwall.dev/v1alpha1
kind: AgentPolicy
```

That version defines missing/null handling, operator behavior, precedence, wildcard rules, and the schema.

- Unsupported versions are rejected at load time.
- Deliberate semantic changes require a new version.
- Policies never silently migrate.
- The service reports its evaluator implementation version separately for diagnostics and audit.

## 19. Atomic activation

Policy sets activate atomically:

1. Validate and compile the entire candidate set.
2. Activate it only if every policy passes.
3. If any policy fails, reject the whole update and retain the previous valid set.
4. Each evaluation uses one immutable snapshot.

If startup has no valid policy set, the service remains unready and evaluation requests return an unavailable error.

This defines loading behavior; it does not add hot reload to v0.1.

## 21. Shared acceptance fixture contract

Loader and evaluator acceptance tests use shared declarative fixtures. Each case declares:

- Policy files, including their paths and source contents.
- An authorization request for evaluation cases.
- An optional fixed server time for reproducible time-condition tests.
- The expected load result.
- The expected evaluation error category, when evaluation fails.
- The expected final allow/deny decision, only when evaluation succeeds.

Load-rejection cases stop at loading and have no expected evaluation result or decision. Evaluation cases require successful loading. Evaluation failures have an expected error category and no final decision. Successful evaluations have an expected decision and no evaluation error. Fixed server time is injected through the test clock, never supplied as a trusted request assertion.

AGE-11 consumes the loader cases; evaluator acceptance tests consume the same fixture contract. The concrete serialization, cases, sequential activation scenarios, runner, and boundary generators are documented in the [conformance corpus](../tests/policy_schema/README.md).

## 22. Compatibility and dependent work

The decisions tracked here are resolved for v1alpha1. Changes to syntax or semantics require a new version and explicit compatibility handling; policies never silently migrate. Production acceptance is established only when the Go implementations pass the shared corpus and their implementation-specific checks. The service remains a scaffold until those dependent tasks are complete.
