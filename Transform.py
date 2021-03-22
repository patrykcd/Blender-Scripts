import bpy
from bpy.props import IntProperty, EnumProperty

class Transform(bpy.types.Operator):
    bl_idname = "object.transform"
    bl_label = "Transform"
    
    x : IntProperty(default=0) 
    y : IntProperty(default=0)
    z : IntProperty(default=0)
    
    def get_vec3(self):
        return [self.x, self.y, self.z]
    
    def move(self, objects):
        for object in objects:
            for i, val in enumerate(self.get_vec3()):
                object.location[i] += val

    def rotate(self, objects):
        import math
        for object in objects:
            for i, val in enumerate(self.get_vec3()):
                object.rotation_euler[i] += math.radians(val)                
    
    def scale(self, objects):
        for object in objects:
            for i, val in enumerate(self.get_vec3()):
                object.scale[i] += val
                
    action_dic = {
        "MOVE": move,
        "ROTATE": rotate,
        "SCALE": scale,
    }
    
    action_enum : EnumProperty(
            items = [
                ([*action_dic][0], "Move", ""),
                ([*action_dic][1], "Rotate", ""),
                ([*action_dic][2], "Scale", "")
            ]
    )
    
    def execute(self, context):
        self.action_dic[self.action_enum](self, bpy.context.selected_objects)
        return {"FINISHED"}

    def invoke(self, context, event):
        self.x = self.y = self.z = 0
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "action_enum", expand=True)
        col = layout.column() 
        row = col.row()   
        row.prop(self, "x", text="X")
        row.prop(self, "y", text="Y")
        row.prop(self, "z", text="Z")

classes = [
        Transform,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
