"""Test-only AGE-7 contract oracle, not the production Go loader or evaluator."""
import json
from pathlib import Path

import jsonschema
import yaml

MIN_INT, MAX_INT = -(2**63), 2**63 - 1
MAX_BYTES = 262144
SCHEMA = json.loads((Path(__file__).resolve().parents[2] / 'docs/schemas/agentpolicy-v1alpha1.schema.json').read_text())
VALIDATOR = jsonschema.Draft202012Validator(SCHEMA)


class ContractError(Exception):
    def __init__(self, category):
        self.category = category
        super().__init__(category)


def require(condition, category):
    if not condition:
        raise ContractError(category)


def inspect_value(value, category, depth=1, metadata=False):
    """Validate decoded types and container depth, and count object members."""
    if isinstance(value, (dict, list)):
        require(depth <= 10, category)
        if isinstance(value, dict):
            members = len(value)
            for key, child in value.items():
                require(type(key) is str and (not metadata or key != ''), category)
                require(len(key.encode('utf-8')) <= 2048, category)
                members += inspect_value(child, category, depth + 1, metadata)
            return members
        require(metadata or len(value) <= 100, category)
        return sum(inspect_value(child, category, depth + 1, metadata) for child in value)
    if type(value) is str:
        require(len(value.encode('utf-8')) <= 2048, category)
    elif type(value) is int:
        require(MIN_INT <= value <= MAX_INT, category)
    else:
        require(value is None or type(value) is bool, category)
    return 0


def valid_target(value, field, pattern):
    if type(value) is not str or not value or len(value.encode('utf-8')) > 2048:
        return False
    if field == 'resource' and value.startswith('/'):
        return False
    if field == 'apiPath' and not value.startswith('/'):
        return False
    if value == '/':
        return field != 'resource'
    parts = value.removeprefix('/').split('/')
    for index, part in enumerate(parts):
        if not part or part in ('.', '..'):
            return False
        if '*' in part:
            if not pattern or part not in ('*', '**'):
                return False
            if part == '**' and index != len(parts) - 1:
                return False
    return True


def decode_source(source):
    category = 'policy_validation'
    require(len(source.encode('utf-8')) <= MAX_BYTES, category)
    try:
        tokens = list(yaml.scan(source))
        require(not any(isinstance(t, (yaml.tokens.AliasToken, yaml.tokens.TagToken)) for t in tokens), category)
        documents = list(yaml.compose_all(source))
        require(len(documents) == 1 and documents[0] is not None, category)

        def visit(node):
            if isinstance(node, yaml.MappingNode):
                keys = []
                for key, value in node.value:
                    require(isinstance(key, yaml.ScalarNode) and key.tag == 'tag:yaml.org,2002:str', category)
                    require(key.value not in keys, category)
                    keys.append(key.value)
                    visit(value)
            elif isinstance(node, yaml.SequenceNode):
                for child in node.value:
                    visit(child)
            else:
                require(node.tag in {'tag:yaml.org,2002:' + t for t in ('str', 'int', 'bool', 'null')}, category)
        visit(documents[0])
        return yaml.safe_load(source)
    except (yaml.YAMLError, RecursionError, ValueError) as error:
        raise ContractError(category) from error


def check_condition(node, depth=1):
    require(depth <= 10, 'policy_validation')
    if 'all' in node or 'any' in node:
        return 1 + sum(check_condition(child, depth + 1) for child in node.get('all', node.get('any')))
    if 'not' in node:
        return 1 + check_condition(node['not'], depth + 1)
    if 'operator' in node:
        value = node['value']
        if type(value) is str:
            require(len(value.encode('utf-8')) <= 2048, 'policy_validation')
        if isinstance(value, list):
            for item in value:
                require(type(item) is not float, 'policy_validation')
                if type(item) is str:
                    require(len(item.encode('utf-8')) <= 2048, 'policy_validation')
        if node['operator'] == 'range':
            lower = value.get('gte', value.get('gt', MIN_INT))
            upper = value.get('lte', value.get('lt', MAX_INT))
            lower += 'gt' in value
            upper -= 'lt' in value
            require(MIN_INT <= lower <= upper <= MAX_INT, 'policy_validation')
    return 1


def check_scalar_types(value):
    """JSON Schema permits integral floats; the source contract rejects them."""
    if isinstance(value, dict):
        for child in value.values():
            check_scalar_types(child)
    elif isinstance(value, list):
        for child in value:
            check_scalar_types(child)
    else:
        require(type(value) in (str, int, bool, type(None)), 'policy_validation')


def load(files):
    require(1 <= len(files) <= 100, 'policy_validation')
    policies, names = [], set()
    for file in files:
        policy = decode_source(file['source'])
        require(VALIDATOR.is_valid(policy), 'policy_validation')
        check_scalar_types(policy)
        inspect_value(policy['metadata'], 'policy_validation', metadata=True)
        name = policy['metadata']['name']
        require(name not in names, 'policy_validation')
        names.add(name)
        ids, nodes = set(), 0
        for rule in policy['rules']:
            require(rule['id'] not in ids, 'policy_validation')
            ids.add(rule['id'])
            for field, pattern in rule['scope'].items():
                require(valid_target(pattern, field, True), 'policy_validation')
            nodes += check_condition(rule['condition'])
        require(nodes <= 1000, 'policy_validation')
        policies.append(policy)
    return policies


def request(raw):
    require(len(raw.encode('utf-8')) <= MAX_BYTES, 'request_validation')
    def object_pairs(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, 'request_validation')
            result[key] = value
        return result
    try:
        value = json.loads(raw, object_pairs_hook=object_pairs)
    except (ValueError, RecursionError) as error:
        raise ContractError('request_validation') from error
    require(type(value) is dict, 'request_validation')
    require(inspect_value(value, 'request_validation') <= 1000, 'request_validation')
    for field in ('path', 'resource', 'apiPath'):
        if field in value:
            require(valid_target(value[field], field, False), 'request_validation')
    if isinstance(value.get('server'), dict):
        require('time' not in value['server'], 'request_validation')
    return value


def lookup(context, field):
    value = context
    for segment in field.split('.'):
        require(type(value) is dict, 'runtime_type_mismatch')
        if segment not in value:
            return False, None
        value = value[segment]
    return True, value


def scalar_type(value):
    return type(value) in (str, int, bool, type(None))


def validate_condition(node, context):
    if 'all' in node or 'any' in node:
        for child in node.get('all', node.get('any')):
            validate_condition(child, context)
    elif 'not' in node:
        validate_condition(node['not'], context)
    elif 'operator' in node:
        present, value = lookup(context, node['field'])
        if not present:
            return
        op, literal = node['operator'], node['value']
        if op in ('eq', 'neq', 'in', 'notIn'):
            require(scalar_type(value), 'runtime_type_mismatch')
            if isinstance(literal, list):
                literal = next(item for item in literal if item is not None)
            require(value is None or literal is None or type(value) is type(literal), 'runtime_type_mismatch')
        else:
            require(type(value) is (str if op == 'startsWith' else int), 'runtime_type_mismatch')


def truth(node, context):
    if 'always' in node:
        return True
    if 'not' in node:
        value = truth(node['not'], context)
        return None if value is None else not value
    if 'all' in node or 'any' in node:
        is_all = 'all' in node
        values = [truth(child, context) for child in node['all' if is_all else 'any']]
        decisive = False if is_all else True
        if decisive in values:
            return decisive
        return None if None in values else not decisive
    present, value = lookup(context, node['field'])
    if not present:
        return None
    op, literal = node['operator'], node['value']
    if op in ('eq', 'neq'):
        equal = type(value) is type(literal) and value == literal
        return equal if op == 'eq' else not equal
    if op in ('in', 'notIn'):
        contained = any(type(value) is type(item) and value == item for item in literal)
        return contained if op == 'in' else not contained
    if op == 'startsWith':
        return value.startswith(literal)
    bounds = literal if op == 'range' else {op: literal}
    return all({'gt': value > bound, 'gte': value >= bound, 'lt': value < bound, 'lte': value <= bound}[operator] for operator, bound in bounds.items())


def pattern_match(pattern, target):
    if pattern.startswith('/') != target.startswith('/'):
        return False
    if pattern == '/' or target == '/':
        return pattern == target
    pattern_parts = pattern.removeprefix('/').split('/')
    target_parts = target.removeprefix('/').split('/')
    for index, part in enumerate(pattern_parts):
        if part == '**':
            return index < len(target_parts)
        if index >= len(target_parts) or part not in ('*', target_parts[index]):
            return False
    return len(pattern_parts) == len(target_parts)


def evaluate(policies, raw, time_ms=0):
    context = request(raw)
    # Trusted time replaces only the reserved time attribute, once per evaluation.
    server = context.get('server', {})
    require(type(server) is dict, 'request_validation')
    context['server'] = dict(server, time=time_ms)
    applicable = []
    unknown_scope = False
    for policy in policies:
        for rule in policy['rules']:
            components = [None if field not in context else pattern_match(pattern, context[field]) for field, pattern in rule['scope'].items()]
            if False in components:
                continue
            if None in components:
                unknown_scope = True
            else:
                applicable.append(rule)
    require(not unknown_scope, 'indeterminate_scope')
    for rule in applicable:
        validate_condition(rule['condition'], context)
    allow, blocked = False, False
    for rule in applicable:
        result = truth(rule['condition'], context)
        if rule['effect'] == 'deny' and result is not False:
            blocked = True
        if rule['effect'] == 'allow' and result is True:
            allow = True
    return 'allow' if allow and not blocked else 'deny'


class Snapshots:
    """Sequential activation oracle; production concurrency must be tested in Go."""
    def __init__(self):
        self.current = None

    def activate(self, files, revision):
        prepared = load(files)
        self.current = (revision, prepared)

    def acquire(self):
        require(self.current is not None, 'unavailable_snapshot')
        return self.current
