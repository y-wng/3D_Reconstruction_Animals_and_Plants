from utils.render import Render
import os
import json


def parse_txt_file(file_path):
    print(f"processing: {file_path}")
    with open(file_path, "r", encoding="utf-8", errors='ignore') as file:
        content = file.read()

    tags = []
    download_link = None

    lines = content.split("\n")

    tags_start = False
    for line in lines:
        if line.strip() == "tags:":
            tags_start = True
            continue
        if tags_start and line.strip():
            tags.append(line.strip())
        elif tags_start and not line.strip():
            tags_start = False

    for line in lines:
        if line.startswith("download_link:"):
            download_link = line.split(":", 1)[1].strip()
            break

    if not tags or not download_link:
        print(f"Warn: Missing [tags] or [download_link] in file {file_path}, deleted")
        file_name = file_path.split('.t')[0] + '.glb'
        os.remove(file_name)
        return None, None

    return file_path.split("/")[-1][:-4], {
        "tags": tags,
        "download_link": download_link,
    }


def process_folder(folder_path, output_json_path):
    data = {}

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                k, v = parse_txt_file(file_path)
                if k:
                    data[k] = v
                os.remove(file_path)

    with open(output_json_path, "a", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4)


if __name__ == "__main__":
    # TODO: enter directory
    folder_path = "./glb_data"
    # TODO: enter json file name
    output_json_path = "./glb_data/data_description.json"
    process_folder(folder_path, output_json_path)
    
    dir_name = os.path.dirname(os.path.abspath(__file__))

    renderer = Render(model_dir=dir_name + '/glb_data', save_dir=dir_name + '/wangyi_522030910147/rendered_data'
                      ,gpu_in_use=False)
    renderer.renderAll()