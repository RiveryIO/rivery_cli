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


def merge_lists(list1, list2):
    """
    not using set for the distinct operation
    in order to support unhashable type(s)
    """
    union_lists = [item for item in list1 if not isinstance(item, dict)] + \
                  [item for item in list2
                   if not isinstance(item, dict) and item not in list1]

    dicts_ = [item for item in list1 if isinstance(item, dict)] + \
             [item for item in list2
              if isinstance(item, dict) and item not in list1]

    merged_dicts = {}
    for item in dicts_:
        merged_dicts = recursively_merge_dictionaries(merged_dicts, item)

    union_lists.append(merged_dicts)
    return union_lists


def recursively_merge_dictionaries(updated_item, overwriting_item,
                                   union_lists=False):
    """self explanatory.
    notes:
    (1) a simple dict.update function does not give the requested result,
        hence the recursion
    (2) when updated_item and overwriting_item params share the same key,
        overwriting_item is stronger and will overwrite the value in
        updated_item"""
    res = updated_item
    for key, val in overwriting_item.items():
        if isinstance(val, list) and isinstance(updated_item.get(key), list) \
                and union_lists:
            res.update({key: merge_lists(val, updated_item.get(key))})
        elif not isinstance(val, dict) or key not in updated_item.keys():
            res.update({key: val})
        else:
            res[key] = recursively_merge_dictionaries(
                updated_item.get(key), val)
    return res