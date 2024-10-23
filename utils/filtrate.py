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
                    shutil.rmtree(folder_path)
                    os.remove('./glb_data/'+folder_name+'.glb')
                    os.remove('./glb_data/'+folder_name+'.txt')
                else:
                    species = extract_species(content)  # 提取species
                    f.close()
                    move_folder(folder_path, species)  # 移动文件夹
                    move_glb(folder_name, species)  # 移动文件夹


def extract_species(content):
    # 提取species
    lines = content.splitlines()
    for line in lines:
        if "species" in line:
            return line.split("species:")[-1].strip().split(',')[0]  # 获取species
    return None

def move_folder(folder_path, species):
    target_folder = os.path.join(os.path.dirname(folder_path), species.lower() + 's')
    os.makedirs(target_folder, exist_ok=True)  # 创建目标文件夹
    shutil.move(folder_path, target_folder)  # 移动文件夹

def move_glb(folder_name, species):
    target_folder = os.path.join('./glb_data', species.lower() + 's')
    os.makedirs(target_folder, exist_ok=True)  # 创建目标文件夹
    file_path=os.path.join('./glb_data',folder_name+'.glb')
    file2_path=os.path.join('./glb_data',folder_name+'.txt')
    shutil.move(file_path, target_folder)  
    shutil.move(file2_path, target_folder)
# # 使用示例
# root_folder = './rendered_data'
# check_and_move_folders(root_folder)
