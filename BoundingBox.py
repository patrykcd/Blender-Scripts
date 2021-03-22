import bpy

class BoundingBox(bpy.types.Operator):
    bl_idname = "object.bounding_box"
    bl_label = "Bounding Box"
    
    def invoke(self, context, event):
        vertices = []
        selected_objects = bpy.context.selected_objects

        for object in selected_objects:
            for vertex in object.data.vertices: 
                vertices.append(object.matrix_world @ vertex.co)

        vertices_x = [vertex.x for vertex in vertices]
        max_x = max(vertices_x)
        min_x = min(vertices_x)

        vertices_y = [vertex.y for vertex in vertices]
        max_y = max(vertices_y)
        min_y = min(vertices_y)

        vertices_z = [vertex.z for vertex in vertices]
        max_z = max(vertices_z)
        min_z = min(vertices_z)

        verts = [
                    (min_x, max_y, max_z),
                    (min_x, min_y, max_z),
                    (max_x, min_y, max_z),
                    (max_x, max_y, max_z),
                    (min_x, max_y, min_z),
                    (min_x, min_y, min_z),
                    (max_x, min_y, min_z),
                    (max_x, max_y, min_z)
                ]
        edges = []
        faces = [
                    (0, 1, 2, 3),
                    (3, 2, 6, 7),
                    (7, 6, 5, 4),
                    (4, 5, 1, 0),
                    (0, 3, 7, 4),
                    (5, 6, 2, 1)
                ]    
                
        name = "Bounding Box"
        get_names = lambda x: [item.name for item in x]
        if name in get_names(bpy.data.objects):
            obj = bpy.data.objects[name]
        else:
            if name in get_names(bpy.data.meshes):
                mesh = bpy.data.meshes[name]
            else:
                mesh = bpy.data.meshes.new(name)
            obj = bpy.data.objects.new(name, mesh)
            bpy.context.collection.objects.link(obj) 
        obj.hide_select = True  
        mesh  = obj.data
        mesh.clear_geometry()
        mesh.from_pydata(verts, edges, faces)
        
        return {"FINISHED"}

classes = [
        BoundingBox,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
