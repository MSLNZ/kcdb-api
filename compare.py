"""Download the JSON schema and compare with the definitions in this package."""

# cSpell: ignore annotationlib
from __future__ import annotations

try:
    from annotationlib import get_annotations
except ModuleNotFoundError:
    msg = "Requires the annotationlib module which was added in Python 3.14"
    raise ModuleNotFoundError(msg) from None

import json
import re
from pathlib import Path
from typing import Any
from urllib.request import urlopen

from msl.kcdb import ChemistryBiology, Physics, Radiation, types
from msl.kcdb.kcdb import SyncKCDB

path = Path("compare.json")
if path.exists():
    data = path.read_bytes()
else:
    response = urlopen("https://www.bipm.org/api/kcdb/v3/api-docs", timeout=10)
    if response.status != 200:  # noqa: PLR2004
        msg = "Did not return HTTP 200 status code"
        raise RuntimeError(msg)
    data = response.read()
    _ = path.write_bytes(data)

api = json.loads(data)
schemas = api["components"]["schemas"]

renamed_map = {
    "ResultChemistryAndBiology": types.ResultChemistryBiology,
    "ResultsChemistryAndBiology": types.ResultsChemistryBiology,
    "ResultsQuick": types.ResultsQuickSearch,
}

search_map = {
    "QuickSearchCriteria": SyncKCDB.quick_search,
    "SearchCriteriaChemistryAndBiology": ChemistryBiology.search,
    "SearchCriteriaPhysics": Physics.search,
    "SearchCriteriaRadiation": Radiation.search,
}


def to_snake_case(text: str) -> str:
    """Convert camelCase and PascalCase to snake_case."""
    str1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", text)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", str1).lower()


def convert_properties(p: dict[str, Any]) -> dict[str, str]:  # noqa: C901, PLR0912
    """Convert a 'properties' field in the schema into a `name: annotation` mapping."""
    out: dict[str, str] = {}
    for k, v in p.items():
        if v.get("$ref"):
            *_, typ = v["$ref"].rsplit("/", 1)
        elif v["type"] == "array":
            if "type" in v["items"]:
                sub = v["items"]["type"]
                if sub == "string":
                    typ = "str"
                else:
                    assert sub == "object", sub  # noqa: S101
                    assert v["items"]["description"] == "The results data", v  # noqa: S101
                    typ = "dict[str, Any]"
            else:
                *_, last = v["items"]["$ref"].rsplit("/", 1)
                typ = last
                if typ == "ResultChemistryAndBiology":
                    typ = "ResultChemistryBiology"
            typ = f"list[{typ}]"
        elif v["type"] == "string":
            typ = "str"
        elif v["type"] == "integer":
            typ = "int"
        elif v["type"] == "number":
            typ = "float"
        elif v["type"] == "boolean":
            typ = "bool"
        else:
            msg = f"Unhandled type {v['type']!r}"
            raise RuntimeError(msg)

        key = to_snake_case(k)

        if k in {"uncertaintyMode", "crmUncertaintyMode"}:
            assert typ == "str"  # noqa: S101
            typ = "AbsoluteRelative"
        elif k == "uncertaintyConvention":
            assert typ == "str"  # noqa: S101
            typ = "UncertaintyConvention"
        elif k == "measurmentTechnique":  # spelling mistake in KCDB cSpell:disable-line
            key = "measurement_technique"

        out[key] = typ

    return out


for k, v in schemas.items():
    print("Comparing", k)  # noqa: T201

    if k == "ResultsDomain":
        api = convert_properties(v["properties"])
        assert api == {"domains": "list[Domain]"}, api  # noqa: S101
        assert v["properties"]["domains"]["items"]["$ref"] == "#/components/schemas/Domain", v  # noqa: S101
        continue

    if k == "ResultsReferenceData":
        api = convert_properties(v["properties"])
        assert api == {"reference_data": "list[ReferenceData]"}, api  # noqa: S101
        assert v["properties"]["referenceData"]["items"]["$ref"] == "#/components/schemas/ReferenceData", v  # noqa: S101
        continue

    msl: dict[str, str]
    if k in search_map:
        api = {k.removesuffix("_label"): v for k, v in convert_properties(v["properties"]).items()}
        msl = {
            k: v.removesuffix(" | None")
            .removesuffix(" | Analyte")
            .removesuffix(" | Category")
            .removesuffix(" | date")
            .removesuffix(" | MetrologyArea")
            .removesuffix(" | Branch")
            .removesuffix(" | Status")
            .removesuffix(" | IndividualService")
            .removesuffix(" | SubService")
            .removesuffix(" | Service")
            .removesuffix(" | Medium")
            .removesuffix(" | Nuclide")
            .removesuffix(" | Quantity")
            .removesuffix(" | Source")
            .replace("Iterable", "list")
            .replace("str | Country | list[str | Country]", "list[str]")
            for k, v in search_map[k].__annotations__.items()
            if k != "return"
        }
        msl = dict(sorted(msl.items()))
        if api != msl:
            msg = f"Different for {k!r}\n\nAPI={api}\n\nMSL={msl}"
            raise RuntimeError(msg)
        continue

    cls = renamed_map[k] if k in renamed_map else getattr(types, k)
    msl = {}
    for obj in cls.__mro__[:-1]:
        msl.update(get_annotations(obj))
    msl = dict(sorted(msl.items()))
    msl = {k: v.removesuffix(" | None") for k, v in msl.items()}

    api = convert_properties(v["properties"])
    if api != msl:
        msg = f"Different for {k!r}\n\nAPI={api}\n\nMSL={msl}\n\n"
        for key, val in api.items():
            if key not in msl or val != msl[key]:
                msg += f"API -> {key}: {val}\n"
        for key, val in msl.items():
            if key not in api or val != api[key]:
                msg += f"MSL -> {key}: {val}\n"
        raise RuntimeError(msg)
