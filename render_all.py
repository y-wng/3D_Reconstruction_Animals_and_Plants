from utils.render import Render
import os
dir_name = os.path.dirname(os.path.abspath(__file__))

renderer = Render(model_dir=dir_name + '/glb_data', save_dir=dir_name + '/wangyi_522030910147/rendered_data')
renderer.renderAll()