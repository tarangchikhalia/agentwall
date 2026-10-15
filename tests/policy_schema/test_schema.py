"""Structural schema checks. Run with Python, jsonschema, and PyYAML installed.

These do not implement the mandatory loader checks in docs/policy-schema-v1alpha1.md.
"""

import copy
import json
import unittest
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads(
    (ROOT / "docs/schemas/agentpolicy-v1alpha1.schema.json").read_text()
)


class PolicySchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        jsonschema.Draft202012Validator.check_schema(SCHEMA)
        cls.validator = jsonschema.Draft202012Validator(SCHEMA)
        cls.sample = yaml.safe_load(
            (
                ROOT / "docs/policy-envelop-sample/policy-v1alpha1-sample.yaml"
            ).read_text()
        )

    def test_sample(self):
        self.validator.validate(self.sample)

    def check_condition(self, condition, valid):
        policy = copy.deepcopy(self.sample)
        policy["rules"][0]["condition"] = condition
        self.assertEqual(self.validator.is_valid(policy), valid, condition)

    def test_conditions(self):
        cases = [
            ({"always": True}, True),
            ({"always": False}, False),
            ({"all": []}, False),
            ({"any": []}, False),
            ({"not": {"always": True}}, True),
            ({"not": [{"always": True}]}, False),
            ({"always": True, "not": {"always": True}}, False),
        ]
        for op, value, valid in [
            ("eq", None, True),
            ("neq", False, True),
            ("eq", {}, False),
            ("eq", [], False),
            ("eq", 1.5, False),
            ("in", ["engineering", None], True),
            ("in", [True, None], True),
            ("in", [], False),
            ("in", [None], False),
            ("in", ["engineering", 5], False),
            ("in", ["a", "a"], False),
            ("in", [True, 1], False),
            ("in", list(range(101)), False),
            ("startsWith", "", False),
            ("startsWith", "eng", True),
            ("gt", 5, True),
            ("gte", "5", False),
            ("lt", -9223372036854775808, True),
            ("lte", 9223372036854775808, False),
            ("range", {"gte": 1, "lt": 4096}, True),
            ("range", {}, False),
            ("range", {"gt": 1, "gte": 2}, False),
            ("range", {"gte": 1, "unknown": 2}, False),
            ("unsupported", 1, False),
        ]:
            cases.append(
                (
                    {"field": "request.token_count", "operator": op, "value": value},
                    valid,
                )
            )
        cases.append(({"field": "user.department", "operator": "eq"}, False))
        for condition, valid in cases:
            with self.subTest(condition=condition):
                self.check_condition(condition, valid)

    def test_scope(self):
        for key, target, valid in [
            ("resource", "tools/github/*", True),
            ("resource", "tools/github/**", True),
            ("resource", "**", True),
            ("resource", "/tools", False),
            ("resource", "tools/", False),
            ("resource", "tools//read", False),
            ("resource", "tools/../read", False),
            ("resource", "read*", False),
            ("resource", "tools/**/read", False),
            ("path", "src/main.go", True),
            ("path", "/src/**", True),
            ("path", "/", True),
            ("apiPath", "/", True),
            ("apiPath", "/repos/*", True),
            ("apiPath", "/**", True),
            ("apiPath", "repos/*", False),
            ("apiPath", "/repos/", False),
        ]:
            policy = copy.deepcopy(self.sample)
            policy["rules"][0]["scope"] = {key: target}
            with self.subTest(key=key, target=target):
                self.assertEqual(self.validator.is_valid(policy), valid)
        for scope in [{}, {"unknown": "target"}]:
            policy = copy.deepcopy(self.sample)
            policy["rules"][0]["scope"] = scope
            self.assertFalse(self.validator.is_valid(policy))

    def test_envelope_and_metadata(self):
        for name, valid in [
            ("A-1", True),
            ("-name-", True),
            ("a" * 50, True),
            ("", False),
            ("a" * 51, False),
            ("a b", False),
            ("café", False),
            ("name\n", False),
        ]:
            policy = copy.deepcopy(self.sample)
            policy["metadata"]["name"] = name
            with self.subTest(name=name):
                self.assertEqual(self.validator.is_valid(policy), valid)
        policy = copy.deepcopy(self.sample)
        policy["metadata"]["extra"] = {"flags": [True, None, {"number": 1}]}
        self.validator.validate(policy)
        for key in self.sample:
            policy = copy.deepcopy(self.sample)
            del policy[key]
            self.assertFalse(self.validator.is_valid(policy))
        for key in self.sample["rules"][0]:
            policy = copy.deepcopy(self.sample)
            del policy["rules"][0][key]
            self.assertFalse(self.validator.is_valid(policy))
        for mutate in [
            lambda p: p.update(unknown=True),
            lambda p: p.update(apiVersion="agentwall.dev/v2"),
            lambda p: p.update(rules=[]),
            lambda p: p["metadata"].update(description="x" * 501),
            lambda p: p["metadata"].update(extra=1.5),
            lambda p: p["rules"][0].update(unknown=True),
        ]:
            policy = copy.deepcopy(self.sample)
            mutate(policy)
            self.assertFalse(self.validator.is_valid(policy))


if __name__ == "__main__":
    unittest.main()
