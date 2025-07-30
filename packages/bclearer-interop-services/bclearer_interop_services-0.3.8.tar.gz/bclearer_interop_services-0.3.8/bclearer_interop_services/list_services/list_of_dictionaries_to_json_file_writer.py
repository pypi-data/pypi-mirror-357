import json


# TODO: move to intero_services
def write_list_of_dictionaries_to_json_file(
    output_file_path: str,
    list_of_dictionaries: list,
) -> None:
    with open(
        output_file_path, "w"
    ) as output_file:
        for (
            entry
        ) in list_of_dictionaries:
            json.dump(
                entry, output_file
            )
            output_file.write("\n")
