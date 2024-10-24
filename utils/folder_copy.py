import os
import shutil

def copy_folder_contents(source_folder, destination_folder):
    # 确保目标文件夹存在，如果不存在则创建
    os.makedirs(destination_folder, exist_ok=True)

    # 遍历源文件夹中的所有文件和子文件夹
    for item in os.listdir(source_folder):
        source_path = os.path.join(source_folder, item)
        destination_path = os.path.join(destination_folder, item)

        # 如果是文件，复制文件
        if os.path.isfile(source_path):
            shutil.copy2(source_path, destination_path)
        # 如果是文件夹，递归复制文件夹
        elif os.path.isdir(source_path):
            shutil.copytree(source_path, destination_path)


