from numpy.linalg import norm
import bpy
import bpy.ops as ops
import sys
from math import pi,sin,cos,tan
import os
import io
from contextlib import contextmanager
#from multiprocessing import Pool
#from functools import partial

class Render():
    def __init__(self, model_dir, save_dir, angle_list=[(pi/4.,pi/6),
                        (3*pi/4.,pi/6),
                        (5*pi/4.,pi/6),
                        (7*pi/4.,pi/6),
                        (pi/4.,0),
                        (3*pi/4.,0),
                        (5*pi/4.,0),
                        (7*pi/4.,0),], viewAngle=0.691112):
        self.model_dir = model_dir
        self.save_dir = save_dir
        self.angle_list = angle_list
        self.viewAngle = viewAngle # uesd in method 'auto_dist'
        self.stdout = io.StringIO()
        self.Objects = bpy.data.objects
        self.Scene = bpy.data.scenes["Scene"]
        bpy.data.worlds['World'].node_tree.nodes['Background'].inputs[0].default_value=[1,1,1,1]
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
        
        deleteListObjects = ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR', 'POINTCLOUD', 'VOLUME', 'GPENCIL',
                            'ARMATURE', 'LATTICE', 'EMPTY', 'LIGHT', 'LIGHT_PROBE', 'CAMERA', 'SPEAKER']
        """
        deleteListObjects = ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR', 'POINTCLOUD', 'VOLUME', 'GPENCIL',
                            'ARMATURE', 'LATTICE', 'EMPTY',  'CAMERA', 'SPEAKER']
        
        # Select all objects in the scene to be deleted:

        for o in self.Objects:
            if o.type in deleteListObjects:
                o.select_set(True)
        bpy.ops.object.delete() # Deletes all selected objects in the scene

    def auto_dist(self, target):
        xs=[ p[0] for p in target.bound_box]
        ys=[ p[1] for p in target.bound_box]
        zs=[ p[2] for p in target.bound_box]
        longest=norm([max(xs)-min(xs),max(ys)-min(ys),max(zs)-min(zs)])
        dist=longest/2/tan(self.viewAngle/2)/cos(self.viewAngle/2)
        return dist
    
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
        camera.location=[dist*cos(theta)*cos(phi),dist*cos(theta)*sin(phi),dist*sin(theta)]
        camera.rotation_euler=[0.5*pi-theta,0,0.5*pi+phi]

    def presetCompositor(self, ):

        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        # clear default nodes
        for node in tree.nodes:
            tree.nodes.remove(node)

        # create input view node
        input_node = tree.nodes.new(type='CompositorNodeRLayers')
        input_node.location = 0,0

        # create output node
        #convert_space=tree.nodes.new('CompositorNodeConvertColorSpace')
        #convert_space.from_color_space='sRGB'
        #convert_space.to_color_space='Linear'
        #convert_space.name='convert_space'
        
        #multi_ply3=tree.nodes.new('CompositorNodeMath')
        #multi_ply3.operation='MULTIPLY'
        #multi_ply3.name='multiply3'
        
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
                countMesh+=1
                o.select_set(True)
                bpy.context.view_layer.objects.active=o
        if countMesh>1:
            ops.object.join()
        ops.object.origin_set(type='GEOMETRY_ORIGIN')
        ops.object.select_all(action='DESELECT')
        
        target=None
        for o in self.Objects:
            if o.type=='MESH':
                target=o
                break
        ops.object.camera_add(location=[self.auto_dist(target),0,0],rotation=[0.5*pi,0,0.5*pi])
        
        
        
        #settings
        ##Format
        self.Scene.render.resolution_x = 256            
        self.Scene.render.resolution_y = 256
        self.Scene.camera = self.Objects['Camera'] 
        self.Scene.render.image_settings.file_format = 'PNG'
        self.Scene.render.image_settings.compression = 0
        self.Scene.render.image_settings.color_management='OVERRIDE'
        
        
        ##render format
        self.Scene.render.engine = self.Engines[1]#Use EEVEE
        
        
        

        
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
                (phi,theta+pi/18),
                (phi,theta-pi/18),
                (phi+pi/18,theta),
                (phi-pi/18,theta),
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
        glb_names=[name for name in os.listdir(self.model_dir) if name.endswith('.glb')]
        if len(glb_names)==0:
            raise Exception('No \'.glb\' file is found')
        if not multiprocess:
            num_names=len(glb_names)
            for Index in range(num_names):
                self.list_render(anglelist=self.angle_list,
                        filepath=os.path.join(self.model_dir,glb_names[Index]),
                        savedir=self.save_dir)
                print(Index+1,'/',num_names,'  name :',glb_names[Index])
        # if multiprocess:
        #     glb_paths=[os.path.join(model_dir,name) for name in glb_names]
        #     with Pool(1) as p:
        #         data_infos=p.map(partial(
        #                             partial(list_render,angle_list)
        #                             ,save_dir
        #                             )
        #                         ,glb_paths
        #                         )
        #         p.close()
        #         p.join()
                

    


if __name__=='__main__':
    render = Render(model_dir='/home/wangyi/ROOT/study_stuffs/Machine_Learning_Project/modules/Data-Collection-3D-model/glb_data', 
                  save_dir='/home/wangyi/ROOT/study_stuffs/Machine_Learning_Project/modules/Data-Collection-3D-model/rendered_data', 
                  angle_list=[(pi/4.,pi/6),
                        (3*pi/4.,pi/6),
                        (5*pi/4.,pi/6),
                        (7*pi/4.,pi/6),
                        (pi/4.,0),
                        (3*pi/4.,0),
                        (5*pi/4.,0),
                        (7*pi/4.,0),], viewAngle=0.691112)
    render.renderAll()
