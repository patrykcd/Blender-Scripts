import bpy
from bpy.types import Operator, Panel
from bpy.props import IntProperty
import json
import requests
from pathlib import Path
from datetime import datetime

URL = "https://localhost:5001/api/Projects"

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

class WebApiImporter(Operator):
    bl_idname = "object.import_web_api"
    bl_label = "Import WebApi"

    def execute(self, context):
        headers = {
            "accept": "application/json"
        }
        id = context.scene.get_request_id
        result = requests.get(url=f"{URL}/{id}", headers=headers, verify=False)
        self.report({"INFO"}, f"Get request status: {result.reason}")
        json_data = json.loads(result.json()["meshes"])
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

class WebApiExporter(Operator):
    bl_idname = "object.export_web_api"
    bl_label = "Export WebApi"

    def execute(self, context):
        blender_file_path = Path(bpy.data.filepath)
        blender_file_name = blender_file_path.stem
        stats = blender_file_path.stat()
        date_format = "%d/%m/%Y %H:%M"
        creation_date = datetime.fromtimestamp(stats.st_birthtime).strftime(date_format)
        modification_date = datetime.fromtimestamp(stats.st_mtime).strftime(date_format)
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
        project = {
            "name": blender_file_name,
            "creationDate": creation_date,
            "modificationDate": modification_date,
            "meshes": json.dumps([mesh.__dict__ for mesh in meshes])
        }
        headers = {
            "Content-Type": "application/json",
            "accept": "application/json"
        }
        result = requests.post(url=URL, data=json.dumps(project), headers=headers, verify=False)
        new_id = json.loads(result.text)['id']
        self.report({"INFO"}, f"Post request status: {result.reason}, Assigned id: {new_id}")
        bpy.types.Scene.get_request_id = IntProperty(min=1, max=new_id)
        context.scene.get_request_id = new_id
        return {"FINISHED"}

class WebApiImportExportPanel(Panel):
    bl_label = "Import/Export"
    bl_region_type = "UI"
    bl_category = "WebApi"
    bl_space_type = "VIEW_3D"

    def invoke(self, context, event):
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        row = layout.row() 
        row.prop(context.scene, "get_request_id", text="ID")
        row.operator("object.import_web_api", text="Import")
        layout.operator("object.export_web_api", text="Export")

classes = [
    WebApiImporter,
    WebApiExporter,
    WebApiImportExportPanel
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.get_request_id = IntProperty(default=1, min=1)

def unregister():
    del py.types.Scene.get_request_id
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
