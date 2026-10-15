# Go policy representation contract

Status: AGE-7 implementation specification. Production parsing/normalization belongs to AGE-11; production evaluation and snapshot lifecycle have their own implementation tasks.

This specification accompanies the [schema](policy-schema-v1alpha1.md), [semantics](policy-semantics.md), and [acceptance corpus](../tests/policy_schema/README.md). Names below describe the intended package boundary, not a promise that these Go symbols already exist.

## Authoring representation

Decode YAML source nodes before constructing typed authoring structs. Do not decode straight into zero-valued structs: absent `value` and `value: null`, missing bounds and zero bounds, and missing booleans and false booleans must remain distinguishable. Source validation rejects duplicate keys, aliases, explicit tags, malformed nodes, floats and out-of-int64 integers before normalization. Preserve source locations for diagnostics. Never parse numbers through float64.

The authoring model consists of PolicyDocument (`apiVersion`, `kind`, MetadataDocument, []RuleDocument); RuleDocument (`id`, Effect, ScopeDocument, ConditionDocument); and a discriminated ConditionDocument. Each comparison carries an explicitly present operand node even when null. A scope uses presence-aware optional strings; only supplied keys become compiled matchers. Metadata has required Name, optional Description with presence, and a recursively typed extension map. Name and description cannot be overridden through that extension map.

Logical forms are distinct variants, not a permissive struct where several forms can be populated at once. Decode metadata numbers as int64, not generic floating-point JSON values. The source document and runtime representation have separate ownership.

## Compiled representation

The following Go type sketch fixes the representation and ownership contract. Production constructors and evaluator functions are intentionally not implemented by AGE-7.

```go
package policy

type Truth uint8
const (
    TruthUnknown Truth = iota + 1
    TruthFalse
    TruthTrue
)

type Decision uint8
const (
    Deny Decision = iota + 1
    Allow
)

type Effect uint8
const (
    EffectAllow Effect = iota + 1
    EffectDeny
)

type valueKind uint8
const (
    kindNull valueKind = iota + 1
    kindString
    kindInt64
    kindBool
    kindObject
    kindList
)

type value struct {
    kind valueKind
    text string
    integer int64
    boolean bool
    object map[string]value
    list []value
}

// Comparisons use scalar values only; object/list kinds are forbidden here.
type scalar struct {
    kind valueKind
    text string
    integer int64
    boolean bool
}

type conditionKind uint8
const (
    conditionComparison conditionKind = iota + 1
    conditionAll
    conditionAny
    conditionNot
    conditionAlways
)

type operator uint8
const (
    operatorEq operator = iota + 1
    operatorNeq
    operatorIn
    operatorNotIn
    operatorStartsWith
    operatorGt
    operatorGte
    operatorLt
    operatorLte
    operatorRange
)

type condition struct {
    kind conditionKind
    field []string
    operator operator
    literal scalar
    members []scalar
    lower int64 // Inclusive compiled range endpoint.
    upper int64 // Inclusive compiled range endpoint.
    children []condition
}

type scopeField uint8
const (
    scopePath scopeField = iota + 1
    scopeResource
    scopeAPIPath
)

type patternSegment struct {
    literal string
    wildcard uint8 // 0: literal, 1: *, 2: terminal **.
}

type matcher struct {
    field scopeField
    absolute bool
    segments []patternSegment
}

type rule struct {
    id string
    effect Effect
    scope []matcher
    condition condition
}

type policy struct {
    name string
    description string
    hasDescription bool
    metadata map[string]value
    rules []rule
}

type Snapshot struct {
    revision string
    policies []policy
}

type ErrorCategory string
const (
    PolicyValidation ErrorCategory = "policy_validation"
    RequestValidation ErrorCategory = "request_validation"
    RuntimeTypeMismatch ErrorCategory = "runtime_type_mismatch"
    IndeterminateScope ErrorCategory = "indeterminate_scope"
    UnavailableSnapshot ErrorCategory = "unavailable_snapshot"
    CancellationDeadline ErrorCategory = "cancellation_deadline"
)

type ContractError struct {
    Category ErrorCategory
    Policy string
    Rule string
    Field string
    Source string
    Line int
    Column int
    Cause error
}
```

Zero enum values are invalid and never meaningful defaults. Constructors enforce variant invariants: comparison nodes have no children; all/any have at least one child; not has exactly one; always has no operand or children. Range endpoints are compiled to a nonempty inclusive int64 interval using overflow-safe checks. Membership retains the non-null element kind even when null is included. Nonselected fields in a tagged representation remain inaccessible and are ignored internally; validated construction is the only route to usable runtime nodes.

Matchers retain case, absolute/relative form, literal segments, and wildcard kinds without normalization. Root `/` has absolute=true and zero segments. A matcher reads only the corresponding top-level request field. Empty scope is not representable after validation. Field references compile to owned path-segment slices.

All fields containing runtime state are unexported. Constructors deep-copy maps, slices, and recursively nested values. Accessors return scalar values or defensive copies, never writable references. Snapshot policies, rules, metadata, matcher segments, and condition trees are immutable after publication. Metadata is retained for descriptive inspection, not inserted into evaluation context.

## Lookup, validation, and evaluation interfaces

The conceptual lookup signature is `lookup(context, segments) (value, present bool, err error)`. Absent keys return present=false with an ignored value. Explicit null returns present=true with kindNull. An intermediate non-object, including null, returns a RuntimeTypeMismatch error. Context objects and lists are validated and owned for the duration of evaluation; caller mutation must not race with evaluation.

Condition evaluation returns `(Truth, error)` and decision evaluation returns `(Decision, error)`. Any non-nil error invalidates the accompanying result. Implement ContractError.Error and Unwrap without formatting raw request values; preserve cancellation and deadline causes for errors.Is. Locations identify source policy/rule/field where relevant. Multiple simultaneous errors need not have a stable diagnostic order; rule order must never change success versus failure or allow versus deny.

The evaluation sequence is:

1. Validate request structure, limits, supplied targets, authentication/assertion constraints at the integration boundary. Client-supplied `server.time` is rejected; a supplied non-object `server` cannot contain the trusted time and is invalid. Other trust permissions remain in the caller assertion contract.
2. Acquire one immutable snapshot; without one return UnavailableSnapshot. Capture UTC time once through an injected clock and represent it as epoch milliseconds in int64.
3. Determine all rule scopes. False excludes a rule, true includes it, unknown is an IndeterminateScope error. A false scope component dominates unknown under AND. All supplied scope targets have already passed request validation.
4. Validate every comparison in every applicable condition tree, including branches whose truth would permit short-circuiting. Missing values are not type errors. Any runtime type failure returns RuntimeTypeMismatch before a decision, even when another rule establishes deny.
5. Evaluate applicable trees using three-valued logic. Unknown allows grant nothing; true or unknown denies block. Return Allow only with at least one true allow and all applicable denies false. Otherwise return Deny.

Short-circuiting is allowed only after validation. No condition performs network/database I/O. Check context cancellation/deadlines between bounded work units; cancellation is an error and never a policy denial. API status mappings are outside this type contract.

## Snapshot preparation and ownership

Compile every candidate policy before publication. A failed set never replaces the active snapshot. Publication replaces one snapshot pointer atomically; an evaluation holds its acquired pointer throughout and reports its revision. Old snapshots remain usable until their readers finish. Never mutate an active snapshot to apply updates. With no initial valid snapshot the service remains unready and returns UnavailableSnapshot. This specifies atomic activation, not a new v0.1 hot-reload feature or persistent-bundle implementation.

The test-only reference harness checks decision and preparation contracts. It does not establish Go immutability, race safety, cancellation propagation, or service integration; dependent production tasks must test those properties against their actual implementations.
