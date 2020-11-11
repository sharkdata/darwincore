

import pathlib
import yaml
import dict2xml
import collections.abc


def do_it():
    """ """
    dwca_file_path = pathlib.Path("dwca_config/dwca_bacterioplankton_nat.yaml")

    with open(dwca_file_path) as file:
        dwca_config = yaml.load(file, Loader=yaml.FullLoader)

    target_dict = {}
    yaml_path = pathlib.Path()
    if "sourceKeys" in dwca_config:
        source_keys_config = dwca_config["sourceKeys"]
        if  "directory" in source_keys_config:
            yaml_path = pathlib.Path(yaml_path, source_keys_config["directory"])
        if "files" in source_keys_config:
            for yaml_file in source_keys_config["files"]:
                yaml_file_path = pathlib.Path(yaml_path, yaml_file)
                with open(yaml_file_path, encoding="utf8") as file:
                    print("DEBUG: Processing ", file)
                    dwca_new_data = yaml.load(file, Loader=yaml.FullLoader)
                    dict_deep_update(target_dict, dwca_new_data)

    print("\n\nDEBUG: \n", target_dict.get("sourceKeys", {}))
    print("\n\nDEBUG: \n", yaml.dump(target_dict.get("sourceKeys", {})))


    dataset_data = []




    



if __name__ == "__main__":
    """ """
    do_it()