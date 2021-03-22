import bpy
from bpy.types import Operator, Panel
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper
from bpy_extras.io_utils import ExportHelper
import json

bl_info = {
    "name": "Import/Export",
    "location": "View3D > Sidebar > New Tab"
}

class MeshJsonData:
    def __init__(self, name, vertices, edges, faces):
        self.name = name
        self.vertices = vertices
        self.edges = edges
        self.faces = faces

class JsonImporter(Operator, ImportHelper):
    bl_idname = "object.import_json"
    bl_label = "Import JSON"

    filter_glob: StringProperty(
        default="*.json;",
        options={"HIDDEN"}
    )

    def execute(self, context):
        json_data = json.load(open(self.filepath))
        meshes = [MeshJsonData(**mesh) for mesh in json_data]
        for mesh in meshes:
            new_mesh = bpy.data.meshes.new(mesh.name)
            new_object = bpy.data.objects.new(new_mesh.name, new_mesh)
            context.collection.objects.link(new_object)
            verts = mesh.vertices
            edges = mesh.edges
            faces = mesh.faces
            new_mesh.from_pydata(verts, edges, faces)
        return {"FINISHED"}

class JsonExporter(Operator, ExportHelper):
    bl_idname = "object.export_json"
    bl_label = "Export JSON"

    filename_ext = ".json"

    def execute(self, context):
        meshes = []
        selected_objects = context.selected_objects
        for object in selected_objects:
            mesh = object.data
            vertices = []
            for vertex in mesh.vertices:
                global_co = object.matrix_world @ vertex.co
                vertices.append((global_co.x, global_co.y, global_co.z))
            edges = []
            for edge in mesh.edges:
                edge_vertices = edge.vertices
                edges.append((edge_vertices[0], edge_vertices[1]))
            faces = []
            for face in mesh.polygons:
                faces.append([vertex for vertex in face.vertices])
            meshes.append(MeshJsonData(object.name, vertices, edges, faces))
        json.dump([mesh.__dict__ for mesh in meshes], open(self.filepath, "w"), indent=4)
        return {"FINISHED"}

class JsonImportExportPanel(Panel):
    bl_label = "Import/Export"
    bl_region_type = "UI"
    bl_category = "JSON"
    bl_space_type = "VIEW_3D"

    def invoke(self, context, event):
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.operator("object.import_json", text="Import JSON")
        layout.operator("object.export_json", text="Export JSON")

classes = [
    JsonImporter,
    JsonExporter,
    JsonImportExportPanel
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
