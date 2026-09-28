"""Keep public schema examples consistent with the runtime's initialized state."""
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from finance_core.core import blank, demo

ROOT = Path(__file__).resolve().parents[1]


class SchemaTests(unittest.TestCase):
    def test_initialized_state_and_examples_follow_public_schemas(self):
        schemas = {p.name: json.loads(p.read_text()) for p in (ROOT / "schemas").glob("*.json")}
        registry = Registry().with_resources(
            (f"https://finance.invalid/{name}", Resource.from_contents(schema)) for name, schema in schemas.items()
        )
        for schema in schemas.values():
            Draft202012Validator.check_schema(schema)

        def validate(name, value):
            Draft202012Validator({"$ref": f"https://finance.invalid/{name}"}, registry=registry,
                                 format_checker=FormatChecker()).validate(value)

        for state in (blank(), demo()):
            for name, value in state.items():
                validate(name.replace(".json", ".schema.json"), value)
        for name, schema in (("account-import.json", "import.schema.json"),
                             ("memory.json", "memory.schema.json"),
                             ("trade-proposal.json", "proposal.schema.json")):
            validate(schema, json.loads((ROOT / "examples" / name).read_text()))


if __name__ == "__main__":
    unittest.main()
