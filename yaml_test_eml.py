
# import xmlplain

# # Read the YAML file
# with open("dwca_eml_metadata/smhi_bacterioplankton_nat.yml") as inf:
#   root = xmlplain.obj_from_yaml(inf)

# # Output back XML
# with open("example-1.new.xml", "w") as outf:
#   xmlplain.xml_from_obj(root, outf, pretty=True)

import pathlib
import yaml
import dict2xml
import collections.abc


def create_eml_xml():
    """ """
    dwca_file_path = pathlib.Path("dwca_config/dwca_bacterioplankton_nat.yaml")

    with open(dwca_file_path) as file:
        dwca_config = yaml.load(file, Loader=yaml.FullLoader)

    target_dict = {}
    yaml_path = pathlib.Path()
    if "emlDefinitions" in dwca_config:
        eml_definitions = dwca_config["emlDefinitions"]
        if  "directory" in eml_definitions:
            yaml_path = pathlib.Path(yaml_path, eml_definitions["directory"])
        if "files" in eml_definitions:
            for yaml_file in eml_definitions["files"]:
                yaml_file_path = pathlib.Path(yaml_path, yaml_file)
                with open(yaml_file_path, encoding="utf8") as file:
                    print("DEBUG: Processing ", file)
                    dwca_new_data = yaml.load(file, Loader=yaml.FullLoader)
                    dict_deep_update(target_dict, dwca_new_data)

    eml_xml = {}
    eml_xml["dataset"] = target_dict["dataset"]
    eml_xml["additionalMetadata"] = target_dict["additionalMetadata"]
    eml_xml_rows = dict2xml.dict2xml(eml_xml, indent = "    ")

    xml_rows = []
    for row in target_dict.get("emlHeader", []):
        xml_rows.append(row)
    xml_rows.append("")
    for row in eml_xml_rows.splitlines():
        xml_rows.append(row)
    for row in target_dict.get("emlFooter", []):
        xml_rows.append(row)

    # print("\n\n", "EML-XML:")
    # print("\n\n", "\n".join(xml_rows))

    target_config = dwca_config.get("dwcaTarget", {}) 
    target_dir = target_config.get("directory", "")
    target_file = target_config.get("file", "")
    eml_xml_path = pathlib.Path(target_file)
    if target_dir:
        target_path = pathlib.Path(target_dir)
        if not target_path.exists():
            target_path.mkdir(parents=True)
        eml_xml_path = pathlib.Path(target_path, target_file)
    # 
    with eml_xml_path.open("w", encoding="utf8") as out_file:
        out_file.write("\n".join(xml_rows))


def dict_deep_update(target, updates):
    """ Recursively updates or extends a dict. """
    for key, value in updates.items():
        if value == "REMOVE":
            del target[key]
        elif isinstance(value, collections.abc.Mapping):
            target[key] = dict_deep_update(target.get(key, {}), value)
        else:
            target[key] = value
    return target

if __name__ == "__main__":
    """ """
    create_eml_xml()