from utils.render import Render
from utils.get_objtexture import GLB2OBJ
from utils.folder_copy import copy_folder_contents
import os
import shutil
import gc

if __name__ == '__main__':
    gc.enable()
    dir_name = os.path.dirname(os.path.abspath(__file__))

    glb2obj=GLB2OBJ(model_dir=dir_name + '/glb_data', save_dir=dir_name + '/wangyi_522030910147/collected_data')
    glb2obj.process()

    shutil.copy(dir_name + '/glb_data/data_description.json', dir_name + '/wangyi_522030910147/collected_data')
    copy_folder_contents(source_folder=dir_name + '/wangyi_522030910147/collected_data',
                        destination_folder=dir_name + '/wangyi_522030910147/filtrated_data')

