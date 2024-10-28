from numpy.linalg import norm
import bpy
import bpy.ops as ops
import sys
from math import pi,sin,cos,tan,sqrt
import os
import io
from contextlib import contextmanager


class Render():
    def __init__(self, model_dir, save_dir, angle_list=[(-pi/3,pi/3),
                        (pi/6,pi/3),
                        (2*pi/3,pi/3),
                        (7*pi/6,pi/3),
                        (-pi/6,pi/2),
                        (pi/3,pi/2),
                        (5*pi/6,pi/2),
                        (4*pi/3,pi/2),], gpu_in_use=False, cam_lens=35,cam_sensor_width=32):
        self.gpu_in_use = gpu_in_use
        self.model_dir = model_dir
        self.save_dir = save_dir
        self.angle_list = angle_list
        self.cam_lens = cam_lens # uesd in method 'auto_dist'
        self.cam_sensor_width = cam_sensor_width
        self.stdout = io.StringIO()
        self.Objects = bpy.data.objects
        self.Scene = bpy.data.scenes["Scene"]
        bpy.data.worlds['World'].node_tree.nodes['Background'].inputs[0].default_value=[0.7,0.7,0.7,1]
        self.Engines=['BLENDER_WORKBENCH' ,'BLENDER_EEVEE', 'CYCLES']
        self.Scene.view_layers["ViewLayer"].use_pass_z = True
        self.presetCompositor()

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
            sys.stdout = os.fdopen(fd, 'w') # Python writes to fd

        with os.fdopen(os.dup(fd), 'w') as old_stdout:
            with open(to, 'w') as file:
                _redirect_stdout(to=file)
            try:
                yield # allow code to be run with the redirected stdout
            finally:
                _redirect_stdout(to=old_stdout) # restore stdout.
                                                # buffering and flags such as
                                                # CLOEXEC may be different

    def deleteAllObjects(self, ):
        """
        Deletes all objects in the current scene
        
        
        """
        deleteListObjects = ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR', 'POINTCLOUD', 'VOLUME', 'GPENCIL',
                            'ARMATURE', 'LATTICE', 'EMPTY', 'LIGHT', 'LIGHT_PROBE', 'CAMERA', 'SPEAKER']
        # deleteListObjects = ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR', 'POINTCLOUD', 'VOLUME', 'GPENCIL',
        #                     'ARMATURE', 'LATTICE', 'EMPTY',  'CAMERA', 'SPEAKER']
        # 
        # Select all objects in the scene to be deleted:

        bpy.ops.object.mode_set(mode="OBJECT")
        
        for o in self.Objects:
            if o.type in deleteListObjects:
                o.select_set(True)

        bpy.ops.object.delete() # Deletes all selected objects in the scene

    
    
    def setCameraAngle(self, target=None, phi=0, theta=0):
        '''
        angle: radius
        '''
        camera=None
        
        for o in bpy.data.objects:
            if target is None and o.type=='MESH':
                target=o
            elif o.type=='CAMERA':
                camera=o
        if target is None:
            raise ValueError('No mesh')
        if camera is None:
            raise ValueError('No camera')
        dist=norm([camera.location,[0,0,0]])
        camera.location=[dist*sin(theta)*cos(phi),dist*sin(theta)*sin(phi),dist*cos(theta)]
        camera.rotation_euler=[theta,0,0.5*pi+phi]

    def presetCompositor(self, ):

        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        # clear default nodes
        for node in tree.nodes:
            tree.nodes.remove(node)

        # create input view node
        input_node = tree.nodes.new(type='CompositorNodeRLayers')
        input_node.location = 0,0


        
        comp_node = tree.nodes.new('CompositorNodeComposite') 
        comp_node.name=  'CompositorNodeComposite'
        comp_node.location = 400,0
        
        # create middle node 
        normalize=tree.nodes.new('CompositorNodeNormalize')
        map_range=tree.nodes.new('CompositorNodeMapRange')
        map_range.use_clamp=True
        map_range.inputs[1].default_value=0
        map_range.inputs[2].default_value=2000
        map_range.inputs[3].default_value=0
        map_range.inputs[4].default_value=2000
        
        less_than1=tree.nodes.new('CompositorNodeMath')
        less_than1.operation='LESS_THAN'
        less_than1.name='less_than1'
        less_than1.inputs[1].default_value=0.99999
        
        less_than2=tree.nodes.new('CompositorNodeMath')
        less_than2.operation='LESS_THAN'
        less_than2.name='less_than2'
        less_than2.inputs[1].default_value=2000
        
        multi_ply1=tree.nodes.new('CompositorNodeMath')
        multi_ply1.operation='MULTIPLY'
        multi_ply1.name='multiply1'
        multi_ply2=tree.nodes.new('CompositorNodeMath')
        multi_ply2.operation='MULTIPLY'
        multi_ply2.name='multiply2'
        
        divide=tree.nodes.new('CompositorNodeMath')
        divide.operation='DIVIDE'
        divide.inputs[1].default_value=65.535
        
        

        # inner link nodes
        
        
        links = tree.links
        
        links.new(input_node.outputs[2],normalize.inputs[0])
        links.new(normalize.outputs[0], less_than1.inputs[0])
        links.new(normalize.outputs[0], multi_ply1.inputs[0])
        links.new(less_than1.outputs[0], multi_ply1.inputs[1])
        
        
        links.new(input_node.outputs[2],map_range.inputs[0])
        links.new(map_range.outputs[0], less_than2.inputs[0])
        links.new(map_range.outputs[0], divide.inputs[0])
        links.new(divide.outputs[0], multi_ply2.inputs[0])
        links.new(less_than2.outputs[0], multi_ply2.inputs[1])
        
        
        #links.new(convert_space.outputs[0],multi_ply3.inputs[0])
        #links.new(multi_ply3.outputs[0],comp_node.inputs[0])
        
        #links.new(convert_space.outputs[0],comp_node.inputs[0])
        
        
        bpy.context.scene.use_nodes = False
        
    def change_compositor(self, mode:int=0):
        
        '''
        0:render
        1:normalized depth 
        2:millimeter depth
        '''
        if mode!=0 and mode!=1 and mode!=2:
            '''No Change'''
            return
        if mode==0:
            bpy.context.scene.use_nodes = False
            self.Scene.render.image_settings.color_mode='RGBA'
            self.Scene.render.image_settings.color_depth='8'
            
            self.Scene.render.image_settings.view_settings.view_transform='Standard'
            
        elif mode==1:
            bpy.context.scene.use_nodes = True
            nodes = bpy.context.scene.node_tree.nodes
            links = bpy.context.scene.node_tree.links
            
            links.new(nodes['multiply1'].outputs[0],nodes['CompositorNodeComposite'].inputs[0])
            #links.new(nodes['less_than1'].outputs[0],nodes['multiply3'].inputs[1])
            
            self.Scene.render.image_settings.color_mode='BW'
            self.Scene.render.image_settings.color_depth='16'
            
            
            
            self.Scene.render.image_settings.view_settings.view_transform='Raw'
            
        
        elif mode==2:
            bpy.context.scene.use_nodes = True
            nodes = bpy.context.scene.node_tree.nodes
            links = bpy.context.scene.node_tree.links
            links.new(nodes['multiply2'].outputs[0],nodes['CompositorNodeComposite'].inputs[0])
            #links.new(nodes['less_than2'].outputs[0],nodes['multiply3'].inputs[1])
            
            self.Scene.render.image_settings.color_mode='BW'
            self.Scene.render.image_settings.color_depth='16'
            
            
            
            self.Scene.render.image_settings.view_settings.view_transform='Raw'

    def list_render(self, anglelist:list[tuple[float]], savedir:str, filepath:str):
        self.deleteAllObjects()
        
        with self.stdout_redirected():
            ops.import_scene.gltf(filepath=filepath)

            
        fileID=os.path.split(filepath)[1].split('.')[0]
        ops.object.select_all(action='DESELECT')
        
        countMesh=0
        for o in self.Objects:
            if o.type=='MESH':
                
                o.select_set(True)
                if countMesh==0:
                    bpy.context.view_layer.objects.active=o
                countMesh+=1
        # print(countMesh)
        if countMesh>1:
            ops.object.join()
            
        target=None
        
        for o in self.Objects:
            if o.type=='MESH':
                bpy.context.view_layer.objects.active=o
                if o.data.shape_keys is not None:
                    blocks = o.data.shape_keys.key_blocks
                    for ind in reversed(range(len(blocks))):
                        o.active_shape_key_index = ind
                        ops.object.shape_key_remove()
                target=o
                break
            
        if target is None:
            raise Exception("No target")
            
        ##隐藏动画信息
        ops.object.select_all(action='DESELECT')
        for o in self.Objects:
            if o.type=='ARMATURE' :
                o.hide_render=True
            elif o.name=='Camera':
                o.select_set(True)
        bpy.ops.object.delete()
        
        for modifier in target.modifiers:
            if modifier.type=="ARMATURE":
                bpy.context.view_layer.objects.active=target
                ops.object.modifier_apply(modifier=modifier.name)
                break
        ops.object.select_all(action='DESELECT')
        
        target.select_set(True)
        ops.object.origin_set(type='ORIGIN_CURSOR')
        ops.object.origin_set(type='GEOMETRY_ORIGIN',center='BOUNDS')
        
        
        
        ops.object.select_all(action='SELECT')
        ops.object.transform_apply(location=False,rotation=False,scale=True)
        ops.object.select_all(action='DESELECT')
        
        ##摄像机设置
        cam_dist=1.2#摄像机距离
        ops.object.camera_add(location=[cam_dist,0,0],rotation=[0.5*pi,0,0.5*pi])
        
        
        bpy.data.cameras['Camera'].lens=self.cam_lens
        bpy.data.cameras['Camera'].sensor_width=self.cam_sensor_width
        
        ops.object.select_all(action='DESELECT')
        self.Scene.camera = self.Objects['Camera'] 
        
        
        ##缩放模型
        
        ViewAngle=bpy.data.cameras['Camera'].angle
        
        diag=norm([target.dimensions.x,target.dimensions.y,target.dimensions.z])
        longest=max([target.dimensions.x,target.dimensions.y,target.dimensions.z])
        
        Side_length=cam_dist*tan(ViewAngle/2)*2/1.73205080756887
        
        target.scale[0],target.scale[1],target.scale[2]=Side_length/longest,Side_length/longest,Side_length/longest
        ops.object.transform_apply(location=True,rotation=True,scale=True)
        
        
        ops.object.select_all(action='DESELECT')

        
        
        anglelen=len(anglelist)
        for i in range(anglelen):
            
            
            phi=anglelist[i][0]
            theta=anglelist[i][1]
            self.setCameraAngle(target,phi,theta)
            prename='view_'+str(i)
            
            #Render main view
            self.Scene.render.film_transparent = True
            self.change_compositor(0)
            self.Scene.render.filepath=os.path.join(savedir,fileID,prename+'.png')
            with self.stdout_redirected():
                bpy.ops.render.render( write_still=True )
            
            
            
            self.change_compositor(1)
            self.Scene.render.filepath=os.path.join(savedir,fileID,prename+'_depth.png')
            
            with self.stdout_redirected():
                bpy.ops.render.render( write_still=True )
            
            

            self.change_compositor(2)
            self.Scene.render.filepath=os.path.join(savedir,fileID,prename+'_depth_mm.png')
            with self.stdout_redirected():
                bpy.ops.render.render( write_still=True )
            
            
            
            sublist=[
                (phi,theta-pi/18),
                (phi,theta+pi/18),
                (phi-pi/18,theta),
                (phi+pi/18,theta),
            ]
            for j in range(4):
                Phi=sublist[j][0]
                Theta=sublist[j][1]
                self.setCameraAngle(target,Phi,Theta)
                midname='_'+str(j)+'_10'
                
                self.change_compositor(0)
                self.Scene.render.film_transparent = False
                self.Scene.render.filepath=os.path.join(savedir,fileID,prename+midname+'.png')
                with self.stdout_redirected():
                    bpy.ops.render.render( write_still=True )
                
                self.Scene.render.film_transparent = True
                self.Scene.render.filepath=os.path.join(savedir,fileID,prename+midname+'_gt.png')
                with self.stdout_redirected():
                    bpy.ops.render.render( write_still=True )

                self.change_compositor(2)
                self.Scene.render.film_transparent = True
                self.Scene.render.filepath=os.path.join(savedir,fileID,prename+midname+'_gt_depth_mm.png')
                with self.stdout_redirected():
                    bpy.ops.render.render( write_still=True )
                
    def renderAll(self, multiprocess=False):
        
        #settings
        self.Scene.render.resolution_x = 256            
        self.Scene.render.resolution_y = 256
        
        self.Scene.render.image_settings.file_format = 'PNG'
        self.Scene.render.image_settings.compression = 15
        self.Scene.render.image_settings.color_management='OVERRIDE'
        
        
        ##渲染引擎
        self.Scene.render.engine = self.Engines[1]#实时渲染引擎


        
        # self.Scene.render.engine = self.Engines[2]#光线追踪引擎

        if self.gpu_in_use:
            self.Scene.cycles.device = 'GPU'
            self.Scene.cycles.samples = 512# 降低采样数可提升性能，但不要低于128
            bpy.context.preferences.addons[
            "cycles"
            ].preferences.compute_device_type = "CUDA" # or "OPENCL"
        
        
        if not os.path.exists('log/render_log/current_id.txt'):
            current_id = 0
        else:
            # 打开文件以读取模式
            with open('log/render_log/current_id.txt', 'r') as file:
                # 读取文件内容并转换为整数
                current_id = int(file.read())

        glb_names=[name for name in os.listdir(self.model_dir) if name.endswith('.glb')]
        print(len(glb_names) - current_id,'models found totally.')
        if len(glb_names) - current_id==0:
            raise Exception('No \'.glb\' file is found')
        if not multiprocess:
            num_names=len(glb_names) - current_id
            for Index in range(num_names - current_id):
                try:
                    self.list_render(anglelist=self.angle_list,
                            filepath=os.path.join(self.model_dir,glb_names[Index + current_id]),
                            savedir=self.save_dir)
                    print(Index+1,'/',num_names,'  name :',glb_names[Index + current_id])
                except KeyboardInterrupt:
                    with open('log/render_log/current_id.txt', 'w') as file:
                        # 将整数转换为字符串并写入文件
                        file.write(str(Index + current_id) + '\n')
                    current_name = glb_names[Index + current_id].split('.')[0]
                    dir_tobe_deleted = os.path.join(self.save_dir, current_name)
                    if os.path.exists(dir_tobe_deleted):
                        import shutil
                        shutil.rmtree(dir_tobe_deleted)
                    exit()
                except:
                    # 打开文件以写入模式
                    with open('log/render_log/excepts.txt', 'a') as file:
                        # 将整数转换为字符串并写入文件
                        file.write(str(Index + current_id) + '\n')
                    continue
                
                
                
##394行可以更换渲染模式，若一种过慢就换

# name: view_0 distance= 1.2000000307119145       theta= 60.00000281832396        phi 300.00000141476715
# name: view_1 distance= 1.200000056521486        theta= 60.00000352980198        phi 30.000004260679024
# name: view_2 distance= 1.2000000943093188       theta= 60.00000457147794        phi 119.99999528267938
# name: view_3 distance= 1.200000068499754        theta= 60.00000386000017        phi 209.99999243676734
# name: view_4 distance= 1.2000000692034751       theta= 90.00000250447802        phi 330.00000387939923
# name: view_5 distance= 1.2000000255698469       theta= 90.00000250447812        phi 59.99999610422294
# name: view_6 distance= 1.2000000394011574       theta= 90.00000250447809        phi 150.00000634403145
# name: view_7 distance= 1.2000001149768345       theta= 90.00000250447793        phi 239.99998871032727