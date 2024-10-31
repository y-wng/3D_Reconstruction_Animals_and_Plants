import os
import shutil
import json

def check_and_move_folders(root_folder):
    json_fil_path = './wangyi_522030910147/filtrated_data/data_description.json'
    with open(json_fil_path, 'r') as file:
        json_fil = json.load(file)
    for folder_name in os.listdir(root_folder):
        folder_path = os.path.join(root_folder, folder_name)
        output_file = os.path.join(folder_path, 'output.txt')

        if os.path.isdir(folder_path) and os.path.isfile(output_file):
            with open(output_file, 'r') as f:
                content = f.read()
                
                if "likely not a plant or animal" in content:
                    f.close()
                    # shutil.rmtree('./wangyi_522030910147/filtrated_data/'+folder_name)
                    # shutil.rmtree('./wangyi_522030910147/rendered_data/'+folder_name)
                    with open('./log/filtrate_log/not_pa.txt', 'a') as f_1:
                        f_1.write(folder_name+'\n')
                    if folder_name in json_fil:
                        del json_fil[folder_name]
                else:
                    species = extract_species(content)  # 提取species
                    f.close()
                    move_folder(folder_name, species)  # 移动文件夹
    with open(json_fil_path, 'w') as file:
        json.dump(json_fil, file, indent=4)


def extract_species(content):
    # 提取species
    lines = content.splitlines()
    for line in lines:
        if "species" in line:
            return line.split("species:")[-1].strip().split(',')[0]  # 获取species
    return None

def move_folder(folder_name, species):
    target_folder_1 = os.path.join('./wangyi_522030910147/filtrated_data', species.lower() + 's')
    os.makedirs(target_folder_1, exist_ok=True)  # 创建目标文件夹
    shutil.move('./wangyi_522030910147/filtrated_data/'+folder_name, target_folder_1)  # 移动文件夹
    target_folder_1 = os.path.join('./wangyi_522030910147/rendered_data', species.lower() + 's')
    os.makedirs(target_folder_1, exist_ok=True)  # 创建目标文件夹
    shutil.move('./wangyi_522030910147/rendered_data/'+folder_name, target_folder_1)  # 移动文件夹

# # 使用示例
# root_folder = './rendered_data'
# check_and_move_folders(root_folder)
