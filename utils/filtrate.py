import os
import shutil

def check_and_move_folders(root_folder):
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
                else:
                    species = extract_species(content)  # 提取species
                    f.close()
                    move_folder(folder_name, species)  # 移动文件夹


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
