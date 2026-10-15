# Operator truth tables for v1alpha1

`T`, `F`, `U`, and `E` mean true, false, unknown, and runtime type error. A source-level operand of an unsupported type is instead a policy-validation error. Missing input is never converted into null. Tables cover every supported operand type and runtime input kind; representative same-kind values expose equality and numeric boundaries.

Input columns: string=`engineering`, other-string=`sales`, int=5, other-int=6, bool=true, other-bool=false, object={}, list=[]. Null is explicit. `prefix` uses startsWith `eng`; gt/gte/lte use bound 5, lt uses bound 6, and range uses gte=5, lt=6. Equality/membership labels identify operands: string=`engineering`, int=5, bool=true, null=null, nullable=[`engineering`, null].

| Operand / operator | missing | null | string | other-string | int | other-int | bool | other-bool | object | list |
|---|---|---|---|---|---|---|---|---|---|---|
| eq-string | U | F | T | F | E | E | E | E | E | E |
| neq-string | U | T | F | T | E | E | E | E | E | E |
| eq-int | U | F | E | E | T | F | E | E | E | E |
| neq-int | U | T | E | E | F | T | E | E | E | E |
| eq-bool | U | F | E | E | E | E | T | F | E | E |
| neq-bool | U | T | E | E | E | E | F | T | E | E |
| eq-null | U | T | F | F | F | F | F | F | E | E |
| neq-null | U | F | T | T | T | T | T | T | E | E |
| in-string | U | F | T | F | E | E | E | E | E | E |
| notIn-string | U | T | F | T | E | E | E | E | E | E |
| in-nullable | U | T | T | F | E | E | E | E | E | E |
| notIn-nullable | U | F | F | T | E | E | E | E | E | E |
| in-int | U | F | E | E | T | F | E | E | E | E |
| notIn-int | U | T | E | E | F | T | E | E | E | E |
| in-bool | U | F | E | E | E | E | T | F | E | E |
| notIn-bool | U | T | E | E | E | E | F | T | E | E |
| prefix | U | E | T | F | E | E | E | E | E | E |
| gt | U | E | E | E | F | T | E | E | E | E |
| gte | U | E | E | E | T | T | E | E | E | E |
| lt | U | E | E | E | T | F | E | E | E | E |
| lte | U | E | E | E | T | F | E | E | E | E |
| range | U | E | E | E | T | F | E | E | E | E |

For any other value of the same scalar type, equality and membership use exact typed equality; numeric operators use signed int64 order; startsWith uses a case-sensitive prefix without normalization. Opposite results follow for neq/notIn. Optional null in integer or boolean membership lists has the same null-handling behavior as nullable string membership. Objects and lists always produce E for comparisons, including comparison to null. Floating-point or out-of-int64 request values are request-validation failures before these tables apply.

## Composition

| A | B | all | any |
|---|---|---|---|
| T | T | T | T |
| T | F | F | T |
| T | U | U | T |
| F | T | F | T |
| F | F | F | F |
| F | U | F | U |
| U | T | U | T |
| U | F | F | U |
| U | U | U | U |

| Input | not |
|---|---|
| T | F |
| F | T |
| U | U |

Any applicable type-validation error supersedes these truth tables; it cannot be hidden by a true any branch or false all branch. always evaluates to T within its scope.

## Rule combination

| Applicable deny results | Applicable allow results | Decision |
|---|---|---|
| Any T or U | Any | Deny |
| All F, or no applicable deny | At least one T | Allow |
| All F, or no applicable deny | Only F/U, or no applicable allow | Deny |

Scope false excludes a rule; unknown combined scope is an error. Any applicable validation/evaluation error invalidates the decision. Neither ordering nor pattern specificity changes the result.

The [shared corpus](../tests/policy_schema/fixtures/semantics.json) fixes concrete expected results independently of the test-only oracle. [Contract tests](../tests/policy_schema/test_contract.py) enforce operator/input-kind coverage and execute the corpus.
