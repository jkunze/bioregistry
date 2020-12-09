# -*- coding: utf-8 -*-

"""Align MIRIAM with the Bioregistry."""

from ..external.miriam import get_miriam_registry
from ..utils import norm, updater

MIRIAM_KEYS = {
    'id',
    'prefix',
    'pattern',
    'namespaceEmbeddedInLui',
    'name',
    'deprecated',
    'description',
}


@updater
def align_miriam(registry):
    """Update MIRIAM references."""
    miriam_id_to_bioregistry_id = {
        entry['miriam']['id']: key
        for key, entry in registry.items()
        if 'miriam' in entry
    }

    miriam_registry = get_miriam_registry(mappify=True)

    miriam_prefix_to_miriam_id = {
        norm(miriam_entry['prefix']): miriam_entry['mirId'].removeprefix('MIR:')
        for miriam_entry in miriam_registry.values()
    }
    for key, entry in registry.items():
        if 'miriam' in entry:
            continue
        miriam_id = miriam_prefix_to_miriam_id.get(norm(key))
        if miriam_id is not None:
            entry['miriam'] = {'id': miriam_id}
            miriam_id_to_bioregistry_id[miriam_id] = key

    for miriam_entry in miriam_registry.values():
        miriam_id = miriam_entry['mirId'].removeprefix('MIR:')

        # Get key by checking the miriam.id key
        bioregistry_id = miriam_id_to_bioregistry_id.get(miriam_id)
        if bioregistry_id is None:
            continue

        miriam_entry = {k: v for k, v in miriam_entry.items() if k in MIRIAM_KEYS}
        miriam_entry['id'] = miriam_id

        if bioregistry_id is not None:
            registry[bioregistry_id]['miriam'] = miriam_entry
        else:
            prefix = miriam_entry['prefix']
            registry[prefix] = {
                'miriam': miriam_entry,
                'synonyms': [prefix],
            }
    return registry


if __name__ == '__main__':
    align_miriam()
