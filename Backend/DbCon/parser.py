import json

CREATE_TYPE = 'create type default::'


def parse_ddl(_ddl: str):
    start, end = 0, 0
    res = {}
    while True:
        start = _ddl.find(CREATE_TYPE)
        if start == -1:
            break
        start += len(CREATE_TYPE)
        end = _ddl.find('{', start)
        type_name = _ddl[start:end].strip()
        res[type_name] = {}
        end = _ddl.find('};', start)
        _sub_ddl = _ddl[start:end]

        while True:
            start = _sub_ddl.find('property')
            if start == -1:
                break
            start += len('property')
            end = _sub_ddl.find('->') - 1
            prop_name = _sub_ddl[start:end].strip()
            start = _sub_ddl.find(' ', end+1)
            end2 = _sub_ddl.find('{', end+1)
            end = _sub_ddl.find(';', end+1)
            if end == -1 or end2 == -1:
                end = max(end, end2)
            else:
                end = min(end, end2)
            res[type_name][prop_name] = _sub_ddl[start:end].strip()
            _sub_ddl = _sub_ddl[end:]

        _ddl = _ddl[end:]
    return res


def create_ddl(table: str, fields: list | str, _filter: tuple = None):
    fields = [fields] if type(fields) is str else fields
    res = f"""
SELECT {table} {{
    {', '.join(fields)}
}} """
    if _filter and len(_filter) == 2:
        res += f"filter {table}.{_filter[0]} = '{_filter[1]}'"
    res += ';'
    return res


if __name__ == "__main__":
    ddl = "create module default if not exists;\ncreate future nonrecursive_access_policies;\ncreate scalar type " \
          "default::fuel_entry_id extending std::sequence;\ncreate type default::FuelEntry {\n    create required " \
          "property date -> cal::local_date;\n    create required property fuel -> std::float32;\n    create required "\
          "property mileage -> std::int64;\n    create required property num -> default::fuel_entry_id;\n};\ncreate " \
          "scalar type default::oil_entry_id extending std::sequence;\ncreate type default::OilEntry {\n    create " \
          "required property date -> cal::local_date;\n    create required property mileage -> std::int64;\n    " \
          "create required property num -> default::oil_entry_id;\n    create required property oil -> " \
          "std::float32;\n    create required property oil_level -> std::float32 {\n        create constraint " \
          "std::max_value(1.0);\n        create constraint std::min_value(0.0);\n    };\n};\ncreate scalar type " \
          "default::vape_puff_id extending std::sequence;\ncreate type default::VapePuff {\n    create required " \
          "property date -> cal::local_datetime;\n    create required property num -> default::vape_puff_id;\n    " \
          "create required property puffs -> std::int32;\n}; "
    print(json.dumps(parse_ddl(ddl), indent=4))

    print(create_ddl('User', 'username'))

    print(create_ddl('User', ['username', 'type']))
    print(create_ddl('User', ['username']))
    print(create_ddl('User', 'username', ('username', 'kipello')))
