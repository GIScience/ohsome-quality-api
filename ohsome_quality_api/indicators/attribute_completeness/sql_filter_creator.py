import re


def translate_filter_to_sql(filter_str, tags_column="contributions.tags"):
    """
    Translates a generic filter string into an SQL filter format dynamically.
    """
    sql_parts = []

    # Match value of geometry/type (assuming there can only be one type)
    type_match = re.compile(r"type:([\w:]+)", re.IGNORECASE)
    for match in type_match.finditer(filter_str):
        key = match.groups()
        sql_parts.append([f"osm_type={key}"])
        sql_parts.append(" AND ")
    geometry_match = re.compile(r"geometry:([\w:]+)", re.IGNORECASE)
    for match in geometry_match.finditer(filter_str):
        key = match.groups()
        sql_parts.append(f"osm_type={key}")
        sql_parts.append(" AND ")

    # Match key IN (...) expressions
    in_pattern = re.compile(
        r"(\w+)\s+in\s+\(([^)]+)\)(?:\s+|\)\s+)?(\w+)?", re.IGNORECASE
    )
    for match in in_pattern.finditer(filter_str):
        key, values = match.group(1), match.group(2)
        values = values.replace(" ", "").replace(",", "', '")
        sql_parts.append(f"element_at({tags_column},'{key}') IS NOT NULL")
        sql_parts.append(" AND ")
        sql_parts.append(f"{tags_column}['{key}'] IN ('{values}')")

        sql_parts.append(f"{match.group(3)}")

    # Match key=value expressions
    equal_pattern = re.compile(r"(\w+)=([\w:]+)(?:\s+|\)\s+)?(\w+)?", re.IGNORECASE)
    for match in equal_pattern.finditer(filter_str):
        key, value = match.groups()
        sql_parts.append(f"element_at({tags_column},'{key}') IS NOT NULL")
        sql_parts.append(" AND ")
        sql_parts.append(f"{tags_column}['{key}'] = '{value}'")

        sql_parts.append(f"{match.group(3)}")

    # Match key=*
    exists_pattern = re.compile(r"(\w+)=\*(?:\s+|\)\s+)?(\w+)?", re.IGNORECASE)
    for match in exists_pattern.finditer(filter_str):
        key = match.group(1)
        sql_parts.append(f"element_at({tags_column}, '{key}') IS NOT NULL")

        sql_parts.append(f"{match.group(2)}")

    # Match key!=*
    not_exists_pattern = re.compile(r"(\w+)!=\*(?:\s+|\)\s+)?(\w+)?", re.IGNORECASE)
    for match in not_exists_pattern.finditer(filter_str):
        key = match.group(1)
        sql_parts.append(f"element_at({tags_column}, '{key}') IS NULL")

        sql_parts.append(f"{match.group(2)}")

    # Match key!=value expressions
    not_exists_pattern = re.compile(
        r"(\w+)!=([\w:]+)(?:\s+|\)\s+)?(\w+)?", re.IGNORECASE
    )
    for match in not_exists_pattern.finditer(filter_str):
        key, value = match.groups()
        sql_parts.append(f"{tags_column}['{key}'] != '{value}'")
        sql_parts.append(f"{match.group(3)}")

    exceptions = [" AND ", "and", "or", "(", ")"]

    # TODO: prevent "None" from happening
    sql_parts = [
        item
        for item in sql_parts
        if (sql_parts.count(item) == 1 or item in exceptions) and item != "None"
    ]

    result_sql = " ".join(sql_parts)

    return result_sql
