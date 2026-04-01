from typing import Iterator

import yaml


def flatten_sequence(input_seq: dict | list | tuple | set) -> list:
    """Returns the given input sequence as a list.

    If the input is a dict, it returns all values.
    """
    output = []
    if isinstance(input_seq, dict):
        input_seq = input_seq.values()
    for val in input_seq:
        if isinstance(val, dict | list | tuple | set):
            output += flatten_sequence(val)
        else:
            output.append(val)
    return output


def filter_dictonary_by_keys(dictonary: dict, whitelist: list | tuple) -> dict:
    if not isinstance(dictonary, dict):
        return dictonary
    result = {}
    for key, value in dictonary.items():
        if key in whitelist:
            if isinstance(value, dict):
                result[key] = filter_dictonary_by_keys(value, whitelist)
            else:
                result[key] = value
        elif isinstance(value, dict):
            filtered_value = filter_dictonary_by_keys(value, whitelist)
            if filtered_value:
                result[key] = filtered_value
    return result


def pybabel_yaml_extractor(
    fileobj,
    keywords,
    comment_tags,
    options: dict,
) -> Iterator[tuple[str, str, str, str]]:
    """Method for extracting localizable text from YAML files.

    Usage:
        pybabel_yaml_extractor(fileobj, options={"keys": "name,description"})

    Complies with the following interface:
    https://babel.readthedocs.io/en/latest/messages.html#writing-extraction-methods
    """
    if "keys" in options:
        keys = options["keys"].split(",")
    else:
        raise ValueError("Options should contain non-empty `keys` item.")
    content = yaml.safe_load(fileobj)
    filtered = filter_dictonary_by_keys(content, keys)
    flattened = flatten_sequence(filtered)
    for string in flattened:
        yield ("", "", string, "")
