# -*- coding: utf-8 -*-

"""Scraper for FAIRsharing.

.. seealso:: https://beta.fairsharing.org/API_doc
"""

import json
from typing import Any, MutableMapping, Optional

from fairsharing_client import load_fairsharing

from bioregistry.constants import EXTERNAL
from bioregistry.license_standardizer import standardize_license
from bioregistry.utils import removeprefix, removesuffix

__all__ = [
    "get_fairsharing",
]

DIRECTORY = EXTERNAL / "fairsharing"
DIRECTORY.mkdir(exist_ok=True, parents=True)
PROCESSED_PATH = DIRECTORY / "processed.json"


ALLOWED_TYPES = {
    "terminology_artefact",
    "identifier_schema",
    # "knowledgebase",
    # "knowledgebase_and_repository",
    # "repository",
}


def get_fairsharing(force_download: bool = False, use_tqdm: bool = False):
    """Get the FAIRsharing registry."""
    if PROCESSED_PATH.exists() and not force_download:
        with PROCESSED_PATH.open() as file:
            return json.load(file)
    data = load_fairsharing(force_download=force_download, use_tqdm=use_tqdm)
    rv = {}
    for prefix, record in data.items():
        new_record = _process_record(record)
        if new_record:
            rv[prefix] = new_record
    with PROCESSED_PATH.open("w") as file:
        json.dump(rv, file, indent=2, ensure_ascii=False, sort_keys=True)
    return rv


KEEP = {
    "abbreviation",
    "description",
    "name",
    "subjects",
}


def _process_record(record: MutableMapping[str, Any]) -> Optional[MutableMapping[str, Any]]:
    if record.get("record_type") not in ALLOWED_TYPES:
        return None
    rv = {key: record[key] for key in KEEP}
    for suf in [
        " CT",
        " CV",
        " Controlled Vocabulary",
        " Terminology",
        " Ontology",
        " Thesaurus",
        " Vocabulary",
        " Taxonomy",
    ]:
        rv["abbreviation"] = removesuffix(rv["abbreviation"], suf)

    metadata = record.get("metadata", {})

    homepage = metadata.get("homepage")
    if homepage:
        rv["homepage"] = homepage

    rv["publications"] = [
        {k: publication[k] for k in ("doi", "pubmed_id", "title")}  # TODO add "year"
        for publication in record.get("publications", [])
        if publication.get("doi") or publication.get("pubmed_id")
    ]

    contacts = [
        {removeprefix(k, "contact_"): v for k, v in contact.items()}
        for contact in metadata.get("contacts", [])
        if contact.get("contact_orcid")  # make sure ORCID is available
    ]
    if contacts:
        rv["contact"] = contacts[0]

    for support_link in metadata.get("support_links", []):
        if support_link["type"] == "Twitter":
            rv["twitter"] = removeprefix(support_link["url"], "https://twitter.com/")
        if support_link["type"] == "Github":
            rv["repository"] = support_link["url"]

    for license_link in metadata.get("licence_links", []):
        license_standard = standardize_license(license_link.get("url"))
        if license_standard:
            rv["license"] = license_standard

    return rv


if __name__ == "__main__":
    get_fairsharing(force_download=True)
