"""Executable shared fixtures and exact boundary checks for AGE-7."""
import copy
import json
from pathlib import Path
import unittest

import yaml

import reference

FIXTURES = json.loads((Path(__file__).parent / 'fixtures/semantics.json').read_text())


def policy():
    return {'apiVersion': 'agentwall.dev/v1alpha1', 'kind': 'AgentPolicy',
            'metadata': {'name': 'example'}, 'rules': [
                {'id': 'rule', 'effect': 'allow', 'scope': {'resource': 'tools/read'},
                 'condition': {'always': True}}]}


class SourceDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


def files(value):
    return [{'path': 'agentwall-policy.yaml', 'source': yaml.dump(value, Dumper=SourceDumper, sort_keys=False)}]


class SharedFixtureTests(unittest.TestCase):
    def test_shared_cases(self):
        ids = set()
        self.assertEqual(FIXTURES['fixtureVersion'], 1)
        for case in FIXTURES['cases']:
            with self.subTest(case=case['id']):
                self.assertNotIn(case['id'], ids)
                ids.add(case['id'])
                expected = case['expected']
                self.assertEqual('decision' in expected, expected['load'] == 'ok' and 'error' not in expected)
                try:
                    policies = reference.load(case['files'])
                except reference.ContractError as error:
                    self.assertEqual(expected['load'], error.category)
                    self.assertNotIn('decision', expected)
                    continue
                self.assertEqual(expected['load'], 'ok')
                raw = json.dumps(case['request'], ensure_ascii=False)
                try:
                    decision = reference.evaluate(policies, raw, case.get('serverTimeMs', 0))
                except reference.ContractError as error:
                    self.assertEqual(expected.get('error'), error.category)
                    continue
                self.assertNotIn('error', expected)
                self.assertEqual(expected['decision'], decision)
                if 'truth' in expected:
                    context = reference.request(raw)
                    reference.validate_condition(policies[0]['rules'][0]['condition'], context)
                    truth = reference.truth(policies[0]['rules'][0]['condition'], context)
                    self.assertEqual(expected['truth'], {True: 'true', False: 'false', None: 'unknown'}[truth])

    def test_activation_contract(self):
        fixture = json.loads((Path(__file__).parent / 'fixtures/activation.json').read_text())
        snapshots = reference.Snapshots()
        handles = {}
        for index, step in enumerate(fixture['steps']):
            with self.subTest(step=index):
                expected = step.get('expected', {})
                try:
                    if step['operation'] == 'activate':
                        snapshots.activate(step['files'], step['revision'])
                        self.assertEqual(snapshots.acquire()[0], expected['revision'])
                    elif step['operation'] == 'acquire':
                        handles[step['handle']] = snapshots.acquire()
                    else:
                        revision, policies = handles[step['handle']] if 'handle' in step else snapshots.acquire()
                        decision = reference.evaluate(policies, json.dumps(fixture['request']))
                        self.assertEqual((revision, decision), (expected['revision'], expected['decision']))
                except reference.ContractError as error:
                    self.assertEqual(expected.get('error'), error.category)
                else:
                    self.assertNotIn('error', expected)

    def test_operator_matrix_coverage(self):
        # Every supported leaf operator has missing/null/valid/cross-type/container cases.
        coverage = {}
        for case in FIXTURES['cases']:
            if case['id'].split('/')[-1] not in {'missing', 'null', 'string', 'other-string', 'int', 'other-int', 'bool', 'other-bool', 'object', 'list'} or case['id'].startswith(('scope/', 'lookup/')):
                continue
            source = yaml.safe_load(case['files'][0]['source'])
            operator = source['rules'][0]['condition']['operator']
            coverage.setdefault(operator, set()).add(case['id'].split('/')[-1])
        self.assertEqual(set(coverage), {'eq', 'neq', 'in', 'notIn', 'startsWith', 'gt', 'gte', 'lt', 'lte', 'range'})
        for states in coverage.values():
            self.assertEqual(states, {'missing', 'null', 'string', 'other-string', 'int', 'other-int', 'bool', 'other-bool', 'object', 'list'})


class BoundaryTests(unittest.TestCase):
    def assert_rejected(self, operation, category):
        with self.assertRaises(reference.ContractError) as caught:
            operation()
        self.assertEqual(caught.exception.category, category)

    def test_document_bytes(self):
        source = files(policy())[0]['source']
        source += '#' + 'x' * (reference.MAX_BYTES - len(source.encode()) - 1)
        reference.load([{'source': source}])
        self.assert_rejected(lambda: reference.load([{'source': source + 'x'}]), 'policy_validation')

    def test_policy_count(self):
        sources = []
        for index in range(100):
            value = policy()
            value['metadata']['name'] = f'p-{index}'
            sources.extend(files(value))
        reference.load(sources)
        self.assert_rejected(lambda: reference.load(sources + files(policy())), 'policy_validation')

    def test_rule_count(self):
        value = policy()
        value['rules'] = [dict(value['rules'][0], id=f'r-{i}') for i in range(100)]
        reference.load(files(value))
        value['rules'].append(dict(value['rules'][0], id='extra'))
        self.assert_rejected(lambda: reference.load(files(value)), 'policy_validation')

    def test_condition_depth(self):
        value = policy()
        node = {'always': True}
        for _ in range(9):
            node = {'not': node}
        value['rules'][0]['condition'] = node
        reference.load(files(value))
        value['rules'][0]['condition'] = {'not': node}
        self.assert_rejected(lambda: reference.load(files(value)), 'policy_validation')

    def test_condition_nodes(self):
        value = policy()
        # Ten groups with 99 leaves each: 1,000 nodes, spread across ten rules.
        value['rules'] = [dict(value['rules'][0], id=f'r-{i}', condition={'all': [{'always': True} for _ in range(99)]}) for i in range(10)]
        reference.load(files(value))
        value['rules'][0]['condition']['all'].append({'always': True})
        self.assert_rejected(lambda: reference.load(files(value)), 'policy_validation')

    def test_metadata_depth_and_strings(self):
        value = policy()
        nested = {}
        for _ in range(9):
            nested = {'child': nested}
        value['metadata'] = dict(nested, name='example')
        reference.load(files(value))
        value['metadata']['extra'] = nested
        self.assert_rejected(lambda: reference.load(files(value)), 'policy_validation')
        for key in ['description', 'extra']:
            value = policy()
            value['metadata'][key] = 'é' * (500 if key == 'description' else 1024)
            reference.load(files(value))
            value['metadata'][key] += 'é'
            self.assert_rejected(lambda: reference.load(files(value)), 'policy_validation')
        value = policy()
        value['metadata']['k'*2048] = None
        reference.load(files(value))
        value['metadata']['k'*2049] = None
        self.assert_rejected(lambda: reference.load(files(value)), 'policy_validation')

    def test_multibyte_operands_and_list_depth(self):
        for field in ('path', 'resource', 'apiPath'):
            value = policy()
            prefix = '/' if field == 'apiPath' else ''
            target = prefix + 'é' * ((2048 - len(prefix)) // 2)
            value['rules'][0]['scope'] = {field: target}
            reference.load(files(value))
            value['rules'][0]['scope'][field] += 'é'
            self.assert_rejected(lambda: reference.load(files(value)), 'policy_validation')
        for operator in ('eq', 'startsWith', 'in'):
            value = policy()
            literal = 'é' * 1024
            node = {'field': 'user.x', 'operator': operator, 'value': [literal] if operator == 'in' else literal}
            value['rules'][0]['condition'] = node
            reference.load(files(value))
            node['value'] = [literal + 'é'] if operator == 'in' else literal + 'é'
            self.assert_rejected(lambda: reference.load(files(value)), 'policy_validation')
        nested = []
        for _ in range(8):
            nested = [nested]
        value = policy()
        value['metadata']['lists'] = nested  # Mapping depth 1 + nine lists.
        reference.load(files(value))
        value['metadata']['lists'] = [nested]
        self.assert_rejected(lambda: reference.load(files(value)), 'policy_validation')
        reference.request(json.dumps({'lists': nested}))
        self.assert_rejected(lambda: reference.request(json.dumps({'lists': [nested]})), 'request_validation')
        members = {'list': [{f'k{i}': None for i in range(999)}]}
        reference.request(json.dumps(members))
        members['list'][0]['extra'] = None
        self.assert_rejected(lambda: reference.request(json.dumps(members)), 'request_validation')

    def test_membership_and_integer_precision(self):
        value = policy()
        node = {'field': 'user.value', 'operator': 'in', 'value': list(range(100))}
        value['rules'][0]['condition'] = node
        reference.load(files(value))
        node['value'].append(100)
        self.assert_rejected(lambda: reference.load(files(value)), 'policy_validation')
        node.update(operator='eq', value=reference.MAX_INT)
        loaded = reference.load(files(value))
        self.assertEqual(reference.evaluate(loaded, json.dumps({'resource': 'tools/read', 'user': {'value': reference.MAX_INT}})), 'allow')
        self.assertEqual(reference.evaluate(loaded, json.dumps({'resource': 'tools/read', 'user': {'value': reference.MAX_INT-1}})), 'deny')

    def test_request_boundaries(self):
        category = 'request_validation'
        raw = '{"resource":"tools/read"}'
        padded = raw + ' ' * (reference.MAX_BYTES - len(raw))
        reference.request(padded)
        self.assert_rejected(lambda: reference.request(padded + ' '), category)
        value = {f'k{i}': None for i in range(1000)}
        reference.request(json.dumps(value))
        value['extra'] = None
        self.assert_rejected(lambda: reference.request(json.dumps(value)), category)
        for value in [{'list': [None]*100}, {'key': 'é'*1024}, {'k'*2048: None}]:
            reference.request(json.dumps(value))
        for value in [{'list': [None]*101}, {'key': 'é'*1025}, {'k'*2049: None}]:
            self.assert_rejected(lambda value=value: reference.request(json.dumps(value)), category)
        nested = {}
        for _ in range(9):
            nested = {'child': nested}
        reference.request(json.dumps(nested))
        self.assert_rejected(lambda: reference.request(json.dumps({'child': nested})), category)
        self.assert_rejected(lambda: reference.request('{"x":1,"x":2}'), category)
        self.assert_rejected(lambda: reference.request('{"x":1.0}'), category)


if __name__ == '__main__':
    unittest.main()
