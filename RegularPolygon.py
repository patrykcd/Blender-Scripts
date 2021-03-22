import bpy
from bpy.props import IntProperty, FloatProperty

class ModalOperator(bpy.types.Operator):
    bl_idname = "mesh.regular_polygon_add"
    bl_label = "Add Regular Polygon"
    bl_options = {"REGISTER", "UNDO"}

    vertex_count: IntProperty(default=3, min=3)
    radius: IntProperty(default=1, min=1)
    height: IntProperty(default=1, min=1)
    x_location: FloatProperty(default=0)
    y_location: FloatProperty(default=0)
    z_location: FloatProperty(default=0)

    def execute(self, context):
        import math
        verts = []
        tau_len = 100000000
        tau_int = 628318530
        for z in range(0, self.height + 1, self.height):
            for i in range(0, tau_int, math.ceil(tau_int / self.vertex_count)):
                radians = i / tau_len
                x = math.cos(radians) * self.radius + self.x_location
                y = math.sin(radians) * self.radius + self.y_location
                verts.append((x, y, z + self.z_location))
        edges = []
        faces = [
            range(self.vertex_count - 1, -1, -1),
            range(self.vertex_count, self.vertex_count * 2)
        ]

        for i in range(0, self.vertex_count):
            a = (i % self.vertex_count)
            b = (i + 1) % self.vertex_count
            face = (a + self.vertex_count, a, b, b + self.vertex_count)
            faces.append(face)

        name = "RegularPolygon"
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
        mesh = obj.data
        mesh.clear_geometry()
        mesh.from_pydata(verts, edges, faces)
        return {'FINISHED'}

    def modal(self, context, event):
        print("modal")
        self.execute(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        print("invoke")
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.prop(self, "vertex_count", text="Number of vertices")
        layout.prop(self, "radius", text="Radius")
        layout.prop(self, "height", text="Height")
        layout.prop(self, "x_location", text="Location X")
        layout.prop(self, "y_location", text="Y")
        layout.prop(self, "z_location", text="Z")

def register():
    bpy.utils.register_class(ModalOperator)

def unregister():
    bpy.utils.unregister_class(ModalOperator)

if __name__ == "__main__":
    register()
