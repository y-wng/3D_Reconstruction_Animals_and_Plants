import shutil
import os

if os.path.exists('./wangyi_522030910147'):
    shutil.rmtree('./wangyi_522030910147')
if os.path.exists('./log'):
    shutil.rmtree('./log')

os.makedirs('./log/filtrate_log')
os.makedirs('./log/render_log')
os.makedirs('./log/glb2mesh_log')

clear_glb_data = True
if clear_glb_data:
    folder_path = './glb_data'
    for filename in os.listdir(folder_path):
        if 'gitkeep' in filename:
            continue
        file_path = os.path.join(folder_path, filename)
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)  # 删除子文件夹及其内容
        else:
            os.remove(file_path)  # 删除文件
