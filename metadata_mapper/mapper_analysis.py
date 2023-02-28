from lambda_shepherd import get_collection
from lambda_function import map_page
import settings
import os
import json
import csv


def generate_csv(collection_id, mapper_type, vernacular_fields="*", mapped_fields="*"):
    raw_rows = _get_data(collection_id, mapper_type, vernacular_fields, mapped_fields)

    shared_keys = _get_shared_keys(raw_rows)

    rows = []
    for raw_row in raw_rows:
        row = {}
        for key in shared_keys:
            row.update({key: raw_row.get(key, "")})
        rows.append(row)

    with open("export.csv", "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(shared_keys)
        for row in rows:
            writer.writerow(row.values())

def _do_that_thing_up_there:
    pass


def _get_shared_keys(rows: [dict]) -> [dict]:
    """
    Finds the shared keys in a list of dictionaries
    """
    shared_keys = []
    for row in rows:
        keys = row.keys()
        for key in keys:
            if key not in shared_keys:
                shared_keys.append(key)
    return shared_keys


# Payload is incomplete
def _get_data(collection_id, mapper_type, vernacular_fields, mapped_fields):
    if not collection_id:
        raise Exception("Collection id must be provided")

    collection = get_collection(collection_id)

    if not collection:
        raise Exception(f"Collection id {collection_id} not found")

    payload = {"collection": collection, "collection_id": collection_id,
               "mapper_type": mapper_type, "return_mapping": True}

    vernacular_path = settings.local_path(
        'vernacular_metadata', collection_id)

    page_list = [f for f in os.listdir(vernacular_path)
                 if os.path.isfile(os.path.join(vernacular_path, f))]

    all_records = []
    for page in page_list:
        payload.update({'page_filename': page})
        records = map_page(json.dumps(payload), {})
        all_records.extend(records)

    rows = []
    for i in range(len(all_records)):
        source_row = _prepend_keys(_show_fields(all_records[i].source_metadata, vernacular_fields), "V: ")
        mapped_row = _prepend_keys(_show_fields(all_records[i].mapped_data, mapped_fields), "M: ")

        row = source_row
        row.update(mapped_row)
        rows.append(row)

    return rows


def _show_fields(dicts, fields):
    if fields == '*':
        return dicts

    return {k: v for (k, v) in dicts.items() if k in fields}


def _prepend_keys(source_dict, prepend):
    keys = source_dict.keys()

    new_dict = {}
    for key in keys:
        new_key = f"{prepend}{key}"
        new_dict.update({new_key: source_dict[key]})
    return new_dict


if __name__ == "__main__":
    print("Run this script from the python console")
