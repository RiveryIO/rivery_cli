import collections


def recursive_update(source, overrides, overwrite_nones=False):
    """Update a nested dictionary or similar mapping.

    Modify ``source`` in place.
    """
    for key, value in overrides.items():
        if value is not None and not overwrite_nones or (overwrite_nones is True):
            if isinstance(value, collections.Mapping):
                returned = recursive_update(source.get(key, {}), value)
                source[key] = returned
            else:
                source[key] = overrides[key]
    return source
