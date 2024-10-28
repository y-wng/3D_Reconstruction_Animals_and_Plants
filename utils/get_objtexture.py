import bpy
import bpy.ops as ops
import shutil
import sys
import os
from contextlib import contextmanager

class GLB2OBJ:
    def __init__(self,model_dir:str, save_dir:str) -> None:
        self.model_dir = model_dir
        self.save_dir = save_dir
        self.Objects = bpy.data.objects
        self.Scene = bpy.data.scenes["Scene"]
        
    @contextmanager
    def stdout_redirected(self, to=os.devnull):#disable print
        '''
        import os

        with stdout_redirected(to=filename):
            print("from Python")
            os.system("echo non-Python applications are also supported")
        '''
        fd = sys.stdout.fileno()

        ##### assert that Python and C stdio write using the same file descriptor
        ####assert libc.fileno(ctypes.c_void_p.in_dll(libc, "stdout")) == fd == 1

        def _redirect_stdout(to):
            sys.stdout.close() # + implicit flush()
            os.dup2(to.fileno(), fd) # fd writes to 'to' file
            sys.stdout = os.fdopen(fd, 'w',encoding='utf8') # Python writes to fd

        with os.fdopen(os.dup(fd), 'w') as old_stdout:
            with open(to, 'w') as file:
                _redirect_stdout(to=file)
            try:
                yield # allow code to be run with the redirected stdout
            finally:
                _redirect_stdout(to=old_stdout) # restore stdout.
                                                # buffering and flags such as
                                                # CLOEXEC may be different
    def process(self):
        
        ops.object.mode_set(mode='OBJECT')
        ops.object.select_all(action='SELECT')
        ops.object.delete()

        if not os.path.exists('log/glb2mesh_log/current_id.txt'):
            current_id = 0
        else:
            # 打开文件以读取模式
            with open('log/glb2mesh_log/current_id.txt', 'r') as file:
                # 读取文件内容并转换为整数
                current_id = int(file.read())

        glb_names=[name for name in os.listdir(self.model_dir) if name.endswith('.glb')]
        if len(glb_names) - current_id==0:
            raise Exception('No \'.glb\' file is found')
        num_names=len(glb_names) - current_id
        for Index in range(num_names):
            try:
                fileID=glb_names[Index + current_id].split('.')[0]
                with self.stdout_redirected():
                    filepath=os.path.join(self.model_dir,glb_names[Index + current_id])
                    ops.import_scene.gltf(filepath=filepath)
                    
                ops.object.mode_set(mode='OBJECT')
                ops.object.select_all(action='SELECT')  
                
                if not os.path.exists(os.path.join(self.save_dir,fileID)):
                    os.makedirs(name=os.path.join(self.save_dir,fileID))  
                

                with self.stdout_redirected():
                    ops.export_scene.obj(filepath=os.path.join(self.save_dir,fileID,fileID+'.obj'),
                                    use_materials=True)
                
                for img in bpy.data.images:
                    if img.name != 'Render Result' and img.name != 'Viewer Node':
                        img.save(filepath=os.path.join(self.save_dir,fileID,img.name+'.png'))  
                        bpy.data.images.remove(img)
                                
                print(Index+1,'/',num_names,'  name :',fileID)
                
                
            except KeyboardInterrupt:
                    with open('log/glb2mesh_log/current_id.txt', 'w') as file:
                        # 将整数转换为字符串并写入文件
                        file.write(str(Index + current_id) + '\n')
                    current_name = glb_names[Index + current_id].split('.')[0]
                    dir_tobe_deleted = os.path.join(self.save_dir, current_name)
                    if os.path.exists(dir_tobe_deleted):
                        shutil.rmtree(dir_tobe_deleted)
                    exit()
            except:
                # 打开文件以写入模式
                with open('log/glb2mesh_log/excepts.txt', 'a') as file:
                    # 将整数转换为字符串并写入文件
                    file.write(str(Index + current_id) + '\n')
                ops.object.mode_set(mode='OBJECT')
                ops.object.select_all(action='SELECT')
                ops.object.delete()
                continue
            ops.object.mode_set(mode='OBJECT')
            ops.object.select_all(action='SELECT')
            ops.object.delete()

