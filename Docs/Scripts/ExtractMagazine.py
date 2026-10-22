# Makes SM_<Gun>_Magazine, a static mesh of just the triangles skinned to a weapon's "Magazine" bone, for the
# magazine that drops out with physics on reload (UOther5WeaponData::MagazineMesh). The mesh stays in the weapon
# mesh's component space (ref pose), so the game places it with the bone's current transform. Rerunnable; needs the
# GeometryScripting plugin, which the project doesn't enable, so run it as a commandlet:
#   UnrealEditor-Cmd.exe Other5.uproject -run=pythonscript -script="<this file>" -EnablePlugins=GeometryScripting
import unreal

GUNS = ["Pistol"]
BONE = "Magazine"

for gun in GUNS:
    src = unreal.load_asset("/Other5Combat/Weapons/%s/Mesh/SK_%s" % (gun, gun))
    dest_path = "/Other5Combat/Weapons/%s/Mesh/SM_%s_Magazine" % (gun, gun)

    mesh = unreal.DynamicMesh()
    options = unreal.GeometryScriptCopyMeshFromAssetOptions()
    lod = unreal.GeometryScriptMeshReadLOD()
    mesh, outcome = unreal.GeometryScript_AssetUtils.copy_mesh_from_skeletal_mesh(src, mesh, options, lod)

    _, found, bone_index = unreal.GeometryScript_BoneWeights.get_bone_index(mesh, BONE)
    if not found:
        raise RuntimeError("ExtractMagazine: no bone %s in %s" % (BONE, src.get_name()))

    profile = unreal.GeometryScriptBoneWeightProfile()
    keep_vertex = {}
    vertex_ids = unreal.GeometryScript_MeshQueries.get_all_vertex_i_ds(mesh)[1]
    for vid in unreal.GeometryScript_List.convert_index_list_to_array(vertex_ids):
        _, weight, valid = unreal.GeometryScript_BoneWeights.get_largest_vertex_bone_weight(mesh, vid, profile)
        keep_vertex[vid] = valid and weight.bone_index == bone_index

    tri_list = unreal.GeometryScript_MeshQueries.get_all_triangle_i_ds(mesh)[1]
    drop = []
    for tid in unreal.GeometryScript_List.convert_index_list_to_array(tri_list):
        tri = unreal.GeometryScript_MeshQueries.get_triangle_indices(mesh, tid)[0]
        if not (keep_vertex.get(tri.x) and keep_vertex.get(tri.y) and keep_vertex.get(tri.z)):
            drop.append(tid)
    drop_list = unreal.GeometryScript_List.convert_array_to_index_list(drop, unreal.GeometryScriptIndexType.TRIANGLE)
    unreal.GeometryScript_MeshEdits.delete_triangles_from_mesh(mesh, drop_list)
    remaining = unreal.GeometryScript_MeshQueries.get_num_triangle_i_ds(mesh)
    if remaining == 0:
        raise RuntimeError("ExtractMagazine: nothing skinned to %s in %s" % (BONE, src.get_name()))

    if unreal.EditorAssetLibrary.does_asset_exist(dest_path):
        target = unreal.load_asset(dest_path)
        write = unreal.GeometryScriptCopyMeshToAssetOptions()
        write.set_editor_property("enable_recompute_normals", False)
        write.set_editor_property("enable_recompute_tangents", False)
        unreal.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(mesh, target, write, unreal.GeometryScriptMeshWriteLOD())
    else:
        create = unreal.GeometryScriptCreateNewStaticMeshAssetOptions()
        create.set_editor_property("enable_recompute_normals", False)
        create.set_editor_property("enable_recompute_tangents", False)
        create.set_editor_property("enable_nanite", False)
        target = unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(mesh, dest_path, create)[0]
    target.set_material(0, src.materials[0].material_interface)
    # One box around it to land and tumble on (editor subsystems, and so EditorStaticMeshLibrary, don't run in a
    # commandlet).
    collision = unreal.GeometryScriptCollisionFromMeshOptions()
    collision.set_editor_property("method", unreal.GeometryScriptCollisionGenerationMethod.ORIENTED_BOXES)
    collision.set_editor_property("max_convex_hulls_per_mesh", 1)
    unreal.GeometryScript_Collision.set_static_mesh_collision_from_mesh(mesh, target, collision)
    unreal.EditorAssetLibrary.save_loaded_asset(target, False)
    unreal.log_warning("ExtractMagazine: %s, %d triangles (bone %d), body %s, bounds %s" % (
        dest_path, remaining, bone_index, target.get_editor_property("body_setup"), target.get_bounds().box_extent))
