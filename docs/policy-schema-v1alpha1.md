# AgentPolicy v1alpha1 schema contract

Status: Schema contract for AGE-7; loader implementation and full acceptance suite pending.

The [JSON Schema](schemas/agentpolicy-v1alpha1.schema.json) describes the structural policy format. This document and [policy semantics](policy-semantics.md) define mandatory checks beyond JSON Schema. Passing the structural schema alone is insufficient to activate a policy. These artifacts jointly specify `agentwall.dev/v1alpha1`; semantics do not silently change within this version.

## Document and policy set

The standard source filename is `agentwall-policy.yaml`. Each file contains exactly one YAML document, whose root is a mapping. Multiple policies use separate files, for example in separate directories. Directory placement has no matching or precedence effect. A loaded set contains 1–100 policies with unique, case-sensitive `metadata.name` values.

The root contains exactly these required fields:

| Field | Type and constraints |
|---|---|
| `apiVersion` | Literal string `agentwall.dev/v1alpha1` |
| `kind` | Literal string `AgentPolicy` |
| `metadata` | Mapping described below |
| `rules` | List of 1–100 rule mappings |

All other root fields are rejected. Missing and null required fields are invalid.

## Metadata

`metadata.name` is required, case-sensitive, and matches `^[A-Za-z0-9-]{1,50}$`. Leading and trailing hyphens are allowed. `metadata.description` is optional; when present it must be a string of at most 500 Unicode code points without normalization, also limited to 2,048 UTF-8 bytes. Empty descriptions are permitted.

Other metadata keys may hold strings, signed int64 numbers, booleans, null, lists, or nested mappings, recursively. Metadata never changes policy identity or authorization behavior except that `name` identifies the policy. All metadata keys, including nested keys, are nonempty, case-sensitive strings of at most 2,048 UTF-8 bytes, without normalization. Non-string keys are rejected. Metadata string values are limited to 2,048 UTF-8 bytes.

Metadata container depth is at most 10. The `metadata` mapping is depth 1, each nested mapping or list adds 1, and scalars add none. Empty containers count. Additional metadata lists have no separate 100-element limit; the membership-list limit applies to conditions, and the request-list limit applies to requests. Document size and metadata depth still apply.

## Rules and scope

Each rule contains exactly four required fields:

| Field | Type and constraints |
|---|---|
| `id` | String matching `^[A-Za-z0-9-]{1,50}$`, unique within the policy, case-sensitive |
| `effect` | Literal string `allow` or `deny` |
| `scope` | Mapping with at least one field from the table below |
| `condition` | Exactly one condition form described below |

Scope contains only `path`, `resource`, and/or `apiPath`. Each value is a pattern string of at most 2,048 UTF-8 bytes and matches the same-named top-level request attribute. Multiple fields combine using three-valued AND.

| Scope field | Syntax |
|---|---|
| `path` | Relative or absolute file/directory path; `/` is a valid root |
| `resource` | Resource name with no leading or trailing slash |
| `apiPath` | Absolute API path with a required leading slash; `/` is valid |

All patterns are case-sensitive, match the whole target, and use `/` as the separator. `*` occupies a whole segment and matches exactly one nonempty segment. `**` occupies a whole terminal segment and matches one or more segments. A standalone `**` (or absolute `/**`) is valid and does not match an empty target (or root). Partial-segment wildcards are invalid. Empty targets, repeated slashes, trailing slashes except root, and `.`/`..` segments are rejected. Matching performs no normalization or percent decoding; relative and absolute paths remain distinct.

Concrete request targets reject `*` anywhere. Every supplied target must be a string with valid corresponding path syntax, validated before evaluation even if no policy references it. Missing targets produce unknown only in scopes that reference them. False combined scope excludes the rule; unknown combined scope is an evaluation error. Conditions of excluded rules need no runtime type validation.

## Conditions

A condition is a mapping in exactly one of these forms, with no additional keys:

| Form | Exact keys and values |
|---|---|
| Comparison | `field`, `operator`, `value`, all required |
| Conjunction | `all`: nonempty list of child condition mappings |
| Disjunction | `any`: nonempty list of child condition mappings |
| Negation | `not`: one child condition mapping directly, never a list |
| Constant | `always`: literal boolean `true` |

`field` is a case-sensitive dot-separated attribute path with each segment matching `[A-Za-z_][A-Za-z0-9_]*`. Array indexes, escaped dots, wildcard segments, and attribute-to-attribute comparisons are unsupported.

| Operator | Literal `value` |
|---|---|
| `eq`, `neq` | String, int64, boolean, or null; never a container |
| `in`, `notIn` | 1–100 values: one non-null scalar type, optionally including null |
| `startsWith` | Nonempty string |
| `gt`, `gte`, `lt`, `lte` | Int64 |
| `range` | Nonempty mapping containing only int64 `gt`, `gte`, `lt`, `lte` bounds |

Membership values must be unique under the agreed typed equality semantics. Null-only and mixed non-null-type lists are rejected as policy validation type errors. Empty strings remain valid for equality and membership. All string literals have a 2,048 UTF-8 byte limit.

Ranges may have one or both sides. `gt` and `gte` cannot coexist; `lt` and `lte` cannot coexist. A range must contain at least one representable int64 value. Validate this without overflow: `gt: 9223372036854775807` and `lt: -9223372036854775808` are invalid. With effective inclusive endpoints, require lower <= upper; unspecified sides extend to the int64 minimum or maximum.

Each rule's root condition is depth 1. Logical children add 1; YAML sequence containers do not add condition depth. Every condition mapping counts as a node, including logical groups and `always`; operands and range bounds do not count as nodes. Maximum condition depth is 10 and maximum total condition nodes across a policy is 1,000.

## Mandatory preparation checks beyond structural schema

Run these checks before compiling or activating a candidate set:

1. Enforce the 256 KiB (262,144-byte) YAML document limit before parsing. Preserve integer precision without any float64 conversion.
2. Reject multiple documents, duplicate YAML keys, aliases, and all explicit tags, including standard tags. Reject non-string mapping keys and unsupported scalar/container types. Implicit scalar resolution must yield the schema's string, int64, boolean, null, mapping, or list types; values must not be silently coerced to make them pass.
3. Validate the decoded structure against the versioned schema, or equivalent strict typed validation. Reject floats and out-of-int64 numbers. JSON Schema's mathematical `integer` check is insufficient to enforce the source-level ban on float literals such as `1.0`; validate source scalar types too.
4. Enforce UTF-8 byte limits. JSON Schema `maxLength` counts Unicode code points, so its string limits are only a preliminary check except for the description's explicit code-point limit.
5. Enforce metadata depth, condition depth and node counts, unique rule IDs, unique policy names, and policy-set count.
6. Reject integer-empty ranges using the int64 domain and confirm membership typing and uniqueness. Match syntax must consume the complete string; no normalization is allowed.
7. Compile into immutable runtime types and activate only after the entire candidate set passes preparation. Failed updates retain the prior valid snapshot.

The schema does not encode YAML source restrictions, byte limits, recursive depth limits, total node counts, identity uniqueness by field, policy-set constraints, or integer-range satisfiability. Loader logic must implement them. It also does not replace runtime type validation, three-valued evaluation, or deny precedence.

## Request and evaluation boundary

Authorization requests are limited to 262,144 serialized JSON bytes, depth 10, 1,000 total object members, 100 elements per list, and 2,048 UTF-8 bytes per decoded string/key. Root request depth is 1; nested objects/lists add 1 and scalars add none. These are request-validation checks, not fields in a policy document.

All applicable rule conditions pass runtime type validation before any condition evaluation or final decision. Missing and null remain distinct. Evaluation errors invalidate results; unknown deny conditions block access, unknown allow conditions grant nothing, deny overrides allow, and absence of a true allow defaults to deny. See the semantic document for truth tables, trusted server time, error categories, immutable models, and atomic activation.

## Sample and acceptance status

The [sample policy](policy-envelop-sample/policy-v1alpha1-sample.yaml) uses this structure and should be deployed under the standard filename. Acceptance must cover both schema checks and mandatory preparation checks. Structural validation examples do not constitute a production loader or the exhaustive shared fixture suite required to finish AGE-7.

Structural checks are in [test_schema.py](../tests/policy_schema/test_schema.py). With Python packages `jsonschema` and `PyYAML` available, run:

```sh
python3 -m unittest discover -s tests/policy_schema -v
```

These are development checks and introduce no Go service dependency. They verify the schema itself, the repository sample, and representative positive/negative structures; they do not claim exhaustive semantic acceptance coverage.
