import re


def translate_filter_to_sql(filter_str, tags_column="contributions.tags"):
    """
    Translates an ohsome filter string into an SQL filter format.
    """

    parts = re.split(r"(\(|\))", filter_str)

    result = []
    for part in parts:
        if part not in ("(", ")"):
            split_part = re.split(r"\b(and|or)\b", part)
            result.extend([p.strip() for p in split_part if p.strip()])
        else:
            result.append(part)

    sql_parts = []
    for substring in result:
        if substring in ("(", ")", "and", "or"):
            sql_parts.append(substring)
        else:
            sql_parts.append(substring_converter(substring))

    for substring in sql_parts:
        if "osm_type = " in substring:
            sql_parts.remove(substring)
            sql_parts.insert(0, substring)

    if sql_parts[-1] in ("and", "or"):
        sql_parts = sql_parts[:-1]

    result_sql = " ".join(sql_parts)

    return result_sql


def substring_converter(substring, tags_column="contributions.tags"):
    # TODO: for all re.compile check if last group can be removed (artifact)

    # key IN
    match = re.search(r"([\w\S]+)\s+in(?:\s|$)", substring)
    if match:
        key = match.group(1)
        return (
            f"element_at({tags_column},'{key}') IS NOT NULL AND "
            f"{tags_column}['{key}'] IN "
        )

    type_match = re.search(r"type:([\w:]+)", substring)
    if type_match:
        key = type_match.group(1)
        return f"osm_type = '{key}' AND "

    geometry_match = re.search(r"geometry:([\w:]+)", substring)
    if geometry_match:
        key = geometry_match.group(1)
        return f"osm_type={key} AND "

    # Match key=value expressions
    equal_pattern = re.compile(r"(\w+)=([\w:]+)(?:\s+|\)\s+)?(\w+)?", re.IGNORECASE)
    for match in equal_pattern.finditer(substring):
        key, value = match.groups()
        return (
            f"element_at({tags_column},'{key}') IS NOT NULL AND "
            f"{tags_column}['{key}'] = '{value}'"
        )

    # Match key=*
    exists_pattern = re.compile(r"(\w+)=\*(?:\s+|\)\s+)?(\w+)?", re.IGNORECASE)
    for match in exists_pattern.finditer(substring):
        key = match.group(1)
        return f"element_at({tags_column}, '{key}') IS NOT NULL "

    # Match key!=*
    not_exists_pattern = re.compile(r"(\w+)!=\*(?:\s+|\)\s+)?(\w+)?", re.IGNORECASE)
    for match in not_exists_pattern.finditer(substring):
        key = match.group(1)
        return f"element_at({tags_column}, '{key}') IS NULL"

    # Match key!=value expressions
    not_exists_pattern = re.compile(
        r"(\w+)!=([\w:]+)(?:\s+|\)\s+)?(\w+)?", re.IGNORECASE
    )
    for match in not_exists_pattern.finditer(substring):
        key, value = match.groups()
        return f"{tags_column}['{key}'] != '{value}'"

    # list of values for "key IN (...)"
    if re.fullmatch(r"^[^,]+(?:\s*,\s*[^,]+)*$", substring):
        formatted_string = ""
        values = re.split(r",\s*", substring)
        for value in values:
            formatted_string = formatted_string + f"'{value}', "
        # remove last ", "
        return formatted_string[:-2]

    else:
        raise (ValueError)
